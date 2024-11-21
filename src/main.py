import os
import json
import ani
import non_aniV2
import sys
import time
import unrestrict
import RD
import torrentLibrary
from mpv_auto import play_in_mpv
import dmm_api
from playwright.sync_api import sync_playwright
import delete_torrents
import hosters


TOKEN_PATH = 'token.json'

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

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    while True:
        try:
            token = get_token()

            while True:
                clear_screen()
                time.sleep(0.5)
                print("Options:\n1. Search Movies/TV Shows\n2. Get Movies/TV Shows in Library\n3. Add Magnet Link\n4. Unrestrict Link\n5. Delete a Torrent from Library\n6. Check Hosters' Status")
                choice = input("Enter Option Number: ")
                
                if choice == '1':
                    while True:
                        media_type = input("\nAnime or Non-Anime? [A/N]: ").strip().upper()

                        if media_type == 'A':
                            ani.main()
                            break
                        elif media_type == 'N':                           
                                non_aniV2.main()
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
                    delete_torrents.main()
                    continue
                if choice == '6':
                    hosters.main()
                else:
                    print("\nInvalid input. Please enter a Number from 1 to 6.")
                    time.sleep(2)

        except Exception as e:
            error_message = str(e)
            print(f"\nAn error occurred:\n{error_message}")
            input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
