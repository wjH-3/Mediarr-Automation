# Using Anilist API for anime queries by title
# Using SeaDex (releases.moe) for Finished Airing shows
# Using SubsPlease / Erai-raws for Airing shows

import requests # pip install requests
from bs4 import BeautifulSoup # pip install beautifulsoup4
import pyperclip # pip install pyperclip

def search_anilist(anime_title):
    # GraphQL query with pagination (Page)
    query = '''
    query ($search: String) {
        Page {
            media (search: $search, type: ANIME) {
                id
                title {
                    romaji
                    english
                }
            }
        }
    }
    '''
    
    # Variables for the GraphQL query
    variables = {
        'search': anime_title
    }
    
    # Make the HTTP API request
    response = requests.post('https://graphql.anilist.co', json={'query': query, 'variables': variables})
    
    if response.status_code == 200:
        data = response.json()
        if data['data']['Page']['media']:
            animes = data['data']['Page']['media']
            results = []
            for anime in animes:
                results.append({
                    'id': anime['id'],
                    'title_romaji': anime['title']['romaji'],
                    'title_english': anime['title']['english']
                })
            return results
    return None

def get_anime_status(anime_id):
    # GraphQL query to get the status of a specific anime by its ID
    query = '''
    query ($id: Int) {
        Media (id: $id, type: ANIME) {
            id
            title {
                romaji
                english
            }
            status
        }
    }
    '''
    
    # Variables for the GraphQL query
    variables = {
        'id': anime_id
    }
    
    # Make the HTTP API request
    response = requests.post('https://graphql.anilist.co', json={'query': query, 'variables': variables})
    
    if response.status_code == 200:
        data = response.json()
        if data['data']['Media']:
            anime = data['data']['Media']
            return {
                'id': anime['id'],
                'title_romaji': anime['title']['romaji'],
                'title_english': anime['title']['english'],
                'status': anime['status']
            }
    return None

# Mapping for status descriptions
status_map = {
    'FINISHED': 'Finished Airing',
    'RELEASING': 'Currently Airing',
    'NOT_YET_RELEASED': 'Not Yet Released',
    'CANCELLED': 'Cancelled',
    'HIATUS': 'On Hiatus'
}

# Example api calls:
# https://releases.moe/api/collections/entries/records?expand=trs&filter=alID=166216
# https://releases.moe/api/collections/entries/records?filter=alID=166216
# https://releases.moe/api/collections/torrents/records/wehqjgww9ch7odq
def get_url(anime_id, anime_status, title_romaji):
    # Alternative source for 'subsplease' is currently 'erai-raws'.
    # If returning further errors, change to any other release group of choice
    subsplease_base_url = "https://nyaa.land/user/subsplease?f=0&c=1_2&q={}+1080p&o=desc&p=1"
    seadex_base_url = "https://releases.moe/"
    subsplease_batch_base_url = "https://nyaa.land/user/subsplease?f=0&c=1_2&q={}+1080p+batch&o=desc&p=1"
    seadex_api_url = "https://releases.moe/api/collections/entries/records?expand=trs&filter=alID={}"

    def custom_quote(s):
        return s.replace(" ", "+").replace("!", "")

    if anime_status == 'FINISHED':
        # Check SeaDex API for entry
        api_response = requests.get(seadex_api_url.format(anime_id))
        if api_response.status_code == 200:
            data = api_response.json()
            if data['totalItems'] > 0:
                # SeaDex entry exists
                notes = data['items'][0]['notes']
                print("\nHere are the Seadex best releases:\n")
                print(f"(Source: {seadex_base_url}{anime_id})")
                if notes == "":
                    print ("Notes:\nN/A\n")
                else:
                    print (f"Notes:\n{notes}\n")
                # Collect unique release groups with "Nyaa" tracker
                release_groups = []
                for item in data['items'][0]['trs']:
                    for tr in data['items'][0]['expand']['trs']:
                        if tr['id'] == item and tr['tracker'] == "Nyaa":
                            release_groups.append(tr['releaseGroup'])

                if not release_groups:
                    print("Error: No Nyaa source found for the release(s). Checking for SubsPlease releases...")
                    formatted_title = custom_quote(title_romaji)
                    return subsplease_batch_base_url.format(formatted_title)

                # Print release groups in a numbered list
                print("Release Groups (w/ Nyaa source):")
                for i, release_group in enumerate(release_groups, 1):
                    print(f"{i}. {release_group}")

                while True:
                    try:
                        # Prompt user for input
                        choice = int(input("Enter the number of the desired release group: "))

                        if 1 <= choice <= len(release_groups):
                            release_group = release_groups[choice - 1]
                            break
                        else:
                            print(f"Please enter a number between 1 and {len(release_groups)}.")
                    except ValueError:
                        # Handle case of when input is not integer
                        print("Invalid input. Please enter a number only.")

                # Find and print the corresponding URL
                for item in data['items'][0]['trs']:
                    for tr in data['items'][0]['expand']['trs']:
                        if tr['id'] == item and tr['tracker'] == "Nyaa" and tr['releaseGroup'] == list(release_groups)[choice - 1]:
                            original_url = tr['url']
                            new_url = original_url.replace(".si/", ".land/")
                            return f"{new_url}"
                
        # If no SeaDex entry or API call failed, fall back to SubsPlease batch
        print("\nNo SeaDex entry, checking for SubsPlease releases...")
        formatted_title = custom_quote(title_romaji)
        return subsplease_batch_base_url.format(formatted_title)

    elif anime_status == 'RELEASING':
        print("\nChecking for SubsPlease releases...")
        formatted_title = custom_quote(title_romaji)
        return subsplease_base_url.format(formatted_title)

    elif anime_status == 'NOT_YET_RELEASED':
        print(f"\nThe show '{title_romaji}' has not been released yet.")
        return None
    
    elif anime_status == 'CANCELLED':
        print(f"\nThe show '{title_romaji}' has been cancelled.")

    else:
        print(f"\nUnknown anime status: {anime_status}")
        return None
    
def get_magnet(url):
    # Determine the type of URL
    if "/view/" in url:
        return scrape_specific_file(url)
    else:
        return scrape_file_list(url)
    
def scrape_specific_file(url):
    # Fetch the webpage
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the magnet link
    magnet_link = soup.find('a', href=lambda x: x and x.startswith('magnet:'))
    
    if magnet_link:
        print(f"\nMagnet Link: {magnet_link['href']}")
        return magnet_link['href']
    else:
        print("\nNo magnet link found on this page.")
        return None

def scrape_file_list(url):
    def fetch_and_parse(url):
        response = requests.get(url)
        return BeautifulSoup(response.text, 'html.parser')

    def extract_files(soup):
        table = soup.find('table')
        if not table:
            return None

        files = []
        rows = table.find_all('tr')
        for row in rows[1:]:  # Skip header row
            name_column = row.find('td', colspan="2")
            if name_column:
                filename_link = name_column.find('a', class_=lambda x: x != 'comments')
                if filename_link:
                    name = filename_link.text.strip()
                    magnet_icon = row.find('i', class_='fa-magnet')
                    if magnet_icon and magnet_icon.parent.name == 'a':
                        link = magnet_icon.parent['href']
                        files.append((name, link))
        return files

    def display_and_select(files, source):
        if not files:
            print(f"\nNo files with magnet links found for {source}.")
            return None

        print(f"\nMatching files from {source}:")
        for i, (name, _) in enumerate(files, 1):
            print(f"{i}. {name}")

        while True:
            if source == 'SubsPlease':
                choice = input("\nEnter the number of the file you want to select, or 'c' to check alternate source: ")
                if choice.lower() == 'c':
                    return 'check_others'
            else:
                choice = input("\nEnter the number of the file you want to select: ")
            
            try:
                choice = int(choice)
                if 1 <= choice <= len(files):
                    selected_file, selected_link = files[choice - 1]
                    print(f"\nYou selected: {selected_file}")
                    print(f"\nMagnet Link: {selected_link}")
                    return selected_link
                else:
                    print(f"Invalid number. Please enter a number between 1 and {len(files)}.")
            except ValueError:
                print("Invalid input. Please enter a number only.")

    # Try with the original URL (subsplease)
    soup = fetch_and_parse(url)
    subsplease_files = extract_files(soup)

    # If no results from SubsPlease
    if not subsplease_files:
        print(f"\nNo files with magnet links found for SubsPlease.")
        result = 'check_others'  # Simulate checking others as no files found

    # If files found from SubsPlease
    else:
        result = display_and_select(subsplease_files, 'SubsPlease')

    # If result is 'check_others' or no files found from SubsPlease
    if result == 'check_others':
        print("\nChecking alternative source...")
        alternative_url = url.replace('subsplease', 'erai-raws').replace('+batch', '')  # Change alt. source here
        soup = fetch_and_parse(alternative_url)
        erai_raws_files = extract_files(soup)

        return display_and_select(erai_raws_files, 'Erai-raws')  # Change alt. source here
    else:
        return result  # Return the magnet link if selected from SubsPlease

def main():
    # Usage
    anime_title = input("Enter Anime: ")
    results = search_anilist(anime_title)

    if results:
        # Display results in a numbered list
        print("\nSearch results:\n")
        for i, result in enumerate(results, start=1):
            print(f"{i}. AniList URL: https://anilist.co/anime/{result['id']}")
            print(f"   Title (Romaji): {result['title_romaji']}")
            print(f"   Title (English): {result['title_english']}")
            print("\n---\n")
        
        while True:
            try:
                # Prompt user to select a result
                selection = int(input("Enter the number of the anime you want to select: ")) - 1
                
                if 0 <= selection < len(results):
                    selected_anime = results[selection]
                    print(f"You selected: '{selected_anime['title_romaji']}' (AniList ID: {selected_anime['id']})")

                    # Fetch status of the selected anime
                    anime_status = get_anime_status(selected_anime['id'])
                    if anime_status:
                        status_description = status_map.get(anime_status['status'], "Unknown status")
                        print(f"'{anime_status['title_romaji']}' status: {status_description}.")
                        
                        # Get the URL based on the anime status
                        url = get_url(selected_anime['id'], anime_status['status'], selected_anime['title_romaji'])
                        if url:
                            # Not printing out Nyaa url
                            # print(f"Nyaa URL: {url}")
                            magnet_link = get_magnet(url)
                            if magnet_link:
                                while True:
                                    copy_input = input("Do you want to copy the magnet link? [Y/N]: ").strip().upper()
                                    if copy_input == 'Y':
                                        pyperclip.copy(magnet_link)
                                        print("Magnet link successfully copied to clipboard.")
                                        input("\nPress Enter to terminate the script...")
                                        break
                                    if copy_input == 'N':
                                        input("\nPress Enter to terminate the script...")
                                        break
                                    else:
                                        print("Invalid input. Please enter 'Y' for yes or 'N' for no.")
                        else:
                            print("Could not generate a URL for this anime.")
                    else:
                        print("Could not retrieve the anime's status.")
                    break
                else:
                    print("Invalid selection.")
            except ValueError:
                print("Invalid selection. Please enter a number.")
    else:
        print("No results found.")

if __name__ == "__main__":
    main()
