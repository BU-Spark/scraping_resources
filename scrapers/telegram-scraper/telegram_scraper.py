import os
import json
import yaml
from datetime import datetime, timezone
from telethon.sync import TelegramClient
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument


def load_config(path='config.yml'):
    with open(path, 'r') as file:
        return yaml.safe_load(file)

def parse_date(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d').replace(tzinfo=timezone.utc) if date_str else None

def generate_fallback_photo_id(message):
    photo = getattr(message.media, 'photo', None)
    if photo and hasattr(photo, 'id'):
        return str(photo.id)
    else:
        return str(int(message.date.timestamp()))


if __name__ == "__main__":
    config = load_config()

    # Telegram API credentials
    api_id = config['telegram']['api_id']
    api_hash = config['telegram']['api_hash']
    session_name = config['telegram']['session_name']

    # Scraping parameters
    target_group = config['scraping']['target_group']
    limit = config['scraping'].get('limit', 1000)
    download_images = config['scraping'].get('download_images', False)
    download_videos = config['scraping'].get('download_videos', False)
    start_date = parse_date(config['scraping'].get('start_date'))
    end_date = parse_date(config['scraping'].get('end_date'))
    reverse = config['scraping'].get('scrape_forward')
    offset_id = config['scraping'].get('offset_id')
    offset_date = parse_date(config['scraping'].get('offset_date')) or start_date

    if start_date and end_date and start_date > end_date:
        raise ValueError("start_date cannot be after end_date.")

    with TelegramClient(session_name, api_id, api_hash) as client:
        entity = client.get_entity(target_group)
        group_id = entity.id
        group_name = entity.username or entity.title or "unknown"
        group_url = f"https://t.me/{entity.username}" if entity.username else None

        folder_name = f"{group_id}_{group_name}".replace(" ", "_")
        os.makedirs(folder_name, exist_ok=True)

        images_folder = os.path.join(folder_name, 'images')
        videos_folder = os.path.join(folder_name, 'videos')
        if download_images:
            os.makedirs(images_folder, exist_ok=True)
        if download_videos:
            os.makedirs(videos_folder, exist_ok=True)

        data = {str(group_id): {}}
        first_msg_time = None
        last_msg_time = None
        image_count = 0
        video_count = 0
        message_count = 0

        iter_args = {"entity": entity, "limit": limit, "reverse": reverse}
        if offset_id is not None:
            iter_args["offset_id"] = offset_id
        elif offset_date is not None:
            # Use offset_date only if reverse is True (forward)
            if reverse:
                iter_args["offset_date"] = offset_date


        for message in client.iter_messages(**iter_args):
            if not message:
                continue
            if start_date and message.date < start_date:
                continue
            if end_date and message.date > end_date:
                continue

            msg_id = message.id
            grouped_id = getattr(message, 'grouped_id', None)
            msg_time = message.date
            content = message.message
            media_saved = []

            if isinstance(message.media, MessageMediaPhoto) and download_images:
                media_id = generate_fallback_photo_id(message)
                filename = os.path.join(images_folder, f"{group_id}_{msg_id}_{media_id}_photo.jpg")
                result = client.download_media(message, file=filename)
                if result:
                    image_count += 1
                    media_saved.append("image")

            elif isinstance(message.media, MessageMediaDocument) and message.media.document.mime_type.startswith("video/") and download_videos:
                media_id = str(getattr(message.media.document, 'id', int(msg_time.timestamp())))
                filename = os.path.join(videos_folder, f"{group_id}_{msg_id}_{media_id}_video.mp4")
                result = client.download_media(message, file=filename)
                if result:
                    video_count += 1
                    media_saved.append("video")

            if media_saved:
                message_count += 1
                first_msg_time = min(first_msg_time or msg_time, msg_time)
                last_msg_time = max(last_msg_time or msg_time, msg_time)

                data[str(group_id)][str(msg_id)] = {
                    "grouped_id": grouped_id,
                    "datetime": msg_time.isoformat(),
                    "content": content,
                    "media_saved": media_saved
                }

        first_msg = client.iter_messages(entity, reverse=True).__next__()
        last_msg = client.iter_messages(entity).__next__()
        total_msg_count = client.get_messages(entity, limit=0).total

        channel_metadata = {
            "channel_name": group_name,
            "channel_id": group_id,
            "channel_url": group_url,
            "total_message_count": total_msg_count,
            "first_message_id": first_msg.id,
            "first_message_datetime": first_msg.date.isoformat(),
            "last_message_id": last_msg.id,
            "last_message_datetime": last_msg.date.isoformat()
        }

        channel_meta_json = os.path.join(folder_name, f"{folder_name}_channel_metadata.json")
        with open(channel_meta_json, 'w', encoding='utf-8') as f:
            json.dump(channel_metadata, f, ensure_ascii=False, indent=4)

        message_json = os.path.join(folder_name, f"{folder_name}.json")
        with open(message_json, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        run_meta = {
            "channel_name": group_name,
            "channel_id": group_id,
            "channel_url": group_url,
            "first_message_datetime": first_msg_time.isoformat() if first_msg_time else None,
            "last_message_datetime": last_msg_time.isoformat() if last_msg_time else None,
            "message_count": message_count,
            "image_count": image_count,
            "video_count": video_count,
            "config_used": {
                "target_group": target_group,
                "limit": limit,
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None,
                "scrape_forward": reverse,
                "offset_id": offset_id,
                "offset_date": offset_date.isoformat() if offset_date else None,
                "download_images": download_images,
                "download_videos": download_videos
            }
        }

        run_meta_json = os.path.join(folder_name, f"{folder_name}_run_metadata.json")
        with open(run_meta_json, 'w', encoding='utf-8') as f:
            json.dump(run_meta, f, ensure_ascii=False, indent=4)

        print(f"\n✅ Scraping complete.")
        print(f"- Channel metadata saved to: {channel_meta_json}")
        print(f"- Messages saved to: {message_json}")
        print(f"- Metadata for the current run saved to: {run_meta_json}")
        if download_images:
            print(f"- Images saved in: {images_folder}")
        if download_videos:
            print(f"- Videos saved in: {videos_folder}")