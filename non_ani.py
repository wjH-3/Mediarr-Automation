from imdb import IMDb
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, WebDriverException
import sys
import time
import psutil
import os
import RD
import torrentLibrary
import pyperclip

# Check if 'user' and 'profile' variables exist in sys.argv
def get_user_profile():
    if len(sys.argv) >= 3:
        return sys.argv[1], sys.argv[2]
    else:
        print("Error: Missing arguments for user and profile")
        sys.exit(1)

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
            return movie.getID(), keywords
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
                    return result.getID(), keywords
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
def automate_webpage(url, media_type, user, profile, keywords, tv_query=None):
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
            input("\nNo releases found for this title. Press Enter to terminate the script and browser window...")
            return

        # Define search patterns
        search_patterns = [
            "remux ^(?!.*(?:hdr|dv|dovi)).*(?:1080p|1080i).*$",
            "web-dl ^(?!.*(?:hdr|dv|dovi)).*(?:2160p).*$" if media_type == 'M' else "web ^(?!.*(?:hdr|dv|dovi)).*(?:1080p|2160p).*$",
            "1080p ^(?!.*(?:hdr|dv|dovi)).*(?:web|bluray|blu-ray).*$"
        ]

        for search_text in search_patterns:
            try:
                search_filter = driver.find_element(By.CSS_SELECTOR, "#query")
                search_filter.clear()  # Clear any existing text
                search_filter.send_keys(search_text)
                search_filter.send_keys(Keys.RETURN)

            except NoSuchElementException:
            # If search filter is not found, print an error message
                print(f"\nError: '{url}' is not a valid URL. The script will now terminate...")
                sys.exit(1)
    
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

            if file_name_elements:
                break

# --------------------------------------------------------

        # Get the text from each file name element and button
        file_names = [element.text for element in file_name_elements]
        file_sizes = [' '.join(element.text.split(';')[0].strip().split()[1:]) for element in file_size_elements]
        file_quantity = [element.text.split('(')[-1].split()[0] for element in file_size_elements]
        button_texts = [element.text for element in button_elements]
        library_url = 'https://debridmediamanager.com/library'

        if not file_names:
            input("\nNo matching files found with the given search filters. Press Enter to terminate the script and browser window...")
            return

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

        # Print available files with new numbering
        print("\nMatching files found:")
        for file_name, file_size in files_in_library:
            print(f"✓ {file_name} - {file_size} (Already in Library)")
        for new_idx, (_, file_name, file_size) in enumerate(available_files, start=1):
            print(f"{new_idx}. {file_name} - {file_size}")

        # Check if there are any available files
        if not available_files:
            print("All matching files found are already in the library.")
            user_choice = input(f"Do you want to get the matching files from the library? [Y/N]: ").strip().upper()
            while True:
                if user_choice == 'Y':
                    driver.quit()
                    print("Getting relevant torrent file(s)...")

                    # Go to torrentLibrary
                    pyperclip.copy(keywords)
                    torrentLibrary.main(auto_paste=True)

                    continue
                elif user_choice == 'N':
                    input("\nPress Enter to terminate the script and browser window...")
                    return
                else:
                    print("Invalid input. Please enter 'Y' for yes or 'N' for no.")
        
        if files_in_library:
            print("One or more matching file(s) found are already in the library.")
            user_choice = input("Do you want to get the matching files from the library? [Y/N]: ").strip().upper()
            while True:
                if user_choice == 'Y':
                    driver.quit()
                    print("Getting relevant torrent file(s)...")

                    # Go to torrentLibrary
                    pyperclip.copy(keywords)
                    torrentLibrary.main(auto_paste=True)

                    continue
                elif user_choice == 'N':
                    break
                else:
                    print("Invalid input. Please enter 'Y' for yes or 'N' for no.")

        while True:
            try:
                # Get user to input a number to choose the corresponding file
                selected_num = int(input("Type in the NUMBER corresponding to the file you want: "))
                
                if 1 <= selected_num <= len(available_files):
                    selected_file_index = available_files[selected_num - 1][0] - 1  # Get the original index
                    selected_file_element = file_name_elements[selected_file_index]
                    break
                else:
                    print(f"Please enter a number between 1 and {len(available_files)}.")
            
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

        print(f"Magnet Link for '{file_names[selected_num - 1]}' copied successfully.")

        driver.quit()

    except WebDriverException:
        print(f"\nError: '{url}' could not be reached. The script will now terminate...")
        sys.exit(1)
    except Exception as e:
        print(f"\nAn unexpected error occurred. Details:\n{str(e)}")

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
        imdb_id, keywords = get_movie_id()
        tv_query = None

    elif media_type =='T':
        imdb_id, keywords = get_tv_id()

        while True:
            tv_query = input("What season of the show are you looking for? Enter the season number - ")
            if tv_query.isdigit():
                break
            else:
                print("Invalid input. Please enter a digit.")
    
    print("\nScraping files, please wait...")

    time.sleep(3)

    if imdb_id:
        url = get_url(media_type, imdb_id, tv_query)
        automate_webpage(url, media_type, user, profile, keywords, tv_query)
        RD.main(auto_paste=True)

if __name__ == "__main__":
    main()
