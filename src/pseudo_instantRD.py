import requests
import json
import sys
import os
import time
import RD
import re

VIDEO_EXTENSIONS = ('.avi', '.mkv', '.mp4', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpeg', '.mpg')

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

def is_video(filename):
    return filename.lower().endswith(VIDEO_EXTENSIONS)

def delete_torrent(api_token, torrent_id):
    url = f"https://api.real-debrid.com/rest/1.0/torrents/delete/{torrent_id}"
    headers = {"Authorization": f"Bearer {api_token}"}
    response = requests.delete(url, headers=headers)
    if response.status_code == 204:
        return
    
def pseudo_instant_check(magnet_link, api_token):    
    add_result = add_magnet(api_token, magnet_link)
    torrent_id = add_result['id']
    info = get_torrent_info(api_token, torrent_id)
    if info['status'] == 'waiting_files_selection':
        # Select video files
        video_files = [file for file in info['files'] if is_video(file['path'])]
        video_file_ids = [file['id'] for file in video_files]
        if not video_file_ids:
            delete_torrent(api_token, torrent_id)
            return False
    else:
        delete_torrent(api_token, torrent_id)
        return False
    select_files(api_token, torrent_id, video_file_ids)
    info_2 = get_torrent_info(api_token, torrent_id)
    if info_2['status'] == 'downloaded':
        delete_torrent(api_token, torrent_id)
        return True
    else:
        delete_torrent(api_token, torrent_id)
        return False

def main():
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

    while True:
        magnet_link = input("\nEnter Magnet Link: ")

        hash_match = re.search(r'btih:([a-fA-F0-9]{40})', magnet_link)
        if not hash_match:
            print("Invalid magnet link.")
        else:
            break
    
    result = pseudo_instant_check(magnet_link, api_token)

    if result is True:
        print("Torrent is instantly available.")
        RD.main(magnet_link)
    elif result is False:
        print("Torrent is not instantly available.")
        while True:
            choice = input("Do you want to proceed? [Y/N]: ").strip().upper()
            if choice == 'N':
                print("Exiting...\n")
                time.sleep(1)
                return
            if choice == 'Y':
                RD.main(magnet_link)
            else:
                print("Invalid input. Please enter 'Y' for yes or 'N' for no.")
    else:
        print("Failed to check for instant availability.")
        input("Press Enter to Exit...")
        return

if __name__ == "__main__":
    main()
