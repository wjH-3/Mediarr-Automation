from imdb import IMDb
import requests
from PTT import Parser, add_defaults
import regex
from PTT.transformers import (boolean)
from RTN import title_match
import sys
import time
import os
import RD
import torrentLibrary
import pyperclip
import re
from dmm_api import key_manager
from typing import List, Tuple, Dict, Optional, Any
import json
import pytvmaze
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# IMDb search functions
# IMDb ID for movies
def get_movie_id():
    ia = IMDb()

    while True:
        keywords = input("Enter title + year (e.g Inception 2010): ")
        search_results = ia.search_movie(keywords)
    
        if search_results:
            movie = search_results[0]
            return movie.getID(), keywords, movie['title']
        else:
            print(f"Error: Unable to find the movie '{keywords}'. Make sure both the title and year are correct.")

# IMDb ID for TV
def get_tv_id():
    ia = IMDb()

    while True:
        keywords = input("Enter title + year (e.g Stranger Things 2016): ")
        search_results = ia.search_movie(keywords)  # Note: This also works for TV series
    
        if search_results:
            for result in search_results:
                if result.get('kind') in ['tv series', 'tv mini series']:
                    imdb_id = result.getID()
                    tvm = pytvmaze.TVMaze()
                    show = tvm.get_show(imdb_id=f'tt{imdb_id}')
                    is_airing = show.status.lower() == 'running'
                    return result.getID(), keywords, result['title'], is_airing
        else:
            print(f"Error: Unable to find the show '{keywords}'. Make sure both the title and year are correct.")

available_files = []
filtered_files = []

# Filter parameters and regex
def filter_files(available_files: List[Tuple[str, str, float]], imdb_title: str, parser) -> List[Tuple[str, str, float]]:
    
    # Compile the custom regex pattern once, outside the loop
    custom_pattern = re.compile(
        r"^(?=.*(?:remux|web|blu(?:ray|-ray|\sray)))"  # Must contain remux, web, or bluray variants
        r"(?=.*(?:2160p|1080p|1080i))"                 # Must contain one of these resolutions
        r"(?!.*(?:hdr|dv|dovi|upscale|upscaling|upscaled|[\u0400-\u04FF]))"  # No HDR & DV
        # r"(?!.*(?:upscale|upscaling|upscaled|[\u0400-\u04FF]))" # With HDR & DV
        r".*$",
        re.IGNORECASE  # Make it case insensitive
    )

    for magnet_hash, file_name, file_size in available_files:
        # SKip over None values
        if magnet_hash is None or file_name is None:
            continue

        # First apply custom regex filter
        if not custom_pattern.match(file_name):
            continue

        # Initialize parser and add default handlers
        parser.add_handler(
            "trash",
            regex.compile(r"\b(\w+rip|hc|((h[dq]|clean)(.+)?)?cam.?(rip|rp)?|(h[dq])?(ts|tc)(?:\d{3,4})?|tele(sync|cine)?|\d+[0o]+([mg]b)|\d{3,4}tc)\b"),
            boolean,
            {"remove": False}
        )
        
        # Parse the filename with the parser
        result = parser.parse(file_name)

        # Check for 'trash' and 'upscaled' fields
        if result.get('trash', False) or result.get('upscaled', False):
            continue

        # Get title from parser result
        title = result.get('title')
        
        # If no title or no title match, skip this file
        if not title or not title_match(imdb_title, title):
            continue

        # If we got here, the file passed all filters
        filtered_files.append((magnet_hash, file_name, file_size))

    return filtered_files

# Scraping DMM API
def scrape_api(imdb_id, media_type, keywords, imdb_title, tv_query=None):
    page_num = 0
    max_pages = 8

    while page_num < max_pages:
        # Get a fresh key-hash pair for this request
        key, solution_hash = key_manager.get_new_key_hash()
        
        if not key or not solution_hash:
            print("Failed to get key-hash pair")
            break

        # Construct the appropriate API endpoint
        if media_type == 'M':
            api_url = f"https://debridmediamanager.com/api/torrents/movie?imdbId=tt{imdb_id}&dmmProblemKey={key}&solution={solution_hash}&onlyTrusted=false&maxSize=0&page={page_num}"
        else:  # media_type == 'T'
            api_url = f"https://debridmediamanager.com/api/torrents/tv?imdbId=tt{imdb_id}&seasonNum={tv_query}&dmmProblemKey={key}&solution={solution_hash}&onlyTrusted=false&maxSize=0&page={page_num}"

        # Make the API request
        api_response = requests.get(api_url)

        if api_response.status_code != 200:
            print(f"Error accessing page {page_num}: Status code {api_response.status_code}")
            break

        data = api_response.json()
        
        # Check if results are empty (end of available pages)
        if not data.get('results') or data['results'] == []:
            print(f"No more results after {page_num} pages")
            break

        # Process the results
        for item in data['results']:
            magnet_hash = item['hash']
            file_name = item['title']
            file_size = item['fileSize']
            available_files.append((magnet_hash, file_name, file_size))

        #print(f"Successfully scraped page {page_num}")
        page_num += 1

    #print("\nAvailable files: ")
    print(f"Number of available files: {len(available_files)}")
    #print(available_files)

    # Apply filters to the collected files
    parser = Parser()  # Create parser instance
    add_defaults(parser)  # Add default handlers
    filtered_files = filter_files(available_files, imdb_title, parser)
    #print("\nFiltered files: ")
    print(f"Number of filtered files: {len(filtered_files)}")
    #print(filtered_files)
    
    return filtered_files

instant_RD = []

def check_instant_RD(api_token, filtered_files, verify_threshold=2):
    """
    Check Real-Debrid availability with multiple verifications for consistency
    
    Args:
        api_token: Real-Debrid API token
        filtered_files: List of tuples (magnet_hash, file_name, file_size)
        verify_threshold: Number of positive checks required to consider a file available
    
    Returns:
        List of available files in instant_RD
    """
    # Create session with retry logic
    session = create_session(max_retries=3, backoff_factor=0.5)
    
    # Convert filtered_files to a dictionary for easy lookup
    files_dict = {magnet_hash: (file_name, file_size) 
                 for magnet_hash, file_name, file_size in filtered_files}
    
    # Track availability counts for each hash
    availability_counts = {}
    batch_size = 20
    
    # Multiple verification rounds
    for round in range(verify_threshold):
        try:
            available_hashes = check_batch(session, api_token, list(files_dict.keys()), batch_size)
            
            # Update counts
            for hash in available_hashes:
                availability_counts[hash] = availability_counts.get(hash, 0) + 1
                
            # Add small delay between rounds to help avoid cache issues
            if round < verify_threshold - 1:
                time.sleep(2)
                
        except Exception as e:
            print(f"Error in verification round {round + 1}: {str(e)}")
            continue
    
    # Clear existing instant_RD list
    instant_RD.clear()
    
    # Add files that meet the threshold
    for magnet_hash, count in availability_counts.items():
        if count >= verify_threshold:
            file_name, file_size = files_dict[magnet_hash]
            instant_RD.append((magnet_hash, file_name, file_size))
    
    # Remove duplicates by normalized file name
    remove_duplicates()
    
    print(f"Number of instantly available files: {len(instant_RD)}")
    return instant_RD

def create_session(max_retries, backoff_factor):
    """Create a session with retry logic"""
    session = requests.Session()
    
    # Configure retry strategy
    retry_strategy = Retry(
        total=max_retries,
        backoff_factor=backoff_factor,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

def check_batch(session, api_token, hashes, batch_size):
    """Check availability for a batch of hashes"""
    available_hashes = set()
    
    for i in range(0, len(hashes), batch_size):
        batch_hashes = hashes[i:i + batch_size]
        hash_path = '/'.join(batch_hashes)
        url = f"https://api.real-debrid.com/rest/1.0/torrents/instantAvailability/{hash_path}"
        
        headers = {
            "Authorization": f"Bearer {api_token}",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }
        
        try:
            response = session.get(url, headers=headers)
            response.raise_for_status()
            availability_data = response.json()
            
            for magnet_hash in batch_hashes:
                if is_hash_available(availability_data, magnet_hash):
                    available_hashes.add(magnet_hash)
            
            time.sleep(1)  # Delay between batches
            
        except Exception as e:
            print(f"Error checking batch: {str(e)}")
            continue
            
    return available_hashes

def is_hash_available(availability_data, magnet_hash):
    """Check if a specific hash is available in the response data"""
    return (
        isinstance(availability_data, dict) and
        magnet_hash in availability_data and
        isinstance(availability_data[magnet_hash], dict) and
        'rd' in availability_data[magnet_hash] and
        isinstance(availability_data[magnet_hash]['rd'], list) and
        len(availability_data[magnet_hash]['rd']) > 0
    )

def normalize_file_name(file_name):
    """Normalize file name for comparison"""
    return re.sub(r'[.\s-]+', '', file_name).lower()

def remove_duplicates():
    """Remove duplicates from instant_RD based on normalized file names"""
    seen_normalized_names = set()
    global instant_RD
    instant_RD[:] = [
        item for item in instant_RD 
        if normalize_file_name(item[1]) not in seen_normalized_names 
        and not seen_normalized_names.add(normalize_file_name(item[1]))
    ]

all_torrents = []

def get_torrent_list(api_token):
    page = 1
    has_more_pages = True
    url = "https://api.real-debrid.com/rest/1.0/torrents"
    headers = {"Authorization": f"Bearer {api_token}"}

    print("\nChecking if there are matching torrents already in the torrent library...")
    print("Fetching torrent library...")

    while has_more_pages:
        response = requests.get(
            url,
            params={'page': page},
            headers=headers
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
            page += 1

    print(f"Total number of torrents: {len(all_torrents)}")
    return all_torrents

files_in_library = []

def matching_torrents(api_token, instant_RD, all_torrents):
    # Get torrents from library
    if not all_torrents:
        all_torrents = get_torrent_list(api_token)
        # If torrent library is empty, break from this function
        if not all_torrents:
            print("No files found in library.")
            return False
        
    # Regular expression to match any video file extensions and brackets at the end of a filename
    pattern = re.compile(r'(?:\[.*?\])?\.?(avi|mkv|mp4|mov|wmv|flv|webm|m4v|mpeg|mpg)?(?:\[.*?\])?$', re.IGNORECASE)

    def strip_extension(filename: str) -> str:
        """Remove video file extension if present."""
        return pattern.sub('', filename)

    # Check each torrent in `all_torrents` against `instant_RD`
    for torrent in all_torrents:
        extract_filename = strip_extension(torrent['filename'])
        for idx, (magnet_hash, file_name, file_size) in enumerate(instant_RD):
            cleaned_file_name = strip_extension(file_name)
            if cleaned_file_name == extract_filename:  # Match found
                files_in_library.append(torrent['filename'])
                del instant_RD[idx] # Remove the matching torrent
                break  # Move to the next torrent once a match is found

    # If matches are found, prompt user for action
    if files_in_library:
        print("\nMatching torrent(s) found in the torrent library:")
        for idx, file in enumerate(files_in_library, start=1):
            print(f"{idx}. {file}")
        
        # Prompt user to choose action
        while True: 
            user_choice = input("Do you want to get a matching torrent from the library instead? [Y/N]: ").strip().upper()   
            if user_choice == 'Y':
                # If only one match, use it automatically
                if len(files_in_library) == 1:
                    chosen_file = files_in_library[0]
                else:
                    while True:
                        try:
                            # Allow user to select specific file if there are multiple
                            choice_num = int(input("Enter the number corresponding to the torrent you want: "))
                            if 1 <= choice_num <= len(files_in_library):
                                chosen_file = files_in_library[choice_num - 1]
                                break
                            else:
                                print(f"Please enter a number between 1 and {len(files_in_library)}.")
                        except ValueError:
                            print("Invalid input. Please enter a number.")

                # Copy the chosen file name and run the torrent library function
                pyperclip.copy(chosen_file)
                torrentLibrary.main(auto_paste=True)
                return True
            elif user_choice == 'N':
                print("Getting instantly available torrents...")
                break
            else:
                print("Please enter 'Y' for yes or 'N' for no.")
    else:
        print("No matching torrents found in the torrent library. Getting instantly available torrents...") 

# ----------------------------------------------

def get_file(instant_RD, media_type, is_airing=None):    
    episode_pattern = r"""
        (?:
            [Ss](?:\d{1,2}|\d{4})[\s._-]*[Ee](?:\d{1,3})|
            (?:season|series)[\s._-]*\d{1,2}[\s._-]*(?:episode|ep)[\s._-]*\d{1,3}|
            [Ss](?:\d{1,2}|\d{4})[\s._-]*(?:ep|episode)[\s._-]*\d{1,3}|
            (?:episode|ep)[\s._-]*\d{1,3}
        )
    """

    single_episode_regex = re.compile(episode_pattern, re.IGNORECASE | re.VERBOSE)
    
    # Base quality patterns
    base_quality_patterns = {
        # 'uhd_remux': r'^(?=.*\b(?:2160p|UHD|4K)\b)(?=.*remux).*$',
        'fhd_remux': r'^(?=.*\b(?:1080p|1080i)\b)(?=.*remux).*$',
        # 'uhd_web': r'^(?=.*\b(?:web[-\s]?dl)\b)(?=.*2160p).*$' if media_type == 'M' else r'^(?=.*2160p)(?=.*web).*$',
        'web': r'^(?=.*\b(?:web[-\s]?dl)\b)(?=.*2160p).*$' if media_type == 'M' else r'^(?=.*\b(?:1080p|2160p)\b)(?=.*web).*$',
        'uhd_fhd_web_&_bluray': r'^(?=.*(?:web|blu(?:ray|-ray|\sray)))(?=.*\b(?:2160p|1080p)\b).*$',
        'others': r'.*'  # Catch-all pattern
    }

    # Convert the regex patterns into lists to maintain priority order
    tv_release_groups = ['BLURANiUM', 'FraMeSToR', 'PmP', 'decibeL', 'EPSiLON', 'HiFi', 'KRaLiMaRKo', 'playBD', 'PTer', 'SiCFoI', 'TRiToN', 'Chotab', 'CtrlHD', 'DON', 'EbP', 'NTb', 'SA89', 'sbR', 'ABBiE', 'AJP69', 'APEX', 'PAXA', 'PEXA', 'XEPA', 'CasStudio', 'CRFW', 'FLUX', 'HONE', 'KiNGS', 'Kitsune', 'monkee', 'NOSiViD', 'NTG', 'QOQ', 'RTN', 'SiC', 'T6D', 'TOMMY', 'ViSUM', '3cTWeB', 'BLUTONiUM', 'BTW', 'Cinefeel', 'CiT', 'CMRG', 'Coo7', 'dB', 'DEEP', 'END', 'ETHiCS', 'FC', 'Flights', 'GNOME', 'iJP', 'iKA', 'iT00NZ', 'JETIX', 'KHN', 'KiMCHI', 'LAZY', 'MiU', 'MZABI', 'NPMS', 'NYH', 'orbitron', 'PHOENiX', 'playWEB', 'PSiG', 'ROCCaT', 'RTFM', 'SbR', 'SDCC', 'SIGMA', 'SMURF', 'SPiRiT', 'TEPES', 'TVSmash', 'WELP', 'XEBEC', '4KBEC', 'CEBEX', 'DRACULA', 'NINJACENTRAL', 'SLiGNOME', 'SwAgLaNdEr', 'T4H', 'ViSiON', 'DEFLATE', 'INFLATE']
    movie_release_groups = ['3L', 'BiZKiT', 'BLURANiUM', 'CiNEPHiLES', 'FraMeSToR', 'PmP', 'ZQ', 'Flights', 'NCmt', 'playBD', 'SiCFoI', 'SURFINBIRD', 'TEPES', 'decibeL', 'EPSiLON', 'HiFi', 'iFT', 'KRaLiMaRKo', 'NTb', 'PTP', 'SumVision', 'TOA', 'TRiToN', 'CtrlHD', 'MainFrame', 'DON', 'W4NK3R', 'HQMUX', 'BHDStudio', 'hallowed', 'HONE', 'PTer', 'SPHD', 'WEBDV', 'BBQ', 'c0kE', 'Chotab', 'CRiSC', 'D-Z0N3', 'Dariush', 'EbP', 'EDPH', 'Geek', 'LolHD', 'TayTO', 'TDD', 'TnP', 'VietHD', 'EA', 'HiDt', 'HiSD', 'QOQ', 'SA89', 'sbR', 'LoRD', 'playHD', 'ABBIE', 'AJP69', 'APEX', 'PAXA', 'PEXA', 'XEPA', 'BLUTONiUM', 'CMRG', 'CRFW', 'CRUD', 'FLUX', 'GNOME', 'KiNGS', 'Kitsune', 'NOSiViD', 'NTG', 'SiC', 'dB', 'MiU', 'monkee', 'MZABI', 'PHOENiX', 'playWEB', 'SbR', 'SMURF', 'TOMMY', 'XEBEC', '4KBEC', 'CEBEX']

    # Function to find best release group match in a file list
    def find_best_match(files: List[Tuple[str, str, float]]) -> Optional[Tuple[str, str, float]]:
        release_groups = tv_release_groups if media_type == 'T' else movie_release_groups
        best_match = None
        best_priority = float('inf')
        
        for file_tuple in files:
            file_name = file_tuple[1]
            for priority, group in enumerate(release_groups):
                if re.search(rf"(?:-|\s){group}(?=(?:(?:\[[^\]]+\])?(?:\.(?:mkv|mp4|avi|mov|flv|wmv|webm))?|(?:\.(?:mkv|mp4|avi|mov|flv|wmv|webm))?(?:\[[^\]]+\])?)?$)", file_name):
                    if priority < best_priority:
                        best_priority = priority
                        best_match = file_tuple
                    break
        return best_match

     # Initialize quality groups
    quality_groups: Dict[str, List[Tuple[str, str, float]]] = {
        name: [] for name in base_quality_patterns
    }

    is_full_season = None  # Initialize the variable
    
    for file_tuple in instant_RD:
        magnet_hash, file_name, file_size = file_tuple
        
        # For TV shows that finished airing, we want full seasons
        if media_type == 'T' and is_airing is False:
            # If it contains episode pattern, skip it
            if single_episode_regex.search(file_name):
                continue
            is_full_season = 'S'  # Set to full season mode
                
        # For currently airing shows, ask user preference
        elif media_type == 'T' and is_airing is True:
            if is_full_season is None:  # Only ask once
                while True:
                    user_choice = input("\nFull Seasons or Single Episodes files? [S/E]: ")
                    if user_choice.upper() == 'S':
                        is_full_season = 'S'
                        break
                    elif user_choice.upper() == 'E':
                        is_full_season = 'E'
                        break
                    else:
                        print("Please input 'S' or 'E'.")
            
            # Apply the filter based on user choice
            if is_full_season == 'S' and single_episode_regex.search(file_name):
                continue
            elif is_full_season == 'E' and not single_episode_regex.search(file_name):
                continue
        
        # Categorize into quality groups (maintaining priority order)
        for group_name, pattern in base_quality_patterns.items():
            if re.search(pattern, file_name, re.IGNORECASE):
                quality_groups[group_name].append(file_tuple)
                break

    # Remove empty groups
    group_names = [name for name, files in quality_groups.items() if files]

    if not group_names:
        print("No files found in any quality group.")
        return None

    current_group_index = 0
    while True:
        if not (0 <= current_group_index < len(group_names)):
            current_group_index = 0

        current_group = group_names[current_group_index]
        files = quality_groups[current_group]
        
        print(f"\n=== {current_group.upper().replace('_', ' ')} ===")
        
        if media_type == 'T' and is_full_season == 'E':
            # Separate files into good releases and others
            good_releases = []
            other_releases = []
            
            for file_tuple in files:
                file_name = file_tuple[1]
                is_good_release = False
                for group in tv_release_groups:
                    if re.search(rf"(?:-|\s){group}(?=(?:(?:\[[^\]]+\])?(?:\.(?:mkv|mp4|avi|mov|flv|wmv|webm))?|(?:\.(?:mkv|mp4|avi|mov|flv|wmv|webm))?(?:\[[^\]]+\])?)?$)", file_name):
                        good_releases.append(file_tuple)
                        is_good_release = True
                        break
                if not is_good_release:
                    other_releases.append(file_tuple)
            
            # Display files already in the library
            if files_in_library:
                print("Files in library:")
                for file in files_in_library:
                    print(f"- {file}")

                print("-" * 40)  # Separator

            # Display good releases
            if good_releases:
                print("Good release groups:")
                for idx, (_, file_name, file_size) in enumerate(good_releases, 1):
                    file_size_gb = file_size/1000
                    print(f"{idx}. {file_name} - {file_size_gb:.2f}GB")
                
                print("-" * 40)  # Separator
            
            # Display other releases
            start_idx = len(good_releases) + 1
            for idx, (_, file_name, file_size) in enumerate(other_releases, start_idx):
                file_size_gb = file_size/1000
                print(f"{idx}. {file_name} - {file_size_gb:.2f}GB")
            
            # Combine lists for selection
            files = good_releases + other_releases
        else:
            # For full seasons or movies, use best match logic
            best_match = find_best_match(files)

            # Display files already in the library
            if files_in_library:
                print("Files in library:")
                for file in files_in_library:
                    print(f"- {file}")
                    
                print("-" * 40)  # Separator

            for idx, (_, file_name, file_size) in enumerate(files, 1):
                file_size_gb = file_size/1000
                print(f"{idx}. {file_name} - {file_size_gb:.2f}GB")
            
            if best_match:
                print(f"\nBest Release found: '{best_match[1]}'")
                while True:
                    auto_select = input("Do you want to auto-select the Nest Release? [Y/N]: ").strip().upper()
                    if auto_select == 'Y':
                        print("Auto-selecting...")
                        return best_match[0]
                    if auto_select == 'N':
                        break
                    else:
                        print("Please enter 'Y' for yes or 'N' for no.")

        # Get user input
        user_input = input("\nEnter number to select file, 'c' to cycle groups, or 'q' to quit: ").lower()
        
        if user_input == 'q':
            return None
        elif user_input == 'c':
            current_group_index += 1
            continue
        
        try:
            selection = int(user_input)
            if 1 <= selection <= len(files):
                selected_file = files[selection - 1]
                return selected_file[0]  # Return magnet hash
            else:
                print(f"Please enter a number between 1 and {len(files)}")
        except ValueError:
            print("Invalid input. Please enter a number, 'c' to cycle, or 'q' to quit.")

# ------------------------

def main():
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
    
    # List of all initialized lists
    list_of_lists = [available_files, filtered_files, instant_RD, all_torrents, files_in_library]
    for lst in list_of_lists:
        lst.clear() # Clear all lists before proceeding

    while True:
        media_type = input("\nMovie or TV? [M/T]: ").strip().upper()
        
        if media_type in ['M', 'T']:
            break  # Exit the loop if the input is valid
        else:
            print("Invalid input. Please enter 'M' for movie or 'T' for TV.")
    
    if media_type == 'M':
        imdb_id, keywords, imdb_title = get_movie_id()
        tv_query = None
        is_airing = None
        print(f"\nIMDb Data for '{keywords}' - ID: '{imdb_id}', Title: '{imdb_title}'")

    elif media_type =='T':
        imdb_id, keywords, imdb_title, is_airing = get_tv_id()
        airing_status = "Airing" if is_airing else "Finished"

        while True:
            tv_query = input("What season of the show are you looking for? Enter the season number - ")
            if tv_query.isdigit():
                break
            else:
                print("Invalid input. Please enter a digit.")
        print(f"\nIMDb Data for '{keywords}' - ID: '{imdb_id}', Title: '{imdb_title}', Status: {airing_status}'")
    
    print("\nScraping files, please wait...\n")

    if imdb_id:
        scrape_api(imdb_id, media_type, keywords, imdb_title, tv_query)
        check_instant_RD(api_token, filtered_files)
        if matching_torrents(api_token, instant_RD, all_torrents):
            return
        magnet_hash = get_file(instant_RD, media_type, is_airing)
        if magnet_hash:
            magnet_link = f"magnet:?xt=urn:btih:{magnet_hash}"
            pyperclip.copy(magnet_link)
            print(f"Magnet link: '{magnet_link}' generated and copied to clipboard successfully.")
            RD.main(auto_paste=True)

if __name__ == "__main__":
    main()
