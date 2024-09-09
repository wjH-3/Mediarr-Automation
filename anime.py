# using SeaDex (releases.moe) for Finished Airing shows
# using SubsPlease (subsplease.org) for Airing shows
from AnilistPython import Anilist

# APIs that can be used: 
# MAL - pip install mal-api --> from mal import AnimeSearch
# AniList - pip install anilistpython --> https://github.com/ReZeroE/AnilistPython

def get_anilist_id():
    anilist = Anilist()

    while True:
        anime_title = input("Enter title (Eng or Romaji): ")

        # Search for the anime
        try:
            anime_dict = anilist.get_anime(anime_title)
            if anime_dict:
                anime_id = anime_dict['id']
                eng_title = anime_dict.get('name_english', 'N/A')
                romaji_title = anime_dict.get('name_romaji', 'N/A')
                
                print(f"Anime found!")
                print(f"Eng Title: {eng_title}")
                print(f"Romaji Title: {romaji_title}")
                print(f"ID: {anime_id}")
                
                return anime_id
            else:
                print(f"Error: Unable to find '{anime_title}'. Make sure the title is correct.")
        except Exception as e:
            print(f"An error occurred: {e}")
            print("Please try again with a different title.")


def main():
    media_type = input("Movie or TV? [M/T]: ").strip().upper()


    # Seadex:
    base_url = "https://releases.moe/"



