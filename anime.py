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
            
            if 0 <= selection < len(results) and selection.isdigit():
                selected_anime = results[selection]
                print(f"You selected: '{selected_anime['title_romaji']}' (AniList ID: {selected_anime['id']})")
                break
                # You can perform further actions on the selected anime here
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid selection. Please enter a number.")
else:
    print("No results found")
