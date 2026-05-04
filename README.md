# 🤖 usedebikes.ie Search Checker — Tutorial

This guide will help you set up the bot from scratch and show you how to change the search when you want to look for something different. No coding experience needed!

---

## 📋 What you'll need

- A free [GitHub](https://github.com) account
- A free [cron-job.org](https://cron-job.org) account (this is what reliably triggers the bot every 15 minutes)
- A phone with [Telegram](https://telegram.org) installed (it's a free messaging app)

---

## 🚀 Part 1: Setting it up for the first time

### Step 1 — Create your Telegram bot

Telegram lets you create simple bots for free with no account beyond your normal Telegram login. Here's how:

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

This tells the bot which conversation to send messages to (yours).

1. In Telegram, search for the bot you just created by its username (e.g. `@myebikes_bot`) and tap **Start**
2. Send it any message — just type `hi` and send it
3. Open this URL in your browser, replacing `YOUR_BOT_TOKEN` with the token you copied:
   `https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates`
4. You'll see some text on screen. Look for a number next to `"id":` inside the `"chat"` section. It'll look something like `"chat":{"id":987654321`
5. **That number is your Chat ID — copy it**

---

### Step 3 — Put the code on GitHub

1. Go to [github.com](https://github.com) and log in, or create a free account
2. Click the **+** button in the top-right corner and click **New repository**
3. Give it a name like `ebikes-bot`
4. Set it to **Private** so only you can see it
5. Click **Create repository**
6. Click **uploading an existing file** (or "Add file > Upload files")
7. Upload all the files from this folder:
   - `checker.py`
   - `seen_ids.json`
   - The file called `usedebikes_checker.yml` needs to go inside a specific folder in your repo. When uploading, GitHub lets you type a path into the filename box — name the file `.github/workflows/usedebikes_checker.yml` and GitHub will create the folders automatically

---

### Step 4 — Add your secrets to GitHub

GitHub has a secure vault for sensitive info like your bot token. The bot reads from this vault so your credentials are never visible in the code.

1. In your GitHub repo, click **Settings** (the tab at the top)
2. In the left menu, click **Secrets and variables**, then click **Actions**
3. Click **New repository secret** and add each of the following two secrets:

| Secret Name | What to put in it |
|---|---|
| `TELEGRAM_BOT_TOKEN` | The bot token from Step 1 |
| `TELEGRAM_CHAT_ID` | The chat ID number from Step 2 |

Make sure the secret names are spelled exactly as shown above — they are case-sensitive.

---

### Step 5 — Turn on GitHub Actions

1. In your repo, click the **Actions** tab at the top
2. If GitHub shows a message asking you to enable Actions, click the green button to enable them

---

### Step 6 — Create a GitHub Personal Access Token

This is what cron-job.org will use to trigger your workflow. It's like a special key that only has permission to run workflows — nothing else.

1. Go to github.com and click your profile picture in the top-right corner, then click **Settings**
2. Scroll all the way down the left menu and click **Developer settings**
3. Click **Personal access tokens** > **Tokens (classic)**
4. Click **Generate new token (classic)**
5. Give it a name like `cron-job trigger`
6. Set the expiry to whatever you like (No expiration means you never have to redo this)
7. Tick the **workflow** checkbox
8. Click **Generate token** and copy it — **you won't be able to see it again after leaving the page**

---

### Step 7 — Set up cron-job.org

This is the service that reliably pings your bot every 15 minutes. GitHub's own built-in scheduler is unreliable and can skip hours at a time, so we use this instead.

1. Go to [cron-job.org](https://cron-job.org) and create a free account
2. Click **Create cronjob**
3. Give it a title like `usedebikes checker`
4. Set the URL to the following, replacing `YOUR_GITHUB_USERNAME` and `YOUR_REPO_NAME` with your own:
   `https://api.github.com/repos/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME/actions/workflows/usedebikes_checker.yml/dispatches`
5. Set the schedule to **every 15 minutes**
6. Expand the **Advanced** section and add the following under **Request headers**:
   - Header: `Authorization` — Value: `Bearer YOUR_PERSONAL_ACCESS_TOKEN` (paste the token from Step 6)
   - Header: `Accept` — Value: `application/vnd.github+json`
7. Under **Request body**, set the type to **JSON** and paste in exactly: `{"ref":"main"}`
8. Click **Save**

The bot will now run every 15 minutes (plus a small random delay each time so it doesn't run like clockwork).

**Want to test it right now?**
1. Go to your GitHub repo and click the **Actions** tab
2. Click **usedebikes Checker** in the left list
3. Click **Run workflow** > **Run workflow**
4. After 30–60 seconds, click the run to see the output and confirm it worked

---

## ✏️ Part 2: Changing the search later

This is what you'll do when you want to search for something different.

### How to change the search URL

1. Go to [usedebikes.ie](https://www.usedebikes.ie) and do your search, applying all the filters you want (type, price, brand, etc.)
2. Copy the full URL from your browser's address bar
3. Go to your GitHub repo and click on the file **`checker.py`**
4. Click the **pencil icon** ✏️ in the top-right corner of the file to edit it
5. Find this line near the top:

```
VINTED_SEARCH_URL = "https://..."
```

6. Replace everything between the quote marks `"..."` with your new URL
7. Scroll down and click **Commit changes**, then click **Commit changes** again in the popup

Done! The bot will use the new search from its next run.

---

### How to change the keywords

The bot has two keyword lists near the top of `checker.py`. A listing only triggers an alert if it passes **both** checks.

**MUST_CONTAIN** — the title must include **all** of these words:
```python
MUST_CONTAIN = ["bosch", "250w"]
```

**MUST_CONTAIN_ONE_OF** — the title must include **at least one** of these words:
```python
MUST_CONTAIN_ONE_OF = ["hardtail", "full suspension", "gravel"]
```

So with the settings above, a listing like "Bosch 250w Full Suspension eBike" would match, but "Shimano 250w Hardtail" would not (missing "bosch").

To edit them:
1. Open **`checker.py`** in GitHub and click the pencil ✏️ to edit it
2. Change the words inside the square brackets to whatever you want
3. Each word goes inside `"quote marks"` and is separated by a comma
4. Keywords are **not** case-sensitive — `"Bosch"` will also match "bosch" or "BOSCH"
5. If you want to skip one of the checks entirely, set it to empty brackets: `[]`

**Examples:**

Alert only when the title contains "trek" and one of "emtb" or "electric":
```python
MUST_CONTAIN = ["trek"]
MUST_CONTAIN_ONE_OF = ["emtb", "electric"]
```

Alert for everything in the search with no keyword filter at all:
```python
MUST_CONTAIN = []
MUST_CONTAIN_ONE_OF = []
```

6. Click **Commit changes** when done

---

## ⏸️ How to pause and re-enable the bot

To pause the bot, log into [cron-job.org](https://cron-job.org), find your cronjob, and toggle it off. To re-enable it, toggle it back on. That's it — no need to touch any files in GitHub.

The manual **Run workflow** button in GitHub Actions will still work even when the cronjob is paused, so you can always trigger a one-off check whenever you like.

---

## 🗑️ How to reset the bot

The bot remembers which listings it has already told you about in a file called `seen_ids.json`. If you want it to start fresh — for example after changing your search — do this:

1. Click on **`seen_ids.json`** in your repo
2. Click the pencil ✏️ to edit it
3. Delete everything and replace it with just: `[]`
4. Click **Commit changes**

The next time the bot runs it will treat all listings as new and message you about any matches.

---

## ❓ Troubleshooting

**The bot isn't running every 15 minutes**
- Log into cron-job.org and check your cronjob is enabled and not showing errors
- Check that the URL, headers, and body in cron-job.org are entered exactly as shown in Step 7
- Make sure the personal access token hasn't expired

**I see "Telegram credentials not set. Skipping notification."**
- Your GitHub secrets are either missing or named incorrectly
- Go to Settings > Secrets and variables > Actions and check that both secrets exist and are named exactly `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`

**I'm not getting any Telegram messages**
- Make sure you sent your bot a message in Telegram first (Step 2) — it can't message you if you've never started a conversation with it
- Go to **Actions** in GitHub and click the latest run — look for any red errors
- Double-check your Chat ID is just the number, with no extra spaces

**The bot ran but found nothing**
- Your search might genuinely have no results right now — that's fine, it'll check again in 15 minutes
- Your keywords might be filtering everything out — try setting both lists to `[]` temporarily and run it again to confirm listings are being found

---

*That's everything! Happy hunting 🚴*
