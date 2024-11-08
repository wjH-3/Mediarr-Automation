from imdb import IMDb
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from PTT import Parser, add_defaults
import regex
from PTT.transformers import (boolean)
from RTN import title_match
import sys
import time
import psutil
import os
import RD
import torrentLibrary
import pyperclip
import re

# Check if 'user' and 'profile' variables exist in sys.argv
def get_user_profile():
    if len(sys.argv) >= 3:
        return sys.argv[1], sys.argv[2]
    else:
        print("Error: Missing arguments for user and profile.")
        input("Press Enter to Exit...")
        return

# Check if browser window(s) open
def browser_open(browser='chrome'):
    for process in psutil.process_iter(['name']):
        if browser in process.info['name'].lower():
            return True
    return False

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

# Return DMM url using IMDb ID found
def get_url(media_type, imdb_id, tv_query=None):
    base_movie_url = "https://debridmediamanager.com/movie/tt"
    base_tv_url = "https://debridmediamanager.com/show/tt"
    
    if media_type == 'M':
        return f"{base_movie_url}{imdb_id}"
    else:
        return f"{base_tv_url}{imdb_id}/{tv_query}"

# Web automation for scraping and interacting with search results
def automate_webpage(url, media_type, user, profile, keywords, imdb_title, tv_query=None):
    # URL info
    print(f"Scraping from -> '{url}'...")

    # Suppress TensorFlow logs
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

    # Set up WebDriver (assuming Chrome)
    # Path to your Chrome user profile (can be modified) (change 'user' to your own user name)
    chrome_profile_path = f"C:/Users/{user}/AppData/Local/Google/Chrome/User Data"

    # Set Chrome options to use the existing profile
    chrome_options = Options()
    chrome_options.add_argument(f"user-data-dir={chrome_profile_path}")  # Path to user data directory
    chrome_options.add_argument(f"profile-directory={profile}")  # Specify profile directory (e.g., 'Profile 1' if you use a custom profile) (can be modified)

    # Reduce Selenium logging
    chrome_options.add_argument('--log-level=3')  # Only show fatal errors
    chrome_options.add_argument('--silent')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

    # Redirect WebDriver logs to devnull
    service = Service(ChromeDriverManager().install(), log_path=os.devnull)

    # Start ChromeDriver using the profile and service
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:      
        # Minimize window
        driver.minimize_window()

        # Open the URL
        driver.get(url)

        # Wait for the page to load
        time.sleep(5)

        releases = driver.find_elements(By.CSS_SELECTOR, "#__next > div > div.mx-2.my-1.overflow-x-auto.grid.grid-cols-1.sm\\:grid-cols-2.md\:grid-cols-3.lg\\:grid-cols-4.xl\\:grid-cols-6.gap-4")
        if not releases:
            input("\nNo releases found for this title. Press Enter to terminate the script and browser window...\n")
            return
        
        # Initialize parser and add default handlers
        parser = Parser()
        add_defaults(parser)
        parser.add_handler("trash", regex.compile(r"\b(\w+rip|hc|((h[dq]|clean)(.+)?)?cam.?(rip|rp)?|(h[dq])?(ts|tc)(?:\d{3,4})?|tele(sync|cine)?|\d+[0o]+([mg]b)|\d{3,4}tc)\b"), boolean, {"remove": False})
        
        # Define search patterns
        search_patterns = [
            r"remux ^(?!.*(?:hdr|dv|dovi|upscale|upscaling|upscaled|[\u0400-\u04FF])).*(?:1080p|1080i).*$",
            r"2160p ^(?!.*\b(?:hdr|dv|dovi|upscale|upscaling|upscaled|[\u0400-\u04FF])\b).*\b(?:web[-\s]?dl)\b.*$" if media_type == 'M' else r"web ^(?!.*(?:hdr|dv|dovi|upscale|upscaling|upscaled|[\u0400-\u04FF])).*(?:1080p|2160p).*$",
            r"^(?!.*(?:hdr|dv|dovi|upscale|upscaling|upscaled|[\u0400-\u04FF])).*\b(?:1080p|2160p)\b.*(?:web|blu(?:ray|-ray|\sray)).*$"
        ]

        for search_text in search_patterns:
            try:
                search_filter = driver.find_element(By.CSS_SELECTOR, "#query")
                search_filter.clear()  # Clear any existing text
                search_filter.send_keys(search_text)
                search_filter.send_keys(Keys.RETURN)

            except NoSuchElementException:
            # If search filter is not found, print an error message
                input(f"\nError: '{url}' is not a valid URL. Press Enter to terminate the script and browser window...\n")
                return
    
            # Detect for "Show Uncached" button to appear (indicating all files parsed)
            def detect_uncached(driver, xpath1, xpath2):
                while True:
                    try:
                        element1 = driver.find_element(By.XPATH, xpath1)
                        return element1
                    except NoSuchElementException:
                        pass
                    try:
                        element2 = driver.find_element(By.XPATH, xpath2)
                        return element2
                    except NoSuchElementException:
                        pass
                    time.sleep(3)  # Wait for 3 seconds before trying again

            # Wait indefinitely for the specific element to be present
            movie_target_element_xpath = "//*[@id='__next']/div/div[2]/div[3]/button[2]"
            tv_target_element_xpath = "//*[@id='__next']/div/div[2]/div[4]/button"
            detect_uncached(driver, movie_target_element_xpath, tv_target_element_xpath)

            # Scrape all file names and their file sizes (generalized selector)
            file_name_elements = driver.find_elements(By.CSS_SELECTOR, "#__next > div > div.mx-2.my-1.overflow-x-auto.grid.grid-cols-1.sm\\:grid-cols-2.md\\:grid-cols-3.lg\\:grid-cols-4.xl\\:grid-cols-6.gap-4 > div > div > h2")
            file_size_elements = driver.find_elements(By.XPATH, "//*[@id='__next']/div/div[4]/div/div/div[1]")
            button_elements = driver.find_elements(By.XPATH, "//*[@id='__next']/div/div[4]/div/div/div[2]/button[1]")

            if not file_name_elements:
                continue

# --------------------------------------------------------

            # Get the text from each file name element and button
            file_names = [element.text for element in file_name_elements]
            file_sizes = [' '.join(element.text.split(';')[0].strip().split()[1:]) for element in file_size_elements]
            file_quantity = [element.text.split('(')[-1].split()[0] for element in file_size_elements]
            button_texts = [element.text for element in button_elements]
            library_url = 'https://debridmediamanager.com/library'

            #if not file_names:
                #time.sleep(0.5)
                #print("\nNo matching files found with the given search filters. Trying the next...\n")
                #continue

            # Check if any files are already in the library
            files_in_library = any(button_text == "RD (100%)" for button_text in button_texts)

            # Create a list of available files (not already in library)
            available_files = []
            files_in_library = []
            for idx, (file_name, file_size, button_text, qty) in enumerate(zip(file_names, file_sizes, button_texts, file_quantity), start=1):
                if media_type == 'T':  # For TV Shows
                    if qty != "1" and button_text != "RD (100%)":
                        available_files.append((idx, file_name, file_size))
                    elif button_text == "RD (100%)":
                        files_in_library.append((file_name, file_size))
                    
                elif media_type == 'M':  # For Movies
                    if button_text != "RD (100%)":
                        available_files.append((idx, file_name, file_size))
                    elif button_text == "RD (100%)":
                        files_in_library.append((file_name, file_size))

            filtered_files = []

            for idx, file_name, file_size in available_files:
                result = parser.parse(file_name)

                # Check for 'trash' and 'upscaled' fields and apply filters
                is_trash = result.get('trash', False)
                is_upscaled = result.get('upscaled', False)
                
                # Append the file if it's neither trash nor upscaled
                if not is_trash and not is_upscaled:
                    title = result.get('title')

                    # Perform title matching
                    match = title_match(imdb_title, title)

                    # If no title match, skip this file
                    if not match:
                        continue

                    filtered_files.append((idx, file_name, file_size))

            if filtered_files:
                break
            else:
                print(f"No matching files found after filtering. Trying next regex...")
        
        if not filtered_files and not files_in_library:
            input("\nNo matching files found with any given regex filters. Press Enter to terminate the script and browser window...\n")
            return

        # Print available files with new numbering
        print("\nMatching files found:")
        for file_name, file_size in files_in_library:
            print(f"✓ {file_name} - {file_size} (Already in Library)")
        for new_idx, (_, file_name, file_size) in enumerate(filtered_files, start=1):
            print(f"{new_idx}. {file_name} - {file_size}")

        if files_in_library:
            print("One or more matching file(s) found are already in the library.")
            while True:
                user_choice = input("Do you want to get the matching files from the library? [Y/N]: ").strip().upper()
                if user_choice == 'Y':
                    driver.quit()
                    print("Getting relevant torrent file(s)...")

                    # Go to torrentLibrary
                    pyperclip.copy(keywords)
                    torrentLibrary.main(auto_paste=True)

                    return
                elif user_choice == 'N':
                    break
                else:
                    print("Invalid input. Please enter 'Y' for yes or 'N' for no.")

        # Define regex patterns for good TV and Movie release groups at the end of the file name
        tv_release_groups = r"(BLURANiUM|FraMeSToR|PmP|decibeL|EPSiLON|HiFi|KRaLiMaRKo|playBD|PTer|SiCFoI|TRiToN|Chotab|CtrlHD|DON|EbP|NTb|SA89|sbR|ABBiE|AJP69|APEX|PAXA|PEXA|XEPA|CasStudio|CRFW|FLUX|HONE|KiNGS|Kitsune|monkee|NOSiViD|NTG|QOQ|RTN|SiC|T6D|TOMMY|ViSUM|3cTWeB|BLUTONiUM|BTW|Cinefeel|CiT|CMRG|Coo7|dB|DEEP|END|ETHiCS|FC|Flights|GNOME|iJP|iKA|iT00NZ|JETIX|KHN|KiMCHI|LAZY|MiU|MZABI|NPMS|NYH|orbitron|PHOENiX|playWEB|PSiG|ROCCaT|RTFM|SbR|SDCC|SIGMA|SMURF|SPiRiT|TEPES|TVSmash|WELP|XEBEC|4KBEC|CEBEX|DRACULA|NINJACENTRAL|SLiGNOME|SwAgLaNdEr|T4H|ViSiON|DEFLATE|INFLATE)(?=(\.(mkv|mp4|avi|mov|flv|wmv|webm))?$)"
        movie_release_groups = r"(3L|BiZKiT|BLURANiUM|CiNEPHiLES|FraMeSToR|PmP|ZQ|Flights|NCmt|playBD|SiCFoI|SURFINBIRD|TEPES|decibeL|EPSiLON|HiFi|iFT|KRaLiMaRKo|NTb|PTP|SumVision|TOA|TRiToN|CtrlHD|MainFrame|DON|W4NK3R|HQMUX|BHDStudio|hallowed|HONE|PTer|SPHD|WEBDV|BBQ|c0kE|Chotab|CRiSC|D-Z0N3|Dariush|EbP|EDPH|Geek|LolHD|TayTO|TDD|TnP|VietHD|EA|HiDt|HiSD|QOQ|SA89|sbR|LoRD|playHD|ABBIE|AJP69|APEX|PAXA|PEXA|XEPA|BLUTONiUM|CMRG|CRFW|CRUD|FLUX|GNOME|KiNGS|Kitsune|NOSiViD|NTG|SiC|dB|MiU|monkee|MZABI|PHOENiX|playWEB|SbR|SMURF|TOMMY|XEBEC|4KBEC|CEBEX)(?=(\.(mkv|mp4|avi|mov|flv|wmv|webm))?$)"

        selected_file_name = None
        
        # Convert the regex patterns into lists to maintain priority order
        tv_groups_list = ['BLURANiUM', 'FraMeSToR', 'PmP', 'decibeL', 'EPSiLON', 'HiFi', 'KRaLiMaRKo', 'playBD', 'PTer', 'SiCFoI', 'TRiToN', 'Chotab', 'CtrlHD', 'DON', 'EbP', 'NTb', 'SA89', 'sbR', 'ABBiE', 'AJP69', 'APEX', 'PAXA', 'PEXA', 'XEPA', 'CasStudio', 'CRFW', 'FLUX', 'HONE', 'KiNGS', 'Kitsune', 'monkee', 'NOSiViD', 'NTG', 'QOQ', 'RTN', 'SiC', 'T6D', 'TOMMY', 'ViSUM', '3cTWeB', 'BLUTONiUM', 'BTW', 'Cinefeel', 'CiT', 'CMRG', 'Coo7', 'dB', 'DEEP', 'END', 'ETHiCS', 'FC', 'Flights', 'GNOME', 'iJP', 'iKA', 'iT00NZ', 'JETIX', 'KHN', 'KiMCHI', 'LAZY', 'MiU', 'MZABI', 'NPMS', 'NYH', 'orbitron', 'PHOENiX', 'playWEB', 'PSiG', 'ROCCaT', 'RTFM', 'SbR', 'SDCC', 'SIGMA', 'SMURF', 'SPiRiT', 'TEPES', 'TVSmash', 'WELP', 'XEBEC', '4KBEC', 'CEBEX', 'DRACULA', 'NINJACENTRAL', 'SLiGNOME', 'SwAgLaNdEr', 'T4H', 'ViSiON', 'DEFLATE', 'INFLATE']
        movie_groups_list = ['3L', 'BiZKiT', 'BLURANiUM', 'CiNEPHiLES', 'FraMeSToR', 'PmP', 'ZQ', 'Flights', 'NCmt', 'playBD', 'SiCFoI', 'SURFINBIRD', 'TEPES', 'decibeL', 'EPSiLON', 'HiFi', 'iFT', 'KRaLiMaRKo', 'NTb', 'PTP', 'SumVision', 'TOA', 'TRiToN', 'CtrlHD', 'MainFrame', 'DON', 'W4NK3R', 'HQMUX', 'BHDStudio', 'hallowed', 'HONE', 'PTer', 'SPHD', 'WEBDV', 'BBQ', 'c0kE', 'Chotab', 'CRiSC', 'D-Z0N3', 'Dariush', 'EbP', 'EDPH', 'Geek', 'LolHD', 'TayTO', 'TDD', 'TnP', 'VietHD', 'EA', 'HiDt', 'HiSD', 'QOQ', 'SA89', 'sbR', 'LoRD', 'playHD', 'ABBIE', 'AJP69', 'APEX', 'PAXA', 'PEXA', 'XEPA', 'BLUTONiUM', 'CMRG', 'CRFW', 'CRUD', 'FLUX', 'GNOME', 'KiNGS', 'Kitsune', 'NOSiViD', 'NTG', 'SiC', 'dB', 'MiU', 'monkee', 'MZABI', 'PHOENiX', 'playWEB', 'SbR', 'SMURF', 'TOMMY', 'XEBEC', '4KBEC', 'CEBEX']

        # Track the best match found
        best_match = {
            'priority': float('inf'),  # Initialize with highest possible number
            'original_idx': None,
            'file_name': None,
            'file_element_idx': None
        }

        # Find file with highest priority release group
        for idx, (original_idx, file_name, file_size) in enumerate(filtered_files):
            if media_type == 'T':
                # Check for TV release groups
                for priority, group in enumerate(tv_groups_list):
                    if re.search(f"{group}(?=(\.(mkv|mp4|avi|mov|flv|wmv|webm))?$)", file_name):
                        if priority < best_match['priority']:
                            best_match = {
                                'priority': priority,
                                'original_idx': original_idx,
                                'file_name': file_name,
                                'file_element_idx': original_idx - 1
                            }
                        break
            elif media_type == 'M':
                # Check for Movie release groups
                for priority, group in enumerate(movie_groups_list):
                    if re.search(f"{group}(?=(\.(mkv|mp4|avi|mov|flv|wmv|webm))?$)", file_name):
                        if priority < best_match['priority']:
                            best_match = {
                                'priority': priority,
                                'original_idx': original_idx,
                                'file_name': file_name,
                                'file_element_idx': original_idx - 1
                            }
                        break

        # If we found a match, use it
        if best_match['file_name'] is not None:
            selected_file_index = best_match['file_element_idx']
            selected_file_element = file_name_elements[selected_file_index]
            selected_file_name = best_match['file_name']
            print(f"Good Release found: '{selected_file_name}'")
            print("Auto-selecting...")

        if selected_file_name is None:
            # Manual selection      
            while True:
                try:
                    # Get user to input a number to choose the corresponding file
                    selected_num = int(input("Type in the NUMBER corresponding to the file you want: "))
                    
                    if 1 <= selected_num <= len(filtered_files):
                        selected_file_index = filtered_files[selected_num - 1][0] - 1  # Get the original index
                        selected_file_element = file_name_elements[selected_file_index]
                        selected_file_name = file_names[selected_file_index]  # Store the selected file name
                        break
                    else:
                        print(f"Please enter a number between 1 and {len(filtered_files)}.")
                
                except ValueError:
                    # Handle case where the input is not an integer
                    print("Invalid input. Please enter a number only.")
        
        print("\nGetting file, please wait...")

        # Locate the corresponding button for the selected file (within the same section)
        focus_button = selected_file_element.find_element(By.XPATH, "./following-sibling::div[contains(@class, 'space-x-2')]/button[4]")

        # Click the button corresponding to the selected file
        focus_button.click()

        # Detect for "Succesfully added" message to appear (indicating file added to library)
        def detect_successful(driver, xpath):
            while True:
                try:
                    element = driver.find_element(By.XPATH, xpath)
                    return element
                except NoSuchElementException:
                    time.sleep(1)  # Wait for 1 second before trying again

        # Wait indefinitely for the specific element to be present
        target_element_xpath = "//*[@id='__next']/div/div[1]/div/div/div[2]"
        detect_successful(driver, target_element_xpath)

        print(f"Magnet Link for '{selected_file_name}' copied successfully.")
        
        driver.quit()

        RD.main(auto_paste=True)

    except WebDriverException:
        print(f"\nError: '{url}' could not be reached. The script will now terminate...")
        input("Press Enter to Exit...")
        return
    except Exception as e:
        print(f"\nAn unexpected error occurred. Details:\n{str(e)}")
        input("Press Enter to Exit...")
        return

def main():
    user, profile = get_user_profile()

    input("\nReminder: Make sure you are logged into Real-Debrid (real-debrid.com) and Debrid Media Manager (debridmediamanager.com).\nPress Enter to continue...\n")

    if browser_open():
        print("Warning: Browser window detected. Please close all browser windows before continuing.")
        input("Press Enter to continue...\n")

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
        url = get_url(media_type, imdb_id, tv_query)
        automate_webpage(url, media_type, user, profile, keywords, imdb_title, tv_query)

if __name__ == "__main__":
    main()
