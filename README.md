# 🤖 usedebikes.ie Search Checker — Tutorial

This guide will help you set up the bot from scratch and show you how to change the search when you want to look for something different. No coding experience needed!

---

## 📋 What you'll need

- A free [GitHub](https://github.com) account
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
   - The file called `vinted_checker.yml` needs to go inside a specific folder in your repo. When uploading, GitHub lets you type a path into the filename box — name the file `.github/workflows/vinted_checker.yml` and GitHub will create the folders automatically

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
3. That's it! The bot will now run automatically every 30 minutes and send you a Telegram message when it finds something new.

**Want to test it right now?**
1. Click **Actions** > click **Used eBikes Listing Checker** in the left list
2. Click **Run workflow** > **Run workflow**
3. After 30–60 seconds, click the run to see the output and confirm it worked. If everything is set up correctly, you should get a Telegram message for any matching listings that currently exist.

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

If you want to temporarily stop the bot from running every 30 minutes, you can pause it without deleting anything.

1. In your GitHub repo, click on `.github/workflows/vinted_checker.yml`
2. Click the **pencil icon** ✏️ to edit it
3. Find this line:

```
    - cron: "0,30 * * * *"
```

4. Add a `#` to the very start of it so it looks like this:

```
    # - cron: "0,30 * * * *"
```

5. Click **Commit changes**

The bot will no longer run automatically. To re-enable it, just remove the `#` and commit again.

Note: even when paused this way, you can still trigger a manual run anytime by going to **Actions > Used eBikes Listing Checker > Run workflow**.

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

**I see "Telegram credentials not set. Skipping notification."**
- Your GitHub secrets are either missing or named incorrectly
- Go to Settings > Secrets and variables > Actions and check that both secrets exist and are named exactly `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`

**I'm not getting any Telegram messages**
- Make sure you sent your bot a message in Telegram first (Step 2) — it can't message you if you've never started a conversation with it
- Go to **Actions** in GitHub and click the latest run — look for any red errors
- Double-check your Chat ID is just the number, with no extra spaces

**The bot ran but found nothing**
- Your search might genuinely have no results right now — that's fine, it'll check again in 30 minutes
- Your keywords might be filtering everything out — try setting both lists to `[]` temporarily and run it again to confirm listings are being found

**GitHub Actions isn't running every 30 minutes**
- GitHub can occasionally delay scheduled runs slightly — this is normal
- If it's been more than an hour with no runs, go to Actions and trigger it manually to check for errors

---

*That's everything! Happy hunting 🚴*
