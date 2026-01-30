import os
from instagrapi import Client

def main():
    client = Client()

    # Set proxy to bypass IP blacklist (replace with your proxy details)
    # Example: "http://your-proxy-ip:port" or "socks5://user:pass@proxy-ip:port"
    # You can find free proxies online or use a VPN service
    proxy_url = input("Enter proxy URL (e.g., http://proxy-ip:port) or press Enter to skip: ").strip()
    if proxy_url:
        client.set_proxy(proxy_url)
        print(f"Using proxy: {proxy_url}")

    session_file = 'session.json'

    if os.path.exists(session_file):
        # Load existing session
        try:
            client.load_settings(session_file)
            client.login("", "")  # Login with saved session
            print("Logged in using saved session.")
        except Exception as e:
            print(f"Failed to load session: {e}")
            os.remove(session_file)  # Remove invalid session file
            login_with_credentials(client, session_file)
    else:
        login_with_credentials(client, session_file)

def login_with_credentials(client, session_file):
    # Prompt for credentials
    username = input("Enter your Instagram username: ")
    password = input("Enter your Instagram password: ")

    try:
        # Attempt to login
        client.login(username, password)
        print("Login successful!")

        # Save the session for reuse
        client.dump_settings(session_file)
        print(f"Session saved to '{session_file}'. You can reuse this session in future runs.")

    except Exception as e:
        print(f"Login failed: {e}")
        # Handle challenge if it's a challenge required
        if "challenge_required" in str(e) or "We can send you an email" in str(e):
            print("Challenge required. Please check your email for the verification code.")
            code = input("Enter the 6-digit code from your email: ")
            try:
                client.challenge_code(code)
                print("Challenge resolved. Login successful!")
                # Save the session for reuse
                client.dump_settings(session_file)
                print(f"Session saved to '{session_file}'. You can reuse this session in future runs.")
            except Exception as challenge_e:
                print(f"Failed to resolve challenge: {challenge_e}")

if __name__ == "__main__":
    main()