import os
import sys
import praw
from config import *
from image_resolver import *
from task_downloader import *

if __name__ == '__main__':
    reddit = praw.Reddit(client_id=CLIENT_ID,
                         client_secret=CLIENT_SECRET,
                         password=PASSWORD,
                         user_agent=USER_AGENT,
                         username=USERNAME)

    last_id = ''
    download_data = []

    # Checkpoint
    if os.path.isfile('checkpoint.txt'):
        with open('checkpoint.txt', 'r') as file:
            last_id = file.read()
            print("Loaded Checkpoint,", last_id)

    while True:
        print("Collecting")
        download_data = []

        if last_id == '':
            generator = reddit.subreddit(SUBREDDIT).top('week', limit=LIMIT)
        else:
            generator = reddit.subreddit(SUBREDDIT).top('week', limit=LIMIT, params={'after': last_id})

        for submission in generator:
            link = parse_url(submission.url)
            last_id = submission.fullname
            if link is not None:
                download_data.append((link, last_id))

        print("Downloading", len(download_data))
        download_images(download_data)

        print('Done')

        with open('checkpoint.txt', 'w') as file:
            file.write(last_id)

        print('Checkpointing')
        print('')

