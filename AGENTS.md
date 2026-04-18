# Agent Execution Guide: CryptoPrism Engagement Engine

This guide instructions AI agents on how to execute the automated engagement loops using standard CLI commands.

## Prerequisites
- **Python Path**: Always run from the project root.
- **Environment**: Ensure `.env` contains `APIFY_TOKEN`, `TELEGRAM_API_ID`, `TELEGRAM_API_HASH`, and `REDDIT_USERNAME/PASSWORD`.
- **Telegram Session**: The first live run requires a one-time terminal login to create `cpio_user_session.session`.

---

## 1. Reddit Engagement Loop
Scrapes subreddits, evaluates matches, and generates/posts replies.

**Dry Run (Logging only):**
```bash
python -m src.reddit_loop
```

**Live Posting:**
```bash
python -m src.reddit_loop --post
```

---

## 2. Telegram Engagement Loop
Monitors Telegram channels or searches keywords and replies. 
**Note**: This loop prioritizes the high-speed **User API (Telethon)** and falls back to Apify if needed.

**Dry Run (Monitoring only):**
```bash
python -m src.telegram_loop --channels "CryptoPrism.io"
```

**Live Replying:**
```bash
python -m src.telegram_loop --channels "CryptoPrism.io" --reply
```

**Arguments:**
- `--channels "Name"`: Target specific channels by their **Display Name/Title**. Supports multiple names separated by space.
- `--limit [INT]`: (Alias for `--max-messages`) The number of historical messages to scan per keyword.
- `--reply`: Enables live replying via your own Telegram account.

---

## 3. Custom Sample Posting (One-offs)
Use these for direct announcements or operational tests.

**Post to Reddit Subreddit:**
```bash
$env:PYTHONPATH = "."; python scratch/live_post_cryptoprismio.py
```

**Post to Telegram Channel/Group Topic:**
```bash
$env:PYTHONPATH = "."; python scratch/telegram_sample_post.py "Channel Display Name" --topic "TopicName"
```

---

## 4. LinkedIn Engagement Loop
Performs standard 3-legged OAuth authentication using the official LinkedIn API for text posting.

**Setup Requirements:**
1. **Developer App**: Create an app on the [LinkedIn Developer Portal](https://www.linkedin.com/developers/).
2. **Redirect URI**: Add `http://localhost:8080/callback` to your app's "Authorized Redirect URIs".
3. **Permissions**: Ensure your app has `w_member_social`, `openid`, and `profile` scopes enabled.
4. **Environment**: Set `LINKEDIN_CLIENT_ID` and `LINKEDIN_CLIENT_SECRET` in your `.env`.

**Authenticate (One-time):**
Opens a browser for you to log in. Saves a token to `.linkedin_token.json`.
```bash
python -m src.linkedin_loop --auth
```

**Live Posting:**
```bash
python -m src.linkedin_loop --post "Your engaging LinkedIn post text here"
```

---

## Error Handling
- **403 Forbidden (Reddit)**: Update `src/safety/reddit_cookies.json`.
- **database is locked (Telegram)**: The engine now shares the client session between scraper and publisher to prevent this.
- **ModuleNotFoundError**: Ensure `PYTHONPATH="."` is set or run using `python -m src.filename`.
