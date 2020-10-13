import os
import sys
import praw
from datetime import datetime
from config import *
from image_resolver import *
from task_downloader import *

if __name__ == '__main__':
    reddit = praw.Reddit(client_id=CLIENT_ID,
                         client_secret=CLIENT_SECRET,
                         password=PASSWORD,
                         user_agent=USER_AGENT,
                         username=USERNAME)

    last_upper = int((datetime.utcnow() - datetime(1970, 1, 1)).total_seconds())
    download_data = []

    # Checkpoint
    if os.path.isfile('checkpoint_cs.txt'):
        with open('checkpoint_cs.txt', 'r') as file:
            last_upper = int(file.read())
            print("Loaded Checkpoint,", last_upper)

    while True:
        print("Collecting")
        download_data = []

        upper = last_upper
        lower = upper - 86400
        query = 'timestamp:%d..%d' % (lower, upper)

        generator = reddit.subreddit(SUBREDDIT).search(query, sort='new', limit=100, syntax='cloudsearch')

        for submission in generator:
            link = parse_url(submission.url)
            id_ = submission.fullname
            if link is not None:
                download_data.append((link, id_))

        print("Downloading", len(download_data))
        download_images(download_data)

        print('Done')

        with open('checkpoint_cs.txt', 'w') as file:
            file.write(str(last_upper))

        print('Checkpointing')
        print('')

        last_upper = lower

