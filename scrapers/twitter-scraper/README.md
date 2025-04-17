# 🐦 Twitter Scraper (Vercel-style Token + Selenium)

This Python script scrapes tweet metadata and media (images, videos) from a public or authenticated Twitter/X profile using:

- 🧠 **Vercel-style token workaround** to access embedded tweet data 
- 🕵️ **Selenium** to scrape tweet IDs directly from a user's timeline

[Vercel-style workaround source](https://github.com/JustAnotherArchivist/snscrape/issues/996)

## 📦 Features

- Extracts tweet text, datetime, and media (images/videos)
- Saves media locally and metadata as structured JSON
- Supports headless login for scraping private/protected timelines
- Outputs organized into a per-user folder

## 📁 Output Structure

For a target user like `@BU_Tweets`, the script creates:

```
BU_Tweets/
├── tweets.json                 # Structured tweet data
├── tweets_run_metadata.json   # Run summary and config
├── images/                    # Downloaded images
└── videos/                    # Downloaded videos
```

## 🔧 Configuration

Create a `config.yml` file in the project directory:

```yaml
auth:
  username: your_x_username
  password: your_x_password

scraping:
  username: BU_Tweets            # Twitter/X username (no @ needed)
  limit: 30                     # Number of tweets to scrape
  tweet_ids: null               # Optional: provide list to skip Selenium
```

## 🚀 Usage

Install dependencies:

```bash
pip install -r requirements.txt
```

Download and install [ChromeDriver](https://sites.google.com/chromium.org/driver/) compatible with your Chrome version.

Then run the script:

```bash
python twitter_scraper.py
```

## 💡 Notes

- Media presence is recorded as:

```json
"media_saved": {
  "image": true,
  "video": false
}
```

- Random delays are added to mimic human scrolling and reduce rate-limiting risk.
- Works best for accounts that don't require heavy login-based protection.

## ⚠️ Disclaimer

This project is for educational purposes. Use responsibly and comply with Twitter/X's Terms of Service.

---

Created with 💻 by [Ta-Chi Lin]
