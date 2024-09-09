# using SeaDex (releases.moe) for Finished Airing shows
# using SubsPlease (subsplease.org) for Airing shows
from AnilistPython import Anilist
import sys

# APIs that can be used: 
# MAL - pip install mal-api --> from mal import AnimeSearch
# AniList - pip install anilistpython --> https://github.com/ReZeroE/AnilistPython

# Other resources for reference:
# nyaascraper: https://github.com/zaini/nyaascraper
# miru: https://github.com/ThaUnknown/miru
# nyaapy: https://github.com/JuanjoSalvador/NyaaPy
# nyaadownloader: https://github.com/marcpinet/nyaadownloader


import requests

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

def main():
    # Usage
    anime_title = input("Enter title: ")
    results = search_anilist(anime_title)


    if results:
        # Display results in a numbered list
        print("\nSearch results:")
        for i, result in enumerate(results, start=1):
            print(f"{i}. AniList ID: {result['id']}")
            print(f"   Title (Romaji): {result['title_romaji']}")
            print(f"   Title (English): {result['title_english']}")
            print("---")
        
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
                    else:
                        print("Could not retrieve the anime's status.")
                    break
                    # You can perform further actions on the selected anime here
                else:
                    print("Invalid selection.")
            except ValueError:
                print("Invalid selection. Please enter a number.")
    else:
        print("No results found")

if __name__ == "__main__":
    main()
