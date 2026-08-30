# 🤖 usedebikes.ie Search Checker — Tutorial

This guide will help you set up the bot from scratch and show you how to manage your searches. No coding experience needed!

---

## 📋 What you'll need

- A free [GitHub](https://github.com) account
- A free [cron-job.org](https://cron-job.org) account (this is what reliably triggers the bot)
- A phone with [Telegram](https://telegram.org) installed (it's a free messaging app)

---

## 🚀 Part 1: Setting it up for the first time

### Step 1 — Create your Telegram bot

1. Open Telegram and search for **@BotFather** (it has a blue tick next to it)
2. Tap on it and tap **Start**
3. Type `/newbot` and send it
4. BotFather will ask you for a name — type anything you like, e.g. `My eBikes Bot`
5. It will then ask for a username — this has to end in `bot`, e.g. `myebikes_bot`
6. BotFather will reply with a long token that looks something like:
   `123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ`
   **Copy this and keep it safe — this is your Bot Token**

---

### Step 2 — Get your Chat ID

1. In Telegram, search for the bot you just created by its username and tap **Start**
2. Send it any message — just type `hi` and send it
3. Open this URL in your browser, replacing `YOUR_BOT_TOKEN` with the token you copied:
   `https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates`
4. Look for a number next to `"id":` inside the `"chat"` section, e.g. `"chat":{"id":987654321`
5. **That number is your Chat ID — copy it**

---

### Step 3 — Put the code on GitHub

1. Go to [github.com](https://github.com) and log in, or create a free account
2. Click the **+** button in the top-right corner and click **New repository**
3. Give it a name, set it to **Private**, and click **Create repository**
4. Upload all the files:
   - `checker.py`
   - `searches.json`
   - `state.json`
   - For `vinted_checker.yml`, type the path `.github/workflows/vinted_checker.yml` in the filename box when uploading — GitHub will create the folders automatically

---

### Step 4 — Add your secrets to GitHub

1. In your repo, click **Settings** > **Secrets and variables** > **Actions**
2. Click **New repository secret** and add both of these:

| Secret Name | What to put in it |
|---|---|
| `TELEGRAM_BOT_TOKEN` | The bot token from Step 1 |
| `TELEGRAM_CHAT_ID` | The chat ID number from Step 2 |

---

### Step 5 — Turn on GitHub Actions

1. Click the **Actions** tab in your repo
2. If prompted, click the green button to enable Actions

---

### Step 6 — Create a GitHub Personal Access Token

1. On github.com, click your profile picture > **Settings**
2. Scroll down and click **Developer settings** > **Personal access tokens** > **Tokens (classic)**
3. Click **Generate new token (classic)**
4. Give it a name like `cron-job trigger`, set any expiry, tick the **workflow** checkbox
5. Click **Generate token** and copy it — **you won't see it again**

---

### Step 7 — Set up cron-job.org

1. Go to [cron-job.org](https://cron-job.org) and create a free account
2. Click **Create cronjob**
3. Set the URL to (replacing `YOUR_GITHUB_USERNAME` and `YOUR_REPO_NAME`):
   `https://api.github.com/repos/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME/actions/workflows/vinted_checker.yml/dispatches`
4. Set the request method to **POST**
5. Set the schedule to every **2 minutes**
6. Under **Advanced > Request headers**, add:
   - `Authorization` → `Bearer YOUR_PERSONAL_ACCESS_TOKEN`
   - `Accept` → `application/vnd.github+json`
7. Under **Request body**, set type to **JSON** and paste: `{"ref":"main"}`
8. Click **Save**

---

## ✏️ Part 2: Managing your searches

All your searches live in a single file called **`searches.json`**. This is the only file you need to edit when adding, changing, or removing a search.

### What searches.json looks like

```json
[
  {
    "name": "Nike Pegasus Gore-Tex",
    "url": "https://www.vinted.ie/catalog?search_text=...",
    "must_contain": ["pegasus", "5"],
    "must_contain_one_of": ["gore-tex", "goretex", "gtx"],
    "interval_minutes": 2
  },
  {
    "name": "Specialized eMTB",
    "url": "https://www.vinted.ie/catalog?search_text=...",
    "must_contain": ["specialized"],
    "must_contain_one_of": ["emtb", "electric", "ebike"],
    "interval_minutes": 30
  }
]
```

Each search has five fields:

| Field | What it does |
|---|---|
| `name` | A label for the search — this appears in your Telegram alerts |
| `url` | The full search URL copied from your browser |
| `must_contain` | The title must include **all** of these words |
| `must_contain_one_of` | The title must include **at least one** of these words |
| `interval_minutes` | How often to check this search (in minutes) |

For `must_contain` and `must_contain_one_of`: each word goes inside `"quote marks"` separated by commas. Set either to `[]` to skip that check entirely. Keywords are not case-sensitive.

---

### How to add a new search

1. Go to the site and set up your search with all the filters you want
2. Copy the full URL from your browser's address bar
3. Open **`searches.json`** in GitHub and click the pencil ✏️ to edit it
4. Copy one of the existing search blocks and paste it after the last one, making sure to add a comma after the previous block. Like this:

```json
[
  {
    "name": "First Search",
    ...
  },
  {
    "name": "Second Search",
    ...
  }
]
```

5. Fill in the new search's `name`, `url`, keywords, and `interval_minutes`
6. Click **Commit changes**

---

### How to remove a search

1. Open **`searches.json`** and click the pencil ✏️
2. Delete the entire block for that search (from the `{` to the closing `}`)
3. Make sure there's no trailing comma after the last remaining search
4. Click **Commit changes**

---

### How to reset a single search

The bot remembers seen listings in a file called `state.json`. To reset just one search (so it re-alerts you on existing listings):

1. Open **`state.json`** and click the pencil ✏️
2. Delete the entry for that search by name
3. Click **Commit changes**

To reset everything, just replace the entire contents of `state.json` with `{}`

---

## ⏸️ How to pause and re-enable the bot

Log into [cron-job.org](https://cron-job.org) and toggle your cronjob off to pause, on to resume. The manual **Run workflow** button in GitHub Actions still works while paused.

---

## ❓ Troubleshooting

**The bot isn't running regularly**
- Check cron-job.org for errors in the execution log
- Make sure the URL, headers, and body are entered exactly as shown in Step 7
- Check that your personal access token hasn't expired

**"Telegram credentials not set"**
- Check Settings > Secrets and variables > Actions — both secrets must exist and be named exactly `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`

**No Telegram messages arriving**
- Make sure you sent the bot a message in Telegram first — it can't message you otherwise
- Check the Actions log for errors
- Double-check your Chat ID has no extra spaces

**A search says "Not due yet" every run**
- The `interval_minutes` for that search is set higher than how often the bot is triggered — that's fine, it just skips that search until enough time has passed

**The bot ran but found nothing**
- The search might genuinely have no results right now
- Your keywords might be too strict — try setting both to `[]` temporarily and run again to confirm listings are being fetched

---

*That's everything! Happy hunting 🚴*
