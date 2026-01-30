import os
from instagrapi import Client

def main():
    client = Client()
    session_file = 'session.json'

    if os.path.exists(session_file):
        try:
            client.load_settings(session_file)
            client.login("", "")  # Login with saved session
            print("Logged in using saved session.")
        except Exception as e:
            print(f"Failed to load session: {e}")
            os.remove(session_file)
            login_with_credentials(client, session_file)
    else:
        login_with_credentials(client, session_file)

def login_with_credentials(client, session_file):
    login_method = input("How would you like to login? (1 - Credentials, 2 - Session ID): ")
    if login_method == '2':
        session_id = input("Enter your Instagram session ID: ")
        try:
            client.login_by_sessionid(session_id)
            print("Login successful!")
            client.dump_settings(session_file)
            print(f"Session saved to '{session_file}'.")
        except Exception as e:
            print(f"Login failed: {e}")
    else:
        username = input("Enter your Instagram username: ")
        password = input("Enter your Instagram password: ")
        try:
            client.login(username, password)
            print("Login successful!")
            client.dump_settings(session_file)
            print(f"Session saved to '{session_file}'.")
        except Exception as e:
            print(f"Login failed: {e}")

if __name__ == "__main__":
    main()