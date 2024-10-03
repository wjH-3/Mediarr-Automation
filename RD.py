import requests
import json
import time
import sys
import os
import pyperclip

VIDEO_EXTENSIONS = ('.avi', '.mkv', '.mp4', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpeg', '.mpg')

def check_instant_availability(api_token, magnet_link):
    # Extract hash from magnet link
    import re
    hash_match = re.search(r'btih:([a-fA-F0-9]{40})', magnet_link)
    if not hash_match:
        print("Invalid magnet link")
        return False
    
    torrent_hash = hash_match.group(1).lower()
    
    url = f"https://api.real-debrid.com/rest/1.0/torrents/instantAvailability/{torrent_hash}"
    headers = {"Authorization": f"Bearer {api_token}"}
    response = requests.get(url, headers=headers)
    availability_data = response.json()
    
    # print("Instant Availability:")
    # print(json.dumps(availability_data, indent=2))
    
    # Check if there are any files available
    is_available = (
        isinstance(availability_data, dict) and
        torrent_hash in availability_data and
        isinstance(availability_data[torrent_hash], dict) and
        'rd' in availability_data[torrent_hash] and
        isinstance(availability_data[torrent_hash]['rd'], list) and
        len(availability_data[torrent_hash]['rd']) > 0
    )
    
    if is_available:
        print("\nThis torrent is instantly available.")
    else:
        print("\nThis torrent is not instantly available.")
    
    return is_available

def add_magnet(api_token, magnet_link):
    url = "https://api.real-debrid.com/rest/1.0/torrents/addMagnet"
    headers = {"Authorization": f"Bearer {api_token}"}
    data = {"magnet": magnet_link}
    response = requests.post(url, headers=headers, data=data)
    return response.json()

def get_torrent_info(api_token, torrent_id):
    url = f"https://api.real-debrid.com/rest/1.0/torrents/info/{torrent_id}"
    headers = {"Authorization": f"Bearer {api_token}"}
    response = requests.get(url, headers=headers)
    return response.json()

def select_files(api_token, torrent_id, file_ids):
    url = f"https://api.real-debrid.com/rest/1.0/torrents/selectFiles/{torrent_id}"
    headers = {"Authorization": f"Bearer {api_token}"}
    data = {"files": ",".join(map(str, file_ids))}
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 204:
        return {"success": True}
    return response.json()

def unrestrict_link(api_token, link):
    url = "https://api.real-debrid.com/rest/1.0/unrestrict/link"
    headers = {"Authorization": f"Bearer {api_token}"}
    data = {"link": link}
    response = requests.post(url, headers=headers, data=data)
    return response.json()

def is_video(filename):
    return filename.lower().endswith(VIDEO_EXTENSIONS)

def process_torrent(api_token, magnet_link):
    print("Processing...")
    add_result = add_magnet(api_token, magnet_link)
    print(f"Successfully added hash: {magnet_link}")

    torrent_id = add_result['id']
    
    while True:
        # Get initial torrent info
        info = get_torrent_info(api_token, torrent_id)
        if info['status'] == 'waiting_files_selection':
            # Select video files
            video_files = [file for file in info['files'] if is_video(file['path'])]
            video_file_ids = [file['id'] for file in video_files]
            if not video_file_ids:
                print("No video files found in the torrent.")
                input("\nPress Enter to Exit...")
                return
            break
        else:
            print(f"Status: {info['status']}")
        time.sleep(10)
 
    print(f"Selecting {len(video_file_ids)} video file(s)...")
    select_result = select_files(api_token, torrent_id, video_file_ids)

    # Wait for torrent to be downloaded
    while True:
        info = get_torrent_info(api_token, torrent_id)
        if info['status'] == 'downloaded':
            print("Torrent succesfully downloaded.")
            break
        else:
            print(f"Status: {info['status']}; Progress: {info['progress']}%")
        time.sleep(10)  # Wait 10 seconds before checking again

    links = info.get('links', [])
    if not links:
        print("Warning: No links found in torrent info.")
        input("\nPress Enter to Exit...")
        return

    print(f"Unrestricting {len(links)} link(s)...")
    unrestricted_links = []
    for link in links:
        unrestricted = unrestrict_link(api_token, link)
        unrestricted_links.append(unrestricted)

    print("All links successfully unrestricted.")

    if len(links) == 1:
        # Use the first unrestricted link for single link case
        selected_file = unrestricted_links[0]
        print(f"\nFile: {selected_file['filename']}")
        print(f"Download Link: {selected_file['download']}")
        pyperclip.copy(selected_file['download'])
        print("Download Link successfully copied to clipboard.\n")
        input("Press Enter to Exit...")
    else:
        print("\nFile list:")
        for i, link in enumerate(unrestricted_links, 1):
            print(f"{i}. {link['filename']}")

        while True:
            choice = input("Input Number to Choose File or press Enter to Exit: ")

            if choice == "":  # If the user presses Enter without input
                print("Exiting...\n")
                time.sleep(1)
                break

            try:
                choice = int(choice)
                if 1 <= choice <= len(unrestricted_links):
                    selected_file = unrestricted_links[choice - 1]
                    print(f"\nSelected file: {selected_file['filename']}")
                    print(f"Download link: {selected_file['download']}")
                    pyperclip.copy(selected_file['download'])
                    print("Download Link successfully copied to clipboard.\n")
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a valid number.")

def main(auto_paste=False):
    # Get the API token from the token.json file
    token_data = None
    if getattr(sys, 'frozen', False):
        token_path = os.path.join(os.path.dirname(sys.executable), 'token.json')
    else:
        token_path = os.path.join(os.path.dirname(__file__), 'token.json')
    
    try:
        with open(token_path, 'r') as f:
            token_data = json.load(f)
    except FileNotFoundError:
        print("API token not found. Please run the main script to set up your token.")
        input("\nPress Enter to Exit...")
        return
    
    api_token = token_data.get('token')
    if not api_token:
        print("Invalid token data. Please run the main script to set up your token.")
        input("\nPress Enter to Exit...")
        return
    
    if auto_paste:
        magnet_link = pyperclip.paste()
    else:
        magnet_link = input("\nEnter the Magnet Link: ")

    is_instant = check_instant_availability(api_token, magnet_link)
    
    if not is_instant:
        choice = input("Do you want to proceed? [Y/N]: ").strip().upper()
        while True:
            if choice == 'N':
                print("Exiting...\n")
                time.sleep(1)
                return
            if choice == 'Y':
                break
            else:
                print("Invalid input. Please enter 'Y' for yes or 'N' for no.")

    process_torrent(api_token, magnet_link)

if __name__ == "__main__":
    main()
