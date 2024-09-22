import os
import json
import ani
import non_ani
import sys

CONFIG_PATH = 'config.json'

def get_config():
    if getattr(sys, 'frozen', False):
        # Running as compiled exe
        config_dir = os.path.dirname(sys.executable)
    else:
        # Running as script
        config_dir = os.path.dirname(__file__)
    
    config_path = os.path.join(config_dir, CONFIG_PATH)
    
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    else:
        return create_config(config_path)

def create_config(config_path):
    print("First-time setup. Please input the necessary information. (Note: Input is case-sensitive)")
    user = input("Enter your system user name: ").strip().upper()
    profile = input("Enter your Chrome profile directory name: ").strip().upper()
    config = {'user': user, 'profile': profile}

    try:
        with open(config_path, 'w') as f:
            json.dump(config, f)
    except IOError as e:
        print(f"Unable to write config file. Error: {e}")
        print("You'll need to enter this information each time you run the program.")

    return config

def main():
    config = get_config()

    while True:
        choice = input("Anime or Non-Anime? [A/N]: ").strip().upper()

        if choice == 'A':
            ani.main()
        elif choice == 'N':
            non_ani.set_global_variables(config['user'], config['profile'])
            non_ani.main()
        else:
            print("Invalid choice. Please enter A for Anime or N for Non-Anime.")

if __name__ == "__main__":
    main()