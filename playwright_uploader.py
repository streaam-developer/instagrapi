import os
import glob
import shutil
import time
from playwright.sync_api import sync_playwright, TimeoutError

def upload_videos_with_playwright():
    """
    Logs into Instagram using Playwright and uploads videos from the 'videos' directory.
    Uses a realistic browser fingerprint. Can be configured to run headless or show the browser.
    """
    # --- Configuration ---
    # Set to True to see the browser in action, False to run in the background.
    SHOW_BROWSER = True

    videos_dir = 'videos'
    uploaded_dir = os.path.join(videos_dir, 'uploaded')
    os.makedirs(uploaded_dir, exist_ok=True)

    # --- Credentials ---
    # WARNING: Storing passwords in code is not secure.
    username = "rinki280200"
    password = "rMuD@e5HH5vuvJE"

    # --- Find Videos ---
    video_files = glob.glob(os.path.join(videos_dir, '*.mp4'))
    if not video_files:
        print(f"No .mp4 videos found in the '{videos_dir}' directory.")
        return

    print(f"Found {len(video_files)} videos to upload.")

    with sync_playwright() as p:
        # --- Launch Browser ---
        # Using a device emulator for a realistic browser fingerprint.
        device = p.devices['Desktop Chrome']
        browser = p.chromium.launch(headless=not SHOW_BROWSER)
        context = browser.new_context(**device)
        page = context.new_page()

        try:
            # --- Login ---
            print("Navigating to Instagram login page...")
            page.goto("https://www.instagram.com/", timeout=60000)
            
            # Wait for login fields to appear
            page.wait_for_selector("input[name='username']", timeout=30000)

            print("Entering credentials...")
            page.fill("input[name='username']", username)
            page.fill("input[name='password']", password)
            
            print("Logging in...")
            page.click("button[type='submit']")
            page.wait_for_load_state('networkidle', timeout=60000)

            # --- Handle Pop-ups ---
            print("Handling post-login pop-ups...")
            # "Save your login info?"
            try:
                page.get_by_role("button", name="Not Now").click(timeout=10000)
                print("Dismissed 'Save Info' pop-up.")
            except TimeoutError:
                print("No 'Save Info' pop-up appeared.")
            
            # "Turn on Notifications"
            try:
                page.get_by_role("button", name="Not Now").click(timeout=10000)
                print("Dismissed 'Notifications' pop-up.")
            except TimeoutError:
                print("No 'Notifications' pop-up appeared.")

            # --- Upload Loop ---
            for video_path in video_files:
                filename = os.path.basename(video_path)
                caption = os.path.splitext(filename)[0]

                print(f"\nStarting upload for '{filename}'...")
                
                try:
                    # Click the 'Create' button
                    page.get_by_role("link", name="New post").click()

                    # Handle the file chooser
                    with page.expect_file_chooser() as fc_info:
                        page.get_by_role("button", name="Select from computer").click()
                    file_chooser = fc_info.value
                    file_chooser.set_files(video_path)
                    print(f"Selected '{filename}' for upload.")
                    
                    page.get_by_role("button", name="Next").click() # To Filters
                    page.get_by_role("button", name="Next").click() # To Share screen
                    
                    # Write caption
                    page.get_by_role("textbox", name="Write a caption...").fill(caption)
                    print("Added caption.")

                    # Share post
                    page.get_by_role("button", name="Share").click()
                    
                    # Wait for confirmation
                    page.wait_for_selector("//span[text()='Your post has been shared.']", timeout=120000)
                    print(f"Successfully uploaded '{filename}'!")
                    
                    # Move the file
                    shutil.move(video_path, os.path.join(uploaded_dir, filename))
                    print(f"Moved '{filename}' to uploaded folder.")

                except Exception as e:
                    print(f"Could not upload '{filename}'. Reason: {e}")
                    # Close the create post dialog if it's still open
                    try:
                        page.get_by_label("Close").click()
                    except:
                        pass # Ignore if it's already closed
            
            print("\nAll videos processed.")

        except Exception as e:
            print(f"\nAn error occurred: {e}")
        finally:
            print("Closing browser.")
            browser.close()

if __name__ == "__main__":
    upload_videos_with_playwright()
