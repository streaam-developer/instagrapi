from instagrapi import Client
import json

def get_user_details():
    cl = Client()
    try:
        cl.load_settings('session.json')
        cl.login_by_sessionid(cl.sessionid)
        print("Login successful!")

        # Get own user ID
        user_id = cl.user_id

        # Fetch user info
        user_info = cl.user_info(user_id)

        print("\n--- Your Account Details ---")
        print(f"Username: {user_info.username}")
        print(f"Full Name: {user_info.full_name}")
        print(f"Followers: {user_info.follower_count}")
        print(f"Following: {user_info.following_count}")
        print(f"Biography: {user_info.biography}")
        print(f"Public Profile: {'Yes' if not user_info.is_private else 'No'}")
        print(f"Verified: {'Yes' if user_info.is_verified else 'No'}")
        print("--------------------------\n")

    except FileNotFoundError:
        print("Error: session.json not found. Please run login_script.py first to create a session file.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    get_user_details()
