from imdb import Cinemagoer

def get_movie_id(keywords):
    ia = Cinemagoer()
    search_results = ia.search_movie(keywords)
    
    if search_results:
        movie = search_results[0]
        return movie.getID()
    else:
        return None

def get_tv_id(keywords):
    ia = Cinemagoer()
    search_results = ia.search_movie(keywords)  # Note: This also works for TV series
    
    if search_results:
        for result in search_results:
            if result.get('kind') in ['tv series', 'tv miniseries']:
                return result.getID()
    return None

def get_url(media_type, imdb_id):
    base_movie_url = "https://debridmediamanager.com/movie/tt"
    base_tv_url = "https://debridmediamanager.com/show/tt"
    
    if media_type == 'M':
        return f"{base_movie_url}{imdb_id}"
    else:
        return f"{base_tv_url}{imdb_id}"

def main():
    media_type = input("Movie or TV? [M/T]: ").strip().upper()
    
    if media_type not in ['M', 'T']:
        print("Invalid input. Please enter 'M' for movie or 'T' for TV.")
        return

    keywords = input("Enter title + year (e.g Inception 2010 or Stranger Things 2016): ")
    
    if media_type == 'M':
        imdb_id = get_movie_id(keywords)
    else:
        imdb_id = get_tv_id(keywords)

    if imdb_id:
        url = get_url(media_type, imdb_id)
        print(f"\nURL for '{keywords}': {url}")
    else:
        print(f"\nNo IMDb ID found for '{keywords}'.")

if __name__ == "__main__":
    main()