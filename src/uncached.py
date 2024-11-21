import time
import requests
import os
import  json
import sys

def get_torrent_list(api_token):
    all_torrents = []
    page = 1
    has_more_pages = True
    url = "https://api.real-debrid.com/rest/1.0/torrents"
    headers = {"Authorization": f"Bearer {api_token}"}

    #print("\nChecking if there are matching torrents already in the torrent library...")
    #print("Fetching torrent library...")

    while has_more_pages:
        response = requests.get(
            url,
            params={'page': page},
            headers=headers
        )
        
        # Check for 204 No Content, indicating no more torrents
        if response.status_code == 204:
            #print("All torrents fetched.")
            break
        elif response.status_code != 200:
            print(f"API Error: {response.status_code}, {response.text}")
            break
        
        try:
            page_data = response.json()
        except json.JSONDecodeError as e:
            print(f"API Error: {str(e)}. Response content: {response.text}")
            break

        if not page_data:
            has_more_pages = False
        else:
            all_torrents.extend(page_data)
            page += 1

    #print(f"Total number of torrents: {len(all_torrents)}")
    return all_torrents

def check_uncached(api_token, all_torrents):
    uncached = []
    batch_size = 20

    # Get list of hashes from torrents
    hashes = [torrent['hash'] for torrent in all_torrents]

    # Split hashes into batches of 20
    for i in range(0, len(hashes), batch_size):
        batch_hashes = hashes[i:i + batch_size]

        # Construct URL with multiple hashes
        hash_path = '/'.join(batch_hashes)
        url = f"https://api.real-debrid.com/rest/1.0/torrents/instantAvailability/{hash_path}"

        # Make API request
        headers = {"Authorization": f"Bearer {api_token}"}
        response = requests.get(url, headers=headers)
        availability_data = response.json()

        # Process each hash in the response
        for torrent_hash in batch_hashes:
            is_available = (
                isinstance(availability_data, dict) and
                torrent_hash in availability_data and
                isinstance(availability_data[torrent_hash], dict) and
                'rd' in availability_data[torrent_hash] and
                isinstance(availability_data[torrent_hash]['rd'], list) and
                len(availability_data[torrent_hash]['rd']) > 0
            )

            if not is_available:
                # Find the corresponding torrent info
                torrent_info = next(t for t in all_torrents if t['hash'] == torrent_hash)
                uncached.append(torrent_info)

        # Add a small delay between batches to be safe
        time.sleep(1)

    return uncached

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
        input("Press Enter to Exit...")
        return
    
    api_token = token_data.get('token')
    if not api_token:
        print("Invalid token data. Please run the main script to set up your token.")
        input("Press Enter to Exit...")
        return
    
     # Get list of torrents with required information
    all_torrents = get_torrent_list(api_token)
    
    if not all_torrents:
        print("No torrents found in your library.")
        input("Press Enter to go to Options Menu...")
        return

    # Check for uncached torrents
    uncached_torrents = check_uncached(api_token, all_torrents)

    if not uncached_torrents:
        print("\nNo uncached torrents found. Going to Options Menu...")
        time.sleep(2)
        return
    else:
        print("\nUncached Torrents found:")
        for torrent in uncached_torrents:
            print(f"- {torrent['filename']}")
        input("\nPress Enter to go to Options Menu...")
        return

if __name__ == "__main__":
    main()
