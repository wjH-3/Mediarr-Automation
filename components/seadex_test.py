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

def get_url(anime_id, anime_status, title_romaji):
    seadex_base_url = "https://releases.moe/"
    subsplease_batch_base_url = "https://nyaa.land/user/subsplease?f=0&c=1_2&q={}+1080p+batch&o=desc&p=1"
    seadex_api_url = "https://releases.moe/api/collections/entries/records?expand=trs&filter=alID={}"

    def custom_quote(s):
        return s.replace(" ", "+")

    if anime_status == 'FINISHED':
        # Check SeaDex API for entry
        api_response = requests.get(seadex_api_url.format(anime_id))
        if api_response.status_code == 200:
            data = api_response.json()
            if data['totalItems'] > 0:
                # SeaDex entry exists
                notes = data['items'][0]['notes']
                print("Here are the Seadex best releases:\n")
                print (f"{notes}\n")
                # Collect unique release groups with "Nyaa" tracker
                release_groups = set()
                for item in data['items'][0]['trs']:
                    for tr in data['items'][0]['expand']['trs']:
                        if tr['id'] == item and tr['tracker'] == "Nyaa":
                            release_groups.add(tr['releaseGroup'])

                # Print release groups in a numbered list
                print("Available release groups:")
                for i, release_group in enumerate(release_groups, 1):
                    print(f"{i}. {release_group}")

                # Prompt user for input
                choice = int(input("Enter the number of the desired release group: "))

                # Find and print the corresponding URL
                for item in data['items'][0]['trs']:
                    for tr in data['items'][0]['expand']['trs']:
                        if tr['id'] == item and tr['tracker'] == "Nyaa" and tr['releaseGroup'] == list(release_groups)[choice - 1]:
                            print(f"URL: {tr['url']}")
        
        # If no SeaDex entry or API call failed, fall back to SubsPlease batch
        formatted_title = custom_quote(title_romaji)
        return subsplease_batch_base_url.format(formatted_title)

    else:
        print(f"Anime is not Finished Airing")
        return None

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
                        
                        # Get the URL based on the anime status
                        get_url(selected_anime['id'], anime_status['status'], selected_anime['title_romaji'])
                        #if url:
                            # print(f"URL generated: {url}")
                            # !!! continue with function to get magnet link HERE !!!
                    else:
                        print("Could not generate a URL for this anime.")
                    #else:
                        #print("Could not retrieve the anime's status.")
                    break
                else:
                    print("Invalid selection.")
            except ValueError:
                print("Invalid selection. Please enter a number.")
    else:
        print("No results found")

if __name__ == "__main__":
    main()