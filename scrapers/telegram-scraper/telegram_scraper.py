import os
import json
import yaml
from telethon.sync import TelegramClient
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument


def load_config(path='config.yml'):
    """Load configuration from a YAML file."""
    with open(path, 'r') as file:
        config = yaml.safe_load(file)
    return config

if __name__ == "__main__":
    # --- Telegram API Credentials ---
    config = load_config()

    # --- Telegram API credentials ---
    api_id = config['telegram']['api_id']
    api_hash = config['telegram']['api_hash']
    session_name = config['telegram']['session_name']
    
    # --- Target group/channel and scrapig options ---
    target_group = config['scraping']['target_group']
    limit = config['scraping'].get('limit', 1)  # Default limit to 1 if not specified
    download_images = config['scraping'].get('download_images', True)
    download_videos = config['scraping'].get('download_videos', True)

    # --- Start session ---
    with TelegramClient(session_name, api_id, api_hash) as client:
        entity = client.get_entity(target_group)
        group_id = entity.id
        group_name = entity.username or entity.title or "unknown"

        # Sanitize folder name
        folder_name = f"{group_id}_{group_name}".replace(" ", "_")
        os.makedirs(folder_name, exist_ok=True)

        # Media folders
        images_folder = os.path.join(folder_name, 'images')
        videos_folder = os.path.join(folder_name, 'videos')
        if download_images:
            os.makedirs(images_folder, exist_ok=True)
        if download_videos:
            os.makedirs(videos_folder, exist_ok=True)

        # Structured data
        data = {str(group_id): {}}

        for message in client.iter_messages(entity, limit=limit):
            if not message.message:
                continue

            msg_id = message.id
            content = message.message
            has_image = isinstance(message.media, MessageMediaPhoto)
            has_video = (
                isinstance(message.media, MessageMediaDocument)
                and message.media.document.mime_type.startswith("video/")
            )

            # Save metadata
            data[str(group_id)][str(msg_id)] = {
                'content': content,
                'image': has_image,
                'video': has_video
            }

            # Media download logic
            if has_image and download_images:
                filename_base = os.path.join(images_folder, f"{group_id}_{msg_id}")
                client.download_media(message, file=filename_base)

            if has_video and download_videos:
                filename_base = os.path.join(videos_folder, f"{group_id}_{msg_id}")
                client.download_media(message, file=filename_base)

        # Save metadata to JSON
        output_json = os.path.join(folder_name, f"{folder_name}.json")
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        print(f"Scraping complete.\n- Metadata: {output_json}")
        if download_images:
            print(f"- Images saved to: {images_folder}")
        if download_videos:
            print(f"- Videos saved to: {videos_folder}")
