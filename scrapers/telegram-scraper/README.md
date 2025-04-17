# Telegram Scraper

This Python script uses [Telethon](https://github.com/LonamiWebs/Telethon) to scrape messages, images, and videos from a public or private Telegram channel or group. It supports filtering by date range, forward/backward traversal, media downloads, and exports structured JSON data for analysis.

---

## 📦 Features

- Download messages from a specific Telegram channel or group
- Optionally download images and/or videos
- Filter messages by start and end date
- Store grouped metadata (message ID, grouped ID, timestamp, content)
- Output three structured files:
  - Message data
  - Channel-wide metadata
  - Metadata for the current scraping run

---

## 🛠 Requirements

- Python 3.8+
- [Telethon](https://docs.telethon.dev/en/stable/)
- PyYAML

Install dependencies with:

```bash
pip install -r requirements.txt
```

---

## 📄 Configuration

Create a file named `config.yml` in the same directory as the script with the following structure:

```yaml
telegram:
  api_id: YOUR_API_ID
  api_hash: YOUR_API_HASH
  session_name: my_session

scraping:
  target_group: https://t.me/your_channel_or_group
  limit: 1000
  download_images: true
  download_videos: true
  start_date: 2024-01-01
  end_date: 2024-12-31
  scrape_forward: false
  offset_id: null
  offset_date: null
```

> ⚠️ Do **not** commit your real `config.yml`. Instead, commit the `config_template.yml` to share structure.

---

## 🚀 Usage

```bash
python telegram_scraper.py
```

After running, the script will generate a folder like:

```
<channel_id>_<channel_name>/
├── images/ (if enabled)
├── videos/ (if enabled)
├── <channel_id>_<channel_name>.json            # message data
├── <channel_id>_<channel_name>_run_metadata.json
├── <channel_id>_<channel_name>_channel_metadata.json
```

---

## 🧠 How It Works

- `start_date` and `end_date` are optional filters
- `reverse = false`: Scrape backward from latest messages (default)
- `reverse = true`: Scrape forward from `offset_date` or the oldest message
- Messages are stored in JSON grouped by their `grouped_id` when available

---

## 🧼 Example Output

```json
{
  "1441684517": {
    "13954242885943317": {
      "7189": {
        "grouped_id": 13954242885943317,
        "datetime": "2025-04-10T10:19:20+00:00",
        "content": "...",
        "media_saved": ["image"]
      },
      "7190": {
        "grouped_id": 13954242885943317,
        "datetime": "...",
        "content": "",
        "media_saved": ["image"]
      }
    },
    "7196": {
      "7196": {
        "grouped_id": null,
        "datetime": "...",
        "content": "...",
        "media_saved": ["video"]
      }
    }
  }
}
```

---

## ✅ Tips

- Use `offset_date` only when `scrape_forward: true`
- You can test scraping metadata without downloading media by setting:
  ```yaml
  download_images: false
  download_videos: false
  ```

---

## 🛡 Security

- Your `api_id` and `api_hash` are **sensitive**
- Use `.gitignore` to prevent `config.yml` from being committed:

```gitignore
scrapers/telegram-scraper/config.yml
scrapers/telegram-scraper/*.session
```
