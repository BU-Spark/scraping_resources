import asyncio
import os
from aiohttp import ClientSession
from config import *

async def download_image(url, id):
    if os.path.isfile(os.path.join(DATA_DIR, id + '.jpg')):
        return
    async with ClientSession() as session:
        async with session.get(url) as response:
            response = await response.read()
            with open(os.path.join(DATA_DIR, id + '.jpg'), 'wb') as f:
                f.write(response)

def download_images(download_data):
    loop = asyncio.get_event_loop()

    tasks = []
    for dl in download_data:
        task = asyncio.ensure_future(download_image(dl[0], dl[1]))
        tasks.append(task)

    loop.run_until_complete(asyncio.wait(tasks))