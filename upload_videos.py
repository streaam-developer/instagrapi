import os
import glob
import shutil
from instagrapi import Client
from instagrapi.types import Media

def upload_videos_from_directory():
    """
    Uploads all .mp4 videos from the 'videos' directory to Instagram,
    using the saved session. Moves uploaded videos to 'videos/uploaded'.
    """
    cl = Client()
    session_file = 'session.json'
    videos_dir = 'videos'
    uploaded_dir = os.path.join(videos_dir, 'uploaded')

    # Ensure directories exist
    os.makedirs(videos_dir, exist_ok=True)
    os.makedirs(uploaded_dir, exist_ok=True)

    try:
        # Load session and login
        cl.load_settings(session_file)
        cl.login_by_sessionid(cl.sessionid)
        print("Login successful. Starting video uploads...")
    except FileNotFoundError:
        print(f"Error: '{session_file}' not found. Please run login_script.py to create a session.")
        return
    except Exception as e:
        print(f"An error occurred during login: {e}")
        return

    # Find video files
    video_files = glob.glob(os.path.join(videos_dir, '*.mp4'))

    if not video_files:
        print(f"No .mp4 videos found in the '{videos_dir}' directory.")
        return

    print(f"Found {len(video_files)} videos to upload.")

    for video_path in video_files:
        filename = os.path.basename(video_path)
        caption = os.path.splitext(filename)[0] # Use filename as caption
        
        print(f"\nUploading '{filename}'...")
        try:
            media = cl.video_upload(video_path, caption=caption)
            print(f"Successfully uploaded '{filename}'!")
            
            # Move the uploaded video
            shutil.move(video_path, os.path.join(uploaded_dir, filename))
            print(f"Moved '{filename}' to the '{uploaded_dir}' directory.")

        except Exception as e:
            print(f"Error uploading '{filename}': {e}")
            # Optionally, move failed uploads to a 'failed' directory
            # failed_dir = os.path.join(videos_dir, 'failed')
            # os.makedirs(failed_dir, exist_ok=True)
            # shutil.move(video_path, os.path.join(failed_dir, filename))

if __name__ == "__main__":
    upload_videos_from_directory()
