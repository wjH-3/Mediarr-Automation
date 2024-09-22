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
            if result.get('kind') in ['tv series', 'tv mini series']:
                return result.getID()
    return None

def main():
    media_type = input("Movie or TV? [M/T]: ").strip().upper()
    
    if media_type not in ['M', 'T']:
        print("Invalid input. Please enter 'M' for movie or 'T' for TV.")
        return

    keywords = input("Enter title + year (e.g Inception 2010 or Stranger Things 2016): ")
    
    if media_type == 'M':
        result = get_movie_id(keywords)
    else:
        result = get_tv_id(keywords)

    if result:
        print(f"\nIMDb ID for '{keywords}': tt{result}")
    else:
        print(f"\nNo IMDb ID found for '{keywords}'.")

if __name__ == "__main__":
    main()