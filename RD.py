import requests
import json
import time

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
    # A 204 status code means success with no content, which is expected for this API call
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

def main():
    api_token = input("Enter your Real-Debrid API token: ")
    magnet_link = input("Enter the magnet link: ")

    print("Processing...")
    add_result = add_magnet(api_token, magnet_link)
    print(f"Successfully added hash: {magnet_link}")

    torrent_id = add_result['id']
    
    time.sleep(5)

    # Get initial torrent info
    info = get_torrent_info(api_token, torrent_id)
    
    # Select video files
    video_files = [file for file in info['files'] if is_video(file['path'])]
    video_file_ids = [file['id'] for file in video_files]
    
    if not video_file_ids:
        print("No video files found in the torrent.")
        return

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
        return

    print(f"Unrestricting {len(links)} link(s)...")
    unrestricted_links = []
    for link in links:
        unrestricted = unrestrict_link(api_token, link)
        unrestricted_links.append(unrestricted)

    print("All links successfully unrestricted.")

    # Display file list and prompt user for selection
    print("\nFile list:")
    for i, link in enumerate(unrestricted_links, 1):
        print(f"{i}. {link['filename']}")

    while True:
        try:
            choice = int(input("\nEnter number to choose file: "))
            if 1 <= choice <= len(unrestricted_links):
                selected_file = unrestricted_links[choice - 1]
                print(f"\nSelected file: {selected_file['filename']}")
                print(f"Download link: {selected_file['download']}")
                break
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

if __name__ == "__main__":
    main()