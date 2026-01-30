import os
import re
from instagrapi import Client
from instagrapi.types import Media

def download_all_user_media():
    """
    Downloads all media (photos, videos, reels, albums) from a specified
    Instagram profile using the saved instagrapi session.
    """
    cl = Client()
    session_file = 'session.json'
    
    # --- Login ---
    try:
        cl.load_settings(session_file)
        cl.login_by_sessionid(cl.sessionid)
        print("Login successful.")
    except FileNotFoundError:
        print(f"Error: '{session_file}' not found. Please run a login script first.")
        return
    except Exception as e:
        print(f"An error occurred during login: {e}")
        return

    # --- Get Target User ---
    url = input("Enter the Instagram profile URL: ")
    username_match = re.search(r"(?:https://www.instagram.com/)?([^/]+)", url)
    if not username_match:
        print("Invalid URL format.")
        return
        
    target_username = username_match.group(1)
    print(f"Target user: {target_username}")

    try:
        user_id = cl.user_id_from_username(target_username)
        print(f"Found user ID: {user_id}")
    except Exception as e:
        print(f"Could not find user '{target_username}'. Error: {e}")
        return

    # --- Setup Download Folder ---
    download_folder = f"./{target_username}"
    os.makedirs(download_folder, exist_ok=True)
    print(f"Saving content to '{download_folder}'")

    # --- Fetch and Download ---
    try:
        medias = cl.user_medias(user_id)
        print(f"Found {len(medias)} media items for '{target_username}'.")

        for i, media in enumerate(medias):
            print(f"\n[{i+1}/{len(medias)}] Processing media {media.pk}...")
            
            try:
                if media.media_type == 1: # Photo
                    print("Type: Photo. Downloading...")
                    cl.photo_download(media.pk, folder=download_folder)
                elif media.media_type == 2 and media.product_type == "feed": # Video Post
                    print("Type: Video Post. Downloading...")
                    cl.video_download(media.pk, folder=download_folder)
                elif media.media_type == 2 and media.product_type == "clips": # Reel
                    print("Type: Reel. Downloading...")
                    cl.clip_download(media.pk, folder=download_folder)
                elif media.media_type == 8: # Album/Carousel
                    print(f"Type: Album. Contains {len(media.resources)} items. Downloading...")
                    # Download each item in the album
                    for resource in media.resources:
                        if resource.media_type == 1: # Photo in Album
                            print(f"  - Downloading photo {resource.pk} from album...")
                            cl.photo_download(resource.pk, folder=download_folder)
                        elif resource.media_type == 2: # Video in Album
                            print(f"  - Downloading video {resource.pk} from album...")
                            cl.video_download(resource.pk, folder=download_folder)
                else:
                    print(f"Skipping unsupported media type: {media.media_type}")

                print(f"Downloaded media {media.pk} successfully.")
            except Exception as e:
                print(f"Error downloading media {media.pk}: {e}")

        print("\nFinished downloading all media.")
    except Exception as e:
        print(f"\nAn error occurred while fetching media: {e}")

if __name__ == "__main__":
    download_all_user_media()
