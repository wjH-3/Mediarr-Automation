import os
import json
import ani
import non_ani
import sys

CONFIG_PATH = 'config.json'

def get_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    else:
        print("First-time setup. Please input the necessary information. (Note: Input is case-sensitive)")
        user = input("Enter your system user name: ")
        profile = input("Enter your Chrome profile directory name: ")
        config = {'user': user, 'profile': profile}

        with open(CONFIG_PATH, 'w') as f:
            json.dump(config, f)

        return config

def main():
    config = get_config()

    while True:
        choice = input("Anime or Non-Anime? [A/N]: ").strip().upper()

        if choice == 'A':
            ani.main()
        elif choice == 'N':
            # Pass config as command line arguments
            sys.argv = [sys.argv[0], config['user'], config['profile']]
            non_ani.main()
        else:
            print("Invalid choice. Please enter A for Anime or N for Non-Anime.")

if __name__ == "__main__":
    main()