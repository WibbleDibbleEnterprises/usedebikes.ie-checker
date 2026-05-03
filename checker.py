import requests
import json
import os

# ============================================================
#  SETTINGS — Edit these to change what the bot looks for
# ============================================================

# Paste your full Vinted search URL here
VINTED_SEARCH_URL = "https://www.vinted.ie/catalog?search_text=Nike%20pegasus%20gore%20tex&price_from=0.0&price_to=100.0&currency=EUR&size_ids[]=790&brand_ids[]=53&order=newest_first"

# MUST_CONTAIN — the listing title must include ALL of these words.
# Leave empty [] to skip this check.
MUST_CONTAIN = ["pegasus", "5"]

# MUST_CONTAIN_ONE_OF — the listing title must include AT LEAST ONE of these words.
# Leave empty [] to skip this check.
MUST_CONTAIN_ONE_OF = ["gore-tex", "goretex", "gtx"]

# ============================================================
#  DO NOT EDIT BELOW THIS LINE (unless you know what you're doing!)
# ============================================================

SEEN_IDS_FILE = "seen_ids.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-IE,en;q=0.9",
    "Referer": "https://www.vinted.ie/",
}


def build_api_url(catalog_url: str) -> str:
    """Convert a Vinted catalog URL into the internal API URL."""
    from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

    parsed = urlparse(catalog_url)
    params = parse_qs(parsed.query, keep_blank_values=True)

    params.pop("search_id", None)

    flat_params = {}
    for key, val in params.items():
        if len(val) == 1:
            flat_params[key] = val[0]
        else:
            flat_params[key] = val

    flat_params["per_page"] = "96"

    api_url = urlunparse((
        parsed.scheme,
        parsed.netloc,
        "/api/v2/catalog/items",
        "",
        urlencode(flat_params, doseq=True),
        ""
    ))
    return api_url


def fetch_listings(api_url: str) -> list:
    """Fetch listings from Vinted's API."""
    try:
        session = requests.Session()
        session.get("https://www.vinted.ie", headers=HEADERS, timeout=15)

        response = session.get(api_url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        data = response.json()
        return data.get("items", [])
    except Exception as e:
        print(f"Error fetching listings: {e}")
        return []


def load_seen_ids() -> set:
    """Load the set of listing IDs we've already sent alerts for."""
    if os.path.exists(SEEN_IDS_FILE):
        with open(SEEN_IDS_FILE, "r") as f:
            return set(json.load(f))
    return set()


def save_seen_ids(seen_ids: set):
    """Save the updated set of seen listing IDs."""
    with open(SEEN_IDS_FILE, "w") as f:
        json.dump(list(seen_ids), f)


def matches_keywords(title: str) -> bool:
    """Check if a listing title passes both keyword filters."""
    title_lower = title.lower()

    # Check that every word in MUST_CONTAIN appears in the title
    if MUST_CONTAIN:
        if not all(word.lower() in title_lower for word in MUST_CONTAIN):
            return False

    # Check that at least one word in MUST_CONTAIN_ONE_OF appears in the title
    if MUST_CONTAIN_ONE_OF:
        if not any(word.lower() in title_lower for word in MUST_CONTAIN_ONE_OF):
            return False

    return True


def send_telegram(new_listings: list):
    """Send a Telegram message for each new matching listing."""
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")

    if not bot_token or not chat_id:
        print("Telegram credentials not set. Skipping notification.")
        return

    api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    for item in new_listings:
        title = item.get("title", "No title")
        price = item.get("price", {})
        price_str = f"€{price.get('amount', '?')}" if isinstance(price, dict) else "?"
        url = f"https://www.vinted.ie/items/{item.get('id', '')}"

        message = (
            f"New Vinted listing found!\n\n"
            f"{title}\n"
            f"{price_str}\n\n"
            f"{url}"
        )

        try:
            response = requests.post(api_url, data={
                "chat_id": chat_id,
                "text": message,
            }, timeout=10)
            response.raise_for_status()
            print(f"Telegram message sent for: {title}")
        except Exception as e:
            print(f"Failed to send Telegram message: {e}")


def main():
    print("Vinted bot starting...")

    api_url = build_api_url(VINTED_SEARCH_URL)
    print(f"Fetching: {api_url}")

    listings = fetch_listings(api_url)
    print(f"Found {len(listings)} listings in search results.")

    seen_ids = load_seen_ids()
    new_matches = []

    for item in listings:
        item_id = str(item.get("id", ""))
        title = item.get("title", "")

        if item_id in seen_ids:
            continue

        seen_ids.add(item_id)

        if matches_keywords(title):
            print(f"  New match: {title}")
            new_matches.append(item)
        else:
            print(f"  Skipped (no keyword match): {title}")

    if new_matches:
        send_telegram(new_matches)
    else:
        print("No new matches found this run.")

    save_seen_ids(seen_ids)
    print("Done!")


if __name__ == "__main__":
    main()
