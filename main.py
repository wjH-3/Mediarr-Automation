import os
import json
import ani
import non_ani
import sys
import time
import unrestrict
import RD
import DMM_library
import torrentLibrary

CONFIG_PATH = 'config.json'
TOKEN_PATH = 'token.json'

def get_config():
    if getattr(sys, 'frozen', False):  # Check if running as an executable
        config_dir = os.path.dirname(sys.executable)
    else:
        config_dir = os.path.dirname(__file__)

    config_path = os.path.join(config_dir, CONFIG_PATH)

    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    else:
        return create_config(config_path)

def create_config(config_path):
    print("First-time setup. Please input the necessary information. The config will be stored locally in 'config.json'. (Note: Input is case-sensitive.)")
    print("You can find the relevant info at: chrome://version/, under 'Profile Path'.")
    user = input("Enter your system user name: ").strip()
    profile = input("Enter your Chrome profile directory name: ").strip()
    config = {'user': user, 'profile': profile}

    try:
        with open(config_path, 'w') as f:
            json.dump(config, f)
        print("Configuration saved successfully.\n")
    except IOError as e:
        print(f"Unable to write config file. Error: {e}")
        print("You'll need to enter this information each time you run the program.")

    return config

def get_token():
    if getattr(sys, 'frozen', False):
        token_dir = os.path.dirname(sys.executable)
    else:
        token_dir = os.path.dirname(__file__)

    token_path = os.path.join(token_dir, TOKEN_PATH)

    if os.path.exists(token_path):
        with open(token_path, 'r') as f:
            return json.load(f)
    else:
        return create_token(token_path)  # Changed from create_config to create_token

def create_token(token_path):
    print("First-time setup. Please input the Real-Debrid API token. The token will be stored locally in 'token.json'.")
    print("You can find your token at: https://real-debrid.com/apitoken")
    api_token = input("Enter your RD API token: ").strip()
    token = {'token': api_token}

    try:
        with open(token_path, 'w') as f:
            json.dump(token, f)
        print("API token saved successfully.\n")
    except IOError as e:
        print(f"Unable to write token file. Error: {e}")
        print("You'll need to enter this information each time you run the program.")

    return token

def run_non_ani(user, profile):
    # Preserve the original sys.argv
    original_argv = sys.argv.copy()
    
    # Set sys.argv for non_ani.py
    sys.argv = [sys.argv[0], user, profile]
    
    try:
        # Run non_ani.main()
        non_ani.main()
    finally:
        # Restore the original sys.argv
        sys.argv = original_argv

def open_DMM_library(user, profile):
    # Preserve the original sys.argv
    original_argv = sys.argv.copy()
    
    # Set sys.argv for non_ani.py
    sys.argv = [sys.argv[0], user, profile]
    
    try:
        # Run non_ani.main()
        DMM_library.main()
    finally:
        # Restore the original sys.argv
        sys.argv = original_argv

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    try:
        config = get_config()
        token = get_token()

        while True:
            clear_screen()
            options = print("Options:\n1. Search Movies/TV Shows\n2. Get Movies/TV Shows in Library\n3. Add Magnet Link\n4. Unrestrict Link\n5. Go DMM Library")
            choice = input("Enter Option Number: ")
            if choice == '1':
                while True:
                    media_type = input("\nAnime or Non-Anime? [A/N]: ").strip().upper()

                    if media_type == 'A':
                        ani.main()
                        break
                    elif media_type == 'N':
                        run_non_ani(config['user'], config['profile'])
                        break
                    else:
                        print("Invalid choice. Please enter A for Anime or N for Non-Anime.")
                continue
            if choice == '2':
                torrentLibrary.main()
                continue
            if choice == '3':
                RD.main()
                continue
            if choice == '4':
                unrestrict.main()
                continue
            if choice == '5':
                open_DMM_library(config['user'], config['profile'])
                continue
            else:
                print("Invalid input, please enter a number from 1 to 5.")
                time.sleep(2)
    
    except Exception as e:
        print(f"\nAn error occurred:\n{str(e)}")
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
