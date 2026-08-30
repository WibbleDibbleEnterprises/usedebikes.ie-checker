import requests
import json
import os
from datetime import datetime, timezone

# ============================================================
#  All searches are configured in searches.json — edit that
#  file to add, remove, or change searches. Do not edit here.
# ============================================================

SEARCHES_FILE = "searches.json"
STATE_FILE = "state.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-IE,en;q=0.9",
    "Referer": "https://www.vinted.ie/",
}


def load_searches() -> list:
    with open(SEARCHES_FILE, "r") as f:
        return json.load(f)


def load_state() -> dict:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {}


def save_state(state: dict):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def is_due(search_name: str, interval_minutes: int, state: dict) -> bool:
    """Check whether enough time has passed to run this search again."""
    if search_name not in state:
        return True
    last_checked_str = state[search_name].get("last_checked")
    if not last_checked_str:
        return True
    last_checked = datetime.fromisoformat(last_checked_str)
    now = datetime.now(timezone.utc)
    minutes_since = (now - last_checked).total_seconds() / 60
    return minutes_since >= interval_minutes


def build_api_url(catalog_url: str) -> str:
    from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

    parsed = urlparse(catalog_url)
    params = parse_qs(parsed.query, keep_blank_values=True)
    params.pop("search_id", None)

    flat_params = {}
    for key, val in params.items():
        flat_params[key] = val[0] if len(val) == 1 else val

    flat_params["per_page"] = "96"

    return urlunparse((
        parsed.scheme,
        parsed.netloc,
        "/api/v2/catalog/items",
        "",
        urlencode(flat_params, doseq=True),
        ""
    ))


def fetch_listings(api_url: str) -> list:
    try:
        session = requests.Session()
        session.get("https://www.vinted.ie", headers=HEADERS, timeout=15)
        response = session.get(api_url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        return response.json().get("items", [])
    except Exception as e:
        print(f"  Error fetching listings: {e}")
        return []


def matches_keywords(title: str, must_contain: list, must_contain_one_of: list, must_not_contain: list) -> bool:
    title_lower = title.lower()
    if must_contain:
        if not all(w.lower() in title_lower for w in must_contain):
            return False
    if must_contain_one_of:
        if not any(w.lower() in title_lower for w in must_contain_one_of):
            return False
    if must_not_contain:
        if any(w.lower() in title_lower for w in must_not_contain):
            return False
    return True


def send_telegram(search_name: str, new_listings: list):
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")

    if not bot_token or not chat_id:
        print("  Telegram credentials not set. Skipping notification.")
        return

    api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    for item in new_listings:
        title = item.get("title", "No title")
        price = item.get("price", {})
        price_str = f"€{price.get('amount', '?')}" if isinstance(price, dict) else "?"
        url = f"https://www.vinted.ie/items/{item.get('id', '')}"

        message = (
            f"[{search_name}]\n\n"
            f"{title}\n"
            f"{price_str}\n\n"
            f"{url}"
        )

        try:
            response = requests.post(api_url, data={"chat_id": chat_id, "text": message}, timeout=10)
            response.raise_for_status()
            print(f"  Telegram sent: {title}")
        except Exception as e:
            print(f"  Failed to send Telegram message: {e}")


def main():
    searches = load_searches()
    state = load_state()
    now_str = datetime.now(timezone.utc).isoformat()

    print(f"Loaded {len(searches)} search(es).\n")

    for search in searches:
        name = search["name"]
        url = search["url"]
        must_contain = search.get("must_contain", [])
        must_contain_one_of = search.get("must_contain_one_of", [])
        must_not_contain = search.get("must_not_contain", [])
        interval = search.get("interval_minutes", 15)

        print(f"--- {name} (every {interval} min) ---")

        if not is_due(name, interval, state):
            print(f"  Not due yet, skipping.\n")
            continue

        api_url = build_api_url(url)
        listings = fetch_listings(api_url)
        print(f"  Found {len(listings)} listings in search results.")

        search_state = state.get(name, {"seen_ids": [], "last_checked": None})
        seen_ids = set(search_state.get("seen_ids", []))
        new_matches = []

        for item in listings:
            item_id = str(item.get("id", ""))
            title = item.get("title", "")

            if item_id in seen_ids:
                continue

            seen_ids.add(item_id)

            if matches_keywords(title, must_contain, must_contain_one_of, must_not_contain):
                print(f"  New match: {title}")
                new_matches.append(item)
            else:
                print(f"  Skipped (no keyword match): {title}")

        if new_matches:
            send_telegram(name, new_matches)
        else:
            print("  No new matches found.")

        state[name] = {
            "seen_ids": list(seen_ids),
            "last_checked": now_str
        }
        print()

    save_state(state)
    print("All done!")


if __name__ == "__main__":
    main()
