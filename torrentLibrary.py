import requests
import json
from typing import List, Dict, Any
import re
import os
import sys
import time
import pyperclip
import unrestrict

class RealDebridCLI:
    def __init__(self, api_token: str, auto_paste: bool = False):
        self.api_token = api_token
        self.auto_paste = auto_paste
        self.base_url = "https://api.real-debrid.com/rest/1.0"
        self.headers = {'Authorization': f'Bearer {self.api_token}'}

    def get_torrent_list(self) -> List[Dict[str, Any]]:
        all_torrents = []
        page = 1
        has_more_pages = True

        print("Fetching torrent library...")
        while has_more_pages:
            response = requests.get(
                f"{self.base_url}/torrents",
                params={'page': page},
                headers=self.headers
            )
            
            # Check for 204 No Content, indicating no more torrents
            if response.status_code == 204:
                print("All torrents fetched.")
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
                # print(f"Fetched page {page} ({len(page_data)} torrents)")
                page += 1

        print(f"Total number of torrents: {len(all_torrents)}")
        return all_torrents

    def get_torrent_info(self, torrent_id: str) -> Dict[str, Any]:
        response = requests.get(f"{self.base_url}/torrents/info/{torrent_id}", headers=self.headers)
        response.raise_for_status()
        return response.json()

    def normalize_string(self, s: str) -> str:
        # Convert to lowercase and replace common separators with spaces
        s = re.sub(r'[._-]', ' ', s.lower())
        s = re.sub(r':', ' ', s.lower())  # Replace colons with spaces

        # Split the string into parts to check for title and year
        parts = s.split()
        
        # Check if the string is purely numeric (e.g., the movie "2012")
        if not re.fullmatch(r'\d+', s.strip()):
            # If not purely numeric, look for a year at the end of the string
            if len(parts) > 1 and re.fullmatch(r'\d{4}', parts[-1]):
                # Remove the last part if it's a year (four digits)
                s = ' '.join(parts[:-1])

        # Remove common torrent notation like 1080p, 2160p, S01, E01, etc.
        s = re.sub(r'\b\d{4}p\b|\b[s]\d{2}\b|\b[e]\d{2}\b|\bweb\b|\bh264\b|\bh265\b|\bx264\b|\bx265\b|\bhdr\b|\bsdr\b|\bdl\b|\bbluray\b|\bremux\b|\binternal\b', '', s, flags=re.IGNORECASE)
        
        # Remove release group names in brackets
        s = re.sub(r'\[.*?\]|\(.*?\)', '', s)
        
        # Remove extra whitespace
        s = ' '.join(s.split())
    
        return s

    def search_torrents(self, search_query: str) -> List[Dict[str, Any]]:
        all_torrents = self.get_torrent_list()
        normalized_query = self.normalize_string(search_query)
        query_parts = normalized_query.split()
        
        matching_torrents = []
        for torrent in all_torrents:
            normalized_filename = self.normalize_string(torrent['filename'])
            # Check if all parts of the search query are in the filename
            if all(part in normalized_filename for part in query_parts):
                matching_torrents.append(torrent)
        
        return matching_torrents

    def get_search_query(self) -> str:
        if self.auto_paste:
            return pyperclip.paste()
        else:
            return input("\nInput Movie/TV Show: ").strip()

    def run(self):
        try:
            # Get search input using the new method
            search_query = self.get_search_query()
            print(f"Searching for: {search_query}")
            
            # Search torrents
            matching_torrents = self.search_torrents(search_query)
            
            if not matching_torrents:
                print("No matching torrents found.\n")
                input("Press Enter to Exit...")
                return
            
            # Display matching torrents
            print(f"\nFound {len(matching_torrents)} matching torrent(s):")
            for i, torrent in enumerate(matching_torrents, 1):
                print(f"{i}. {torrent['filename']}")
            
            if len(matching_torrents) == 1:
                print("Only 1 matching torrent found. Auto-selecting...")
                selected_torrent = matching_torrents[0]

            else:   
                # Get user choice for torrent
                while True:
                    try:
                        choice = int(input("\nSelect a torrent (enter number): "))
                        if 1 <= choice <= len(matching_torrents):
                            break
                        print("Invalid choice. Please try again.")
                    except ValueError:
                        print("Please enter a valid number.")
                
                selected_torrent = matching_torrents[choice - 1]
            
            # Get detailed info for selected torrent
            torrent_info = self.get_torrent_info(selected_torrent['id'])
            
            # Filter and match selected files with links
            selected_files = [f for f in torrent_info['files'] if f['selected'] == 1]
            file_link_pairs = list(zip(selected_files, torrent_info['links']))
            
            if len(file_link_pairs) == 1:
                # If there's only one file, print its path and link directly
                print("\nGetting file...")
                selected_file, selected_link = file_link_pairs[0]
                print(f"File: {selected_file['path']}")
                print(f"Link: {selected_link}")
                pyperclip.copy(selected_link)
                print("Link copied, unrestricting link...")
                unrestrict.main(auto_paste=True)
                input("Press Enter to Exit...")
                return
            else:
                # Display available files
                print("\nAvailable files:")
                for i, (file, _) in enumerate(file_link_pairs, 1):
                    print(f"{i}. {file['path']}")
                
                # Get user choice for file
                while True:
                    file_choice = input("Input Number to Choose File or press Enter to Exit: ")

                    if file_choice == "":  # If the user presses Enter without input
                        print("Exiting...\n")
                        time.sleep(1)
                        return
                        
                    try:
                        file_choice=int(file_choice)
                        if 1 <= file_choice <= len(file_link_pairs):
                            # Display selected file and its link
                            selected_file, selected_link = file_link_pairs[file_choice - 1]
                            print("\nSelected file:")
                            print(f"File: {selected_file['path']}")
                            print(f"Link: {selected_link}")
                            pyperclip.copy(selected_link)
                            print("Link copied, unrestricting link...")
                            unrestrict.main(auto_paste=True)
                        else:
                            print("Invalid choice. Please try again.")
                    except ValueError:
                        print("Please enter a valid number.")                
                
        except requests.RequestException as e:
            print(f"API Error: {e}")
            input("Press Enter to Exit...")
            return
        except Exception as e:
            print(f"An error occurred: {e}")
            input("Press Enter to Exit...")
            return

def main(auto_paste: bool = False):
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
    cli = RealDebridCLI(api_token, auto_paste)
    cli.run()
    return

if __name__ == "__main__":
    main()