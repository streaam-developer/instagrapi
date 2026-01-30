import os
import glob
import shutil
import time
from playwright.sync_api import sync_playwright, TimeoutError

def upload_videos_with_playwright():
    """
    Logs into multiple Instagram accounts using Playwright, saves sessions, and uploads videos from the 'videos' directory one by one per account.
    Uses a realistic browser fingerprint. Can be configured to run headless or show the browser.
    """
    # --- Configuration ---
    # Set to True to see the browser in action, False to run in the background.
    SHOW_BROWSER = True

    videos_dir = 'videos'
    uploaded_dir = os.path.join(videos_dir, 'uploaded')
    sessions_dir = 'sessions'
    os.makedirs(uploaded_dir, exist_ok=True)
    os.makedirs(sessions_dir, exist_ok=True)

    # --- Accounts ---
    # List of accounts to automate
    accounts = [
        {"username": "rinki280200", "password": "rMuD@e5HH5vuvJE"},
        # Add more accounts here
    ]

    # --- Find Videos ---
    video_files = glob.glob(os.path.join(videos_dir, '*.mp4'))
    if not video_files:
        print(f"No .mp4 videos found in the '{videos_dir}' directory.")
        return

    print(f"Found {len(video_files)} videos to upload.")

    with sync_playwright() as p:
        # --- Launch Browser ---
        browser = p.chromium.launch(
            headless=not SHOW_BROWSER,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
        )

        for account in accounts:
            username = account['username']
            password = account['password']
            session_path = os.path.join(sessions_dir, f"{username}_session.json")

            print(f"\nProcessing account: {username}")

            # Check if session exists
            if os.path.exists(session_path):
                print(f"Loading existing session for {username}")
                context = browser.new_context(storage_state=session_path)
            else:
                print(f"No session found for {username}, logging in...")
                context = browser.new_context()
                page = context.new_page()

                try:
                    # --- Login ---
                    page.goto("https://www.instagram.com/accounts/login/", timeout=60000)
                    page.wait_for_load_state('networkidle', timeout=30000)

                    # Additional wait for dynamic content
                    time.sleep(5)

                    # Debug: Save page source
                    with open(f"debug_{username}_page.html", "w", encoding="utf-8") as f:
                        f.write(page.content())
                    print(f"Saved page source to debug_{username}_page.html")

                    # Debug: Print all placeholders
                    inputs = page.query_selector_all("input")
                    print(f"Found {len(inputs)} inputs:")
                    for inp in inputs:
                        placeholder = inp.get_attribute('placeholder')
                        name = inp.get_attribute('name')
                        aria_label = inp.get_attribute('aria-label')
                        print(f"  - name: {name}, placeholder: {placeholder}, aria-label: {aria_label}")

                    # Wait for login form - try multiple selectors with longer timeout
                    try:
                        page.wait_for_selector("input[name='email']", timeout=30000)
                        username_selector = "input[name='email']"
                        password_selector = "input[name='pass']"
                    except TimeoutError:
                        try:
                            page.wait_for_selector("input[name='username']", timeout=30000)
                            username_selector = "input[name='username']"
                            password_selector = "input[name='password']"
                        except TimeoutError:
                            raise Exception("Could not find login form inputs")

                    # Fill username
                    username_field = page.locator(username_selector)
                    username_field.fill(username)

                    # Fill password
                    password_field = page.locator(password_selector)
                    password_field.fill(password)

                    # Click login
                    login_button = page.get_by_role("button", name="Log in")
                    login_button.click()

                    # Wait for login to complete
                    page.wait_for_load_state('networkidle', timeout=60000)

                    # Handle pop-ups
                    try:
                        page.get_by_role("button", name="Not Now").click(timeout=10000)
                    except TimeoutError:
                        pass
                    try:
                        page.get_by_role("button", name="Not Now").click(timeout=10000)
                    except TimeoutError:
                        pass

                    # Save session
                    context.storage_state(path=session_path)
                    print(f"Session saved for {username}")

                except Exception as e:
                    print(f"Login failed for {username}: {e}")
                    context.close()
                    continue

            page = context.new_page()

            # --- Upload Loop for this account ---
            for video_path in video_files:
                filename = os.path.basename(video_path)
                caption = os.path.splitext(filename)[0]

                print(f"Starting upload for '{filename}' on {username}...")

                try:
                    # Navigate to home if not already
                    page.goto("https://www.instagram.com/", timeout=60000)

                    # Click create post
                    page.get_by_role("link", name="New post").click()

                    # Select file
                    with page.expect_file_chooser() as fc_info:
                        page.get_by_role("button", name="Select from computer").click()
                    file_chooser = fc_info.value
                    file_chooser.set_files(video_path)

                    # Proceed
                    page.get_by_role("button", name="Next").click()
                    page.get_by_role("button", name="Next").click()

                    # Add caption
                    page.get_by_role("textbox", name="Write a caption...").fill(caption)

                    # Share
                    page.get_by_role("button", name="Share").click()

                    # Wait for success
                    page.wait_for_selector("//span[text()='Your post has been shared.']", timeout=120000)
                    print(f"Successfully uploaded '{filename}' on {username}!")

                    # Move file after all accounts have uploaded it
                    # We'll move after processing all accounts

                except Exception as e:
                    print(f"Could not upload '{filename}' on {username}. Reason: {e}")
                    try:
                        page.get_by_label("Close").click()
                    except:
                        pass

            # Close context for this account
            context.close()

        # After all accounts, move uploaded videos
        for video_path in video_files:
            filename = os.path.basename(video_path)
            shutil.move(video_path, os.path.join(uploaded_dir, filename))
            print(f"Moved '{filename}' to uploaded folder.")

        print("\nAll videos processed for all accounts.")
        browser.close()

if __name__ == "__main__":
    upload_videos_with_playwright()

