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


def get_anime_info(anime_name):
    anilist = Anilist()

    try:
        # Get the anime ID directly
        anime_id = anilist.get_anime_id(anime_name)
        
        if anime_id:
            # Get detailed anime information
            anime_info = anilist.get_anime(anime_name)
            return anime_id, anime_info.get('name_english'), anime_info.get('name_romaji')
        else:
            return None, None, None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None, None

def seadex_url(anime_id):
    base_url = "https://releases.moe/"

    if anime_id:
        return f"{base_url}{anime_id}"

def subsplease_url(name_romaji):
    base_url = "https://subsplease.org/shows/"

    if name_romaji:
        # (WIP) find results corresponding to search query (romaji anime title) and output their links (using Find in Page)
        return
    
def main():
    while True:
        anime_name = input("Enter anime title (Eng or Romaji): ")
        anime_id, name_english, name_romaji = get_anime_info(anime_name)

        if anime_id is not None:
            print(f"Anilist ID: {anime_id}")
            print(f"Full English Title: '{name_english or 'Not available'}'")
            print(f"Full Romaji Title: '{name_romaji or 'Not available'}'")
            break
        else:
            print("Could not find the anime. Please try again.")

if __name__ == "__main__":
    main()

