## Quickstart

Fast subreddit image scraper. Has no real limits.

Place `config.py` as

```python
SUBREDDIT = ''

USERNAME = ''
PASSWORD = ''
CLIENT_SECRET = ''
CLIENT_ID = ''
PLATFORM = 'python'
APP_ID = ''
VERSION = 'v0.0.1'
LIMIT = 200
DATA_DIR = './data'

USER_AGENT = '{platform}:{app_id}:{version} (by /u/{username})'.format(platform=PLATFORM,
                                                                       app_id=APP_ID,
                                                                       version=VERSION,
                                                                       username=USERNAME)
```

Use `python3 cloudsearch.py` to start. 

## Dependencies

Depends on `praw` and `aiohttp`