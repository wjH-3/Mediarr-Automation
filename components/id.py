from imdb import IMDb
import pytvmaze


def get_movie_id(keywords):
    ia = IMDb()
    search_results = ia.search_movie(keywords)
    
    if search_results:
        movie = search_results[0]
        return movie.getID(), movie['title']
    else:
        return None

def get_tv_id(keywords):
    ia = IMDb()
    search_results = ia.search_movie(keywords)  # Note: This also works for TV series
    
    if search_results:
        for result in search_results:
            if result.get('kind') in ['tv series', 'tv mini series']:
                imdb_id = result.getID()
                print(imdb_id)
                tvm = pytvmaze.TVMaze()
                show = tvm.get_show(imdb_id=f'tt{imdb_id}')
                is_airing = show.status.lower() == 'running'
                return result.getID(), result['title'], is_airing
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
        if media_type == 'M':
            imdb_id, title = result
            print(f"\nIMDb data for '{keywords}' - ID: '{imdb_id}', Title: '{title}'")
        else:
            imdb_id, title, is_airing = result
            airing_status = "Airing" if is_airing else "Finished"
            print(f"\nIMDb data for '{keywords}' - ID: '{imdb_id}', Title: '{title}, Status: {airing_status}'")
            
    else:
        print(f"\nNo IMDb ID found for '{keywords}'.")

if __name__ == "__main__":
    main()