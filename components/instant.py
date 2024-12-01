import requests
import time

VIDEO_EXTENSIONS = ('.avi', '.mkv', '.mp4', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpeg', '.mpg')

def add_magnet(api_token, magnet_hash):
        url = "https://api.real-debrid.com/rest/1.0/torrents/addMagnet"
        headers = {"Authorization": f"Bearer {api_token}"}
        data = {"magnet": f"magnet:?xt=urn:btih:{magnet_hash}"}
        response = requests.post(url, headers=headers, data=data)
        #print(response.json())
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
    print(response.json())
    return response.json()

def is_video(filename):
    return filename.lower().endswith(VIDEO_EXTENSIONS)

def delete_torrent(api_token, torrent_id):
    url = f"https://api.real-debrid.com/rest/1.0/torrents/delete/{torrent_id}"
    headers = {"Authorization": f"Bearer {api_token}"}
    response = requests.delete(url, headers=headers)
    if response.status_code == 204:
        return
    
def pseudo_instant_check(magnet_hash, api_token):    
    add_result = add_magnet(api_token, magnet_hash)
    # Check if 'error' exists in the response and handle it
    if 'error' in add_result and add_result['error']:
        print(f"Error: {add_result['error']}")
        return False, None        
    torrent_id = add_result['id']
    info = get_torrent_info(api_token, torrent_id)
    print(f"Torrent File: {info['filename']}")
    if info['status'] == 'waiting_files_selection':
        # Select video files
        video_files = [file for file in info['files'] if is_video(file['path'])]
        video_file_ids = [file['id'] for file in video_files]
        if not video_file_ids:
            return False, torrent_id
    else:
        return False, torrent_id
    select_files(api_token, torrent_id, video_file_ids)
    info_2 = get_torrent_info(api_token, torrent_id)
    if info_2['status'] == 'downloaded':
        return True, torrent_id
    else:
        return False, torrent_id
    
def main():
    api_token = input("Enter API token: ")
    
    # TEST HASHES:
    # Arcane S02E04 1080p WEB-DL FLUX (CACHED): 8cf843d57f7702e6176a419378135f5130706db7
    # Tenet 1080p BluRay REMUX FraMeSToR (UNCACHED): 571d85882b7733c2d16c0dd534721f5820ba9592
    # The Outsider S01 1080p BluRay REMUX PmP (CACHED): ef2e20adbf8a6af9b72708b75c1b01e5cc7794b5
    # Black Mirror S03 1080i BluRau REMUX EPSiLON (UNCACHED): a1217dc6b392cb7a1d47f901e92d3bd7e5c11c22
    # INFRINGING FILE (Error Code 35): 0c234063653cb6ae7437d70a388751da1821ef58
    # INTERNAL ERROR (Error Code -1): aa0917dfdf60a3fb6f4fb7cad679783ffc194561
    # INTERNAL ERROR (Error Code -1) (NOT Invalid Magnet): 13651b8db7074da3aa0d1bfebb479f75fef03ca2
    magnet_hash = input("Enter Magnet Hash: ")

    start_time = time.perf_counter()
    result, torrent_id = pseudo_instant_check(magnet_hash, api_token)
    delete_torrent(api_token, torrent_id)
    end_time = time.perf_counter()
    if result is True:
        print("Torrent is instantly available.")
    elif result is False:
        print("Torrent is not instantly available.")
    else:
        print("Failed to check for instant availability.")
    runtime = (end_time - start_time) * 1000
    print("Runtime:", round(runtime, 2), "ms")

if __name__ == "__main__":
    main()
