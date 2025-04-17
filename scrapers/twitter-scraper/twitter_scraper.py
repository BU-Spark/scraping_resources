# twitter_scraper.py using Vercel-style token workaround + Selenium for tweet ID scraping
import os
import json
import yaml
import requests
from datetime import datetime, timezone
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import random

# ----------------------------
# Twitter Login with Selenium
# ----------------------------
def login_to_twitter(driver, username, password):
    driver.get("https://x.com/login")
    wait = WebDriverWait(driver, 15)

    user_input = wait.until(EC.presence_of_element_located((By.NAME, "text")))
    time.sleep(random.uniform(1.5, 5.5))
    user_input.send_keys(username)
    user_input.send_keys(Keys.RETURN)

    pwd_input = wait.until(EC.presence_of_element_located((By.NAME, "password")))
    time.sleep(random.uniform(1.5, 5.5))
    pwd_input.send_keys(password)
    pwd_input.send_keys(Keys.RETURN)

    wait.until(EC.invisibility_of_element((By.NAME, "password")))

# ----------------------------
# Configuration and Utilities
# ----------------------------
def load_config(path='config.yml'):
    with open(path, 'r') as file:
        return yaml.safe_load(file)

def parse_date(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d').replace(tzinfo=timezone.utc) if date_str else None

def base36(num):
    chars = '0123456789abcdefghijklmnopqrstuvwxyz'
    result = ''
    while num > 0:
        num, i = divmod(num, 36)
        result = chars[i] + result
    return result or '0'

def get_token(tweet_id: str) -> str:
    token = ((int(tweet_id) / 1e15) * 3.141592653589793)
    return base36(int(token * 1e6))

# ----------------------------
# Tweet Data Retrieval
# ----------------------------
def fetch_tweet_data(tweet_id):
    token = get_token(tweet_id)
    url = f"https://cdn.syndication.twimg.com/tweet-result?id={tweet_id}&token={token}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"[WARN] Failed to fetch tweet {tweet_id}: HTTP {response.status_code}")
        return None

def download_media(url, folder):
    parsed = urlparse(url)
    filename = os.path.basename(parsed.path)
    path = os.path.join(folder, filename)
    try:
        r = requests.get(url)
        if r.status_code == 200:
            with open(path, 'wb') as f:
                f.write(r.content)
            return filename
    except Exception as e:
        print(f"[ERROR] Downloading media failed: {e}")
    return None

# ----------------------------
# Tweet ID Scraper via Selenium
# ----------------------------
def get_tweet_ids_from_profile(username, limit=50, login_credentials=None):
    print(f"[INFO] Scraping tweet IDs from https://x.com/{username} ...")
    tweet_ids = set()
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(options=options)

    try:
        if login_credentials:
            login_to_twitter(driver, login_credentials['username'], login_credentials['password'])
            time.sleep(random.uniform(2, 4))

        url = f"https://x.com/{username}"
        driver.get(url)
        driver.save_screenshot("debug_screenshot.png")
        time.sleep(random.uniform(2, 4))

        last_height = driver.execute_script("return document.body.scrollHeight")
        while len(tweet_ids) < limit:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(2, 3))
            page_source = driver.page_source
            matches = re.findall(r'/status/(\d+)', page_source)
            tweet_ids.update(matches)
            if len(tweet_ids) >= limit:
                break
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
    finally:
        driver.quit()

    tweet_ids = list(tweet_ids)[:limit]
    print(f"[INFO] Collected tweet IDs: {tweet_ids}")
    return tweet_ids

# ----------------------------
# Main Scraping Logic
# ----------------------------
def scrape_tweets(config):
    tweet_ids = config['scraping'].get('tweet_ids')
    username = config['scraping'].get('username')
    limit = config['scraping'].get('limit', 100)
    login_credentials = config.get('auth')

    if username and not tweet_ids:
        tweet_ids = get_tweet_ids_from_profile(username, limit=limit, login_credentials=login_credentials)

    folder_name = username or "tweet_scrape"
    folder_name = folder_name.replace("@", "").strip().lower()
    os.makedirs(folder_name, exist_ok=True)

    images_folder = os.path.join(folder_name, 'images')
    videos_folder = os.path.join(folder_name, 'videos')
    os.makedirs(images_folder, exist_ok=True)
    os.makedirs(videos_folder, exist_ok=True)

    data = {"tweets": {}}
    tweet_count = 0
    image_count = 0
    video_count = 0

    for tweet_id in tweet_ids:
        tweet_data = fetch_tweet_data(tweet_id)
        if tweet_data is None:
            continue

        tweet_time = parse_date(tweet_data.get('created_at', '')[:10])
        tweet_text = tweet_data.get('text', '')
        has_image = False
        has_video = False

        media_entities = tweet_data.get('photos') or []
        for media in media_entities:
            media_url = media.get('url')
            if not media_url:
                continue
            filename = download_media(media_url, images_folder)
            if filename:
                has_image = True
                image_count += 1

        video_url = tweet_data.get('video_url')
        if video_url:
            filename = download_media(video_url, videos_folder)
            if filename:
                has_video = True
                video_count += 1

        data["tweets"][str(tweet_id)] = {
            "datetime": tweet_time.isoformat() if tweet_time else None,
            "content": tweet_text,
            "media_saved": {
                "image": has_image,
                "video": has_video
            }
        }

        tweet_count += 1

    message_json = os.path.join(folder_name, "tweets.json")
    with open(message_json, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    run_meta = {
        "tweet_count": tweet_count,
        "image_count": image_count,
        "video_count": video_count,
        "config_used": {
            "username": username,
            "tweet_ids": tweet_ids,
            "limit": limit
        }
    }

    run_meta_json = os.path.join(folder_name, "tweets_run_metadata.json")
    with open(run_meta_json, 'w', encoding='utf-8') as f:
        json.dump(run_meta, f, ensure_ascii=False, indent=4)

    print("\n✅ Tweet scrape complete.")
    print(f"- Tweets saved to: {message_json}")
    print(f"- Metadata saved to: {run_meta_json}")
    print(f"- Images saved to: {images_folder}")
    print(f"- Videos saved to: {videos_folder}")


if __name__ == '__main__':
    config = load_config()
    scrape_tweets(config)