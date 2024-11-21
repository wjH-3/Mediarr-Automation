import requests
import json
from typing import List, Dict, Any
import re
import os
import sys
import pyperclip

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

    def delete_torrent(self, torrent_id: str) -> None:
        response = requests.delete(f"{self.base_url}/torrents/delete/{torrent_id}", headers=self.headers)
        if response.status_code == 204:
            print("Torrent successfully deleted.")
            input("\nPress Enter to Exit...")
            return

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
            return input("\nInput Movie/TV Show to Delete: ").strip()

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
                        user_input = input("\nEnter a number to select torrent, or 'q' to quit: ")
                        if user_input == 'q':
                            return
                        choice = int(user_input)
                        if 1 <= choice <= len(matching_torrents):
                            break
                        print("Invalid choice. Please try again.")
                    except ValueError:
                        print("Please enter a valid number.")
                
                selected_torrent = matching_torrents[choice - 1]
            
            while True:
                confirm = input(f"\nAre you sure you want to delete '{selected_torrent['filename']}'? [Y/N]: ").strip().upper()
                if confirm == 'Y':
                    # Delete selected torrent using its id
                    self.delete_torrent(selected_torrent['id'])
                if confirm == 'N':
                    input("Press Enter to Exit...")
                    return
                else:
                    print("Please enter 'Y' for yes or 'N' for no.")

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
