from imdb import IMDb
import requests
from bs4 import BeautifulSoup
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
from typing import List, Tuple, Dict, Optional
import json


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
                    return result.getID(), keywords, result['title']
        else:
            print(f"Error: Unable to find the show '{keywords}'. Make sure both the title and year are correct.")


# Scraping DMM API
available_files = []
filtered_files = []

def filter_files(available_files: List[Tuple[str, str, float]], imdb_title: str, parser) -> List[Tuple[str, str, float]]:
    
    # Compile the custom regex pattern once, outside the loop
    custom_pattern = re.compile(
        r"^(?=.*(?:remux|web|blu(?:ray|-ray|\sray)))"  # Must contain remux, web, or bluray variants
        r"(?=.*(?:2160p|1080p|1080i))"                 # Must contain one of these resolutions
        r"(?!.*(?:hdr|dv|dovi|upscale|upscaling|upscaled|[\u0400-\u04FF]))"  # Must not contain these terms
        r".*$",
        re.IGNORECASE  # Make it case insensitive
    )

    for magnet_hash, file_name, file_size in available_files:
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
            print(f"\nNo more results after {page_num} pages")
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
    print(f"\nNumber of available files: {len(available_files)}")
    #print(available_files)

    # Apply filters to the collected files
    parser = Parser()  # Create parser instance
    add_defaults(parser)  # Add default handlers
    filtered_files = filter_files(available_files, imdb_title, parser)
    #print("\nFiltered files: ")
    print(f"\nNumber of filtered files: {len(filtered_files)}")
    #print(filtered_files)
    
    return filtered_files

instant_RD = []

def check_instant_RD(api_token, filtered_files, media_type):
    batch_size = 20
    
    # Convert filtered_files to a dictionary for easy lookup
    files_dict = {magnet_hash: (file_name, file_size) 
                 for magnet_hash, file_name, file_size in filtered_files}
    
    # Split hashes into batches of 20
    hashes = list(files_dict.keys())
    for i in range(0, len(hashes), batch_size):
        batch_hashes = hashes[i:i + batch_size]
        
        # Construct URL with multiple hashes
        hash_path = '/'.join(batch_hashes)
        url = f"https://api.real-debrid.com/rest/1.0/torrents/instantAvailability/{hash_path}"
        
        # Make API request
        headers = {"Authorization": f"Bearer {api_token}"}
        response = requests.get(url, headers=headers)
        availability_data = response.json()
        
        # Process each hash in the response
        for magnet_hash in batch_hashes:
            if media_type == 'M':
                is_available = (
                    isinstance(availability_data, dict) and
                    magnet_hash in availability_data and
                    isinstance(availability_data[magnet_hash], dict) and
                    'rd' in availability_data[magnet_hash] and
                    isinstance(availability_data[magnet_hash]['rd'], list) and
                    len(availability_data[magnet_hash]['rd']) > 0
                )
            if media_type == 'T':
                is_available = (
                    isinstance(availability_data, dict) and
                    magnet_hash in availability_data and
                    isinstance(availability_data[magnet_hash], dict) and
                    'rd' in availability_data[magnet_hash] and
                    isinstance(availability_data[magnet_hash]['rd'], list) and
                    len(availability_data[magnet_hash]['rd']) > 1 # Exclude single episode files
                )
            
            if is_available:
                file_name, file_size = files_dict[magnet_hash]
                instant_RD.append((magnet_hash, file_name, file_size))
        
        # Add a small delay between batches to besafe
        time.sleep(1)

    #print("\nInstantly available files: ")
    print(f"\nNumber of instantly available files: {len(instant_RD)}")
    #print(f"{instant_RD}")

    return instant_RD

# ----------------------------------------------

def get_file(instant_RD, media_type):
    # Quality group regex patterns
    quality_patterns = {
        'fhd_remux': r'^(?=.*\b(?:1080p|1080i)\b)(?=.*remux).*$',
        'uhd_web': r'^(?=.*\b(?:web[-\s]?dl)\b)(?=.*2160p).*$' if media_type == 'M' else r'^(?=.*\b(?:1080p|2160p)\b)(?=.*web).*$',
        'uhd_fhd_web_&_bluray': r'^(?=.*(?:web|blu(?:ray|-ray|\sray)))(?=.*\b(?:2160p|1080p)\b).*$',
        'others': r'.*'  # Catch-all pattern
    }

    # Convert the regex patterns into lists to maintain priority order
    tv_release_groups = ['BLURANiUM', 'FraMeSToR', 'PmP', 'decibeL', 'EPSiLON', 'HiFi', 'KRaLiMaRKo', 'playBD', 'PTer', 'SiCFoI', 'TRiToN', 'Chotab', 'CtrlHD', 'DON', 'EbP', 'NTb', 'SA89', 'sbR', 'ABBiE', 'AJP69', 'APEX', 'PAXA', 'PEXA', 'XEPA', 'CasStudio', 'CRFW', 'FLUX', 'HONE', 'KiNGS', 'Kitsune', 'monkee', 'NOSiViD', 'NTG', 'QOQ', 'RTN', 'SiC', 'T6D', 'TOMMY', 'ViSUM', '3cTWeB', 'BLUTONiUM', 'BTW', 'Cinefeel', 'CiT', 'CMRG', 'Coo7', 'dB', 'DEEP', 'END', 'ETHiCS', 'FC', 'Flights', 'GNOME', 'iJP', 'iKA', 'iT00NZ', 'JETIX', 'KHN', 'KiMCHI', 'LAZY', 'MiU', 'MZABI', 'NPMS', 'NYH', 'orbitron', 'PHOENiX', 'playWEB', 'PSiG', 'ROCCaT', 'RTFM', 'SbR', 'SDCC', 'SIGMA', 'SMURF', 'SPiRiT', 'TEPES', 'TVSmash', 'WELP', 'XEBEC', '4KBEC', 'CEBEX', 'DRACULA', 'NINJACENTRAL', 'SLiGNOME', 'SwAgLaNdEr', 'T4H', 'ViSiON', 'DEFLATE', 'INFLATE']
    movie_release_groups = ['3L', 'BiZKiT', 'BLURANiUM', 'CiNEPHiLES', 'FraMeSToR', 'PmP', 'ZQ', 'Flights', 'NCmt', 'playBD', 'SiCFoI', 'SURFINBIRD', 'TEPES', 'decibeL', 'EPSiLON', 'HiFi', 'iFT', 'KRaLiMaRKo', 'NTb', 'PTP', 'SumVision', 'TOA', 'TRiToN', 'CtrlHD', 'MainFrame', 'DON', 'W4NK3R', 'HQMUX', 'BHDStudio', 'hallowed', 'HONE', 'PTer', 'SPHD', 'WEBDV', 'BBQ', 'c0kE', 'Chotab', 'CRiSC', 'D-Z0N3', 'Dariush', 'EbP', 'EDPH', 'Geek', 'LolHD', 'TayTO', 'TDD', 'TnP', 'VietHD', 'EA', 'HiDt', 'HiSD', 'QOQ', 'SA89', 'sbR', 'LoRD', 'playHD', 'ABBIE', 'AJP69', 'APEX', 'PAXA', 'PEXA', 'XEPA', 'BLUTONiUM', 'CMRG', 'CRFW', 'CRUD', 'FLUX', 'GNOME', 'KiNGS', 'Kitsune', 'NOSiViD', 'NTG', 'SiC', 'dB', 'MiU', 'monkee', 'MZABI', 'PHOENiX', 'playWEB', 'SbR', 'SMURF', 'TOMMY', 'XEBEC', '4KBEC', 'CEBEX']

    # Categorize files into quality groups
    quality_groups: Dict[str, List[Tuple[str, str, float]]] = {
        name: [] for name in quality_patterns
    }

    for file_tuple in instant_RD:
        magnet_hash, file_name, file_size = file_tuple
        # Categorize into first matching quality group
        for group_name, pattern in quality_patterns.items():
            if re.search(pattern, file_name, re.IGNORECASE):
                quality_groups[group_name].append(file_tuple)
                break

    # Function to find best release group match in a file list
    def find_best_match(files: List[Tuple[str, str, float]]) -> Optional[Tuple[str, str, float]]:
        release_groups = tv_release_groups if media_type == 'T' else movie_release_groups
        best_match = None
        best_priority = float('inf')
        
        for file_tuple in files:
            file_name = file_tuple[1]
            for priority, group in enumerate(release_groups):
                if re.search(f"{group}(?=(\.(mkv|mp4|avi|mov|flv|wmv|webm))?$)", file_name):
                    if priority < best_priority:
                        best_priority = priority
                        best_match = file_tuple
                    break
        return best_match

    # Display and selection logic
    current_group_index = 0
    group_names = [name for name, files in quality_groups.items() if files]  # Only groups with files

    if not group_names:
        print("No files found in any quality group.")
        return None

    while True:
        if not (0 <= current_group_index < len(group_names)):
            current_group_index = 0

        current_group = group_names[current_group_index]
        files = quality_groups[current_group]
        
        print(f"\n=== {current_group.upper().replace('_', ' ')} ===")
        
        # Check for best match in current group
        best_match = find_best_match(files)
        
        # Display files
        for idx, (_, file_name, file_size) in enumerate(files, 1):
            file_size_gb = file_size/1000
            print(f"{idx}. {file_name} - {file_size_gb:.2f}GB")
        
        # If there's a best match, auto-select it
        if best_match:
            print(f"\nGood Release found: '{best_match[1]}'")
            print("Auto-selecting...")
            return best_match[0]  # Return magnet hash
        
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


def main():

    #input("\nReminder: Make sure you are logged into Real-Debrid (real-debrid.com) and Debrid Media Manager (debridmediamanager.com).\nPress Enter to continue...\n")

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
    
    while True:
        media_type = input("Movie or TV? [M/T]: ").strip().upper()
        
        if media_type in ['M', 'T']:
            break  # Exit the loop if the input is valid
        else:
            print("Invalid input. Please enter 'M' for movie or 'T' for TV.")
    
    if media_type == 'M':
        imdb_id, keywords, imdb_title = get_movie_id()
        tv_query = None
        print(f"\nIMDb Data for '{keywords}' - ID: '{imdb_id}', Title: '{imdb_title}'")

    elif media_type =='T':
        imdb_id, keywords, imdb_title = get_tv_id()

        while True:
            tv_query = input("What season of the show are you looking for? Enter the season number - ")
            if tv_query.isdigit():
                break
            else:
                print("Invalid input. Please enter a digit.")
        print(f"\nIMDb Data for '{keywords}' - ID: '{imdb_id}', Title: '{imdb_title}'")
    
    print("\nScraping files, please wait...")

    time.sleep(3)

    if imdb_id:
        #url = get_url(media_type, imdb_id, tv_query)
        scrape_api(imdb_id, media_type, keywords, imdb_title, tv_query)
        check_instant_RD(api_token, filtered_files, media_type)
        magnet_hash = get_file(instant_RD, media_type)  # 'M' for movie or 'T' for TV show
        if magnet_hash:
            magnet_link = f"magnet:?xt=urn:btih:{magnet_hash}"
            pyperclip.copy(magnet_link)
            print(f"Magnet link: '{magnet_link}' generated and copied to clipboard successfully.")
            RD.main(auto_paste=True)

if __name__ == "__main__":
    main()
