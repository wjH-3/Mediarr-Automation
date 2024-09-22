import os
import json
import subprocess

def get_non_anime_config():
    # Check if configuration already exists
    config_path = 'non_anime_config.json'
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    else:
        # First-time setup
        print("First-time setup for Non-Anime script. Please input the necessary information variables. (Note: Input is case-sensitive)")
        user = input("Enter your system user name: ") # Case-sesitive
        profile = input("Enter your Chrome profile name: ") # Case-sensitive
        config = {'user': user, 'profile': profile}

        # Save configuration for future runs
        with open(config_path, 'w') as f:
            json.dump(config, f)

        return config

def run_anime_script():
    # Run the anime script (replace 'anime_script.py' with the actual script name)
    subprocess.run(['python', 'ani.py'])

def run_non_anime_script():
    # Get user and profile info from config
    config = get_non_anime_config()
    user = config['user']
    profile = config['profile']

    # Inject into the non-anime script (replace 'non_anime_script.py' with the actual script name)
    subprocess.run(['python', 'non-ani.py', user, profile])

def main():
    print("Anime or Non-Anime? [A/N]")
    choice = input().strip().upper()

    if choice == 'A':
        run_anime_script()
    elif choice == 'N':
        run_non_anime_script()
    else:
        print("Invalid choice. Please enter A for Anime or N for Non-Anime.")

if __name__ == "__main__":
    main()