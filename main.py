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

# IMDb search functions
# IMDb ID for movies
def get_movie_id():
    ia = IMDb()

    while True:
        keywords = input("Enter title + year (e.g Inception 2010): ")
        search_results = ia.search_movie(keywords)
    
        if search_results:
            movie = search_results[0]
            return movie.getID()
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
                    return result.getID()
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
def automate_webpage(url, search_text, media_type):
    # Set up WebDriver (assuming Chrome)
    
    # Path to your Chrome user profile (can be modified) (change 'user' to your own user name)
    chrome_profile_path = "C:/Users/user/AppData/Local/Google/Chrome/User Data"

    # Set Chrome options to use the existing profile
    chrome_options = Options()
    chrome_options.add_argument(f"user-data-dir={chrome_profile_path}")  # Path to user data directory
    chrome_options.add_argument("profile-directory=Default")  # Specify profile directory (e.g., 'Profile 1' if you use a custom profile) (can be modified)

    # Create a service object for ChromeDriver
    service = Service(ChromeDriverManager().install())

    # Start ChromeDriver using the profile and service
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # URL info
        print(f"Scraping from -> '{url}'...")

        # Minimize window
        driver.minimize_window()

        # Open the URL
        driver.get(url)

        # Wait for the page to load
        time.sleep(5)

        # Locate the search filter
        try:
            search_filter = driver.find_element(By.CSS_SELECTOR, "#query")

            # Click on the filter and enter the search text
            search_filter.click()
            search_filter.send_keys(search_text)
            search_filter.send_keys(Keys.RETURN)

        except NoSuchElementException:
            # If search filter is not found, print an error message
            print(f"\nError: '{url}' is not a valid URL. The script will now terminate...")
            sys.exit(1)
    
        # Wait for the results to filter (120 seconds)
        time.sleep(120)

        # Scrape all file names (generalized selector)
        file_name_elements = driver.find_elements(By.CSS_SELECTOR, "#__next > div > div.mx-2.my-1.overflow-x-auto.grid.grid-cols-1.sm\\:grid-cols-2.md\\:grid-cols-3.lg\\:grid-cols-4.xl\\:grid-cols-6.gap-4 > div > div > h2")
        file_size_elements = driver.find_elements(By.XPATH, "//*[@id='__next']/div/div[4]/div/div/div[1]")

        # Check if there are any files found
        if not file_name_elements:
            print(f"No matching files found from '{url}'. The script will now terminate...")
            sys.exit(1)

        # Get the text from each file name element
        print("\nMatching files found:")
        file_names = [element.text for element in file_name_elements]

        # Extract only the total file size from each element
        file_sizes = []
        for element in file_size_elements:
            size_text = element.text
            # Extract the first part before the semicolon, which should be the total size
            total_size = size_text.split(';')[0].strip()
            # Extract just the size value (e.g., "57.89 GB")
            size_value = ' '.join(total_size.split()[1:])
            file_sizes.append(size_value)

        # Print file names to the terminal for the user to select
        for idx, (file_name, file_size) in enumerate(zip(file_names, file_sizes), start=1):
            print(f"{idx}. {file_name} - {file_size}")

        while True:
            try:
                # Get user to input a number to choose the corresponding file
                selected_num = int(input("Type in the NUMBER corresponding to the file you want: "))
                
                if 1 <= selected_num <= len(file_name_elements):  # Ensure the number is within the valid range
                    selected_file_element = file_name_elements[selected_num - 1]
                    break  # Exit the loop if the input is valid
                else:
                    print(f"Please enter a number between 1 and {len(file_name_elements)}.")
            
            except ValueError:
                # Handle case where the input is not an integer
                print("Invalid input. Please enter a number only.")
        
        print("Getting file, please wait...")

        # Locate the corresponding button for the selected file (within the same section)
        button = selected_file_element.find_element(By.XPATH, "./following-sibling::div[contains(@class, 'space-x-2')]/button")

        # Click the button corresponding to the selected file
        button.click()

        time.sleep(10)

        print(f"File '{file_names[selected_num - 1]}' added to library successfully. Click on the file then click on 'DL' to send to Real-Debrid to download or stream it. Now opening DMM Library...")

        time.sleep(5)

        # Show browser window
        driver.maximize_window()

        # Go to DMM library
        library_url = 'https://debridmediamanager.com/library'
        driver.get(library_url)

        input("\nPress Enter to terminate the script and browser window...")

    except WebDriverException:
        print(f"\nError: '{url}' could not be reached. The script will now terminate...")
        sys.exit(1)
    except Exception as e:
        print(f"\nAn unexpected error occurred. Details:\n{str(e)}")
        sys.exit(1)

def main():
    input("Reminder: Make sure you are logged into Real-Debrid (real-debrid.com) and Debrid Media Manager (debridmediamanager.com).\nPress Enter to continue...\n")

    while True:
        media_type = input("Movie or TV? [M/T]: ").strip().upper()
        
        if media_type in ['M', 'T']:
            break  # Exit the loop if the input is valid
        else:
            print("Invalid input. Please enter 'M' for movie or 'T' for TV.")
    
    if media_type == 'M':
        imdb_id = get_movie_id()
        tv_query = None

        while True:
            movie_query = input("Is it a recently released (within this month) movie? [Y/N]: ").strip().upper()
            if movie_query == 'Y':
                search_text = "web-dl ^(?!.*(?:hdr|dv|dovi)).*(?:2160p).*$" # (can be modified)
                break  # Exit the loop on valid input
            elif movie_query == 'N':
                search_text = "remux ^(?!.*(?:hdr|dv|dovi)).*(?:1080p).*$" # (can be modified)
                break  # Exit the loop on valid input
            else:
                print("Invalid input. Please enter 'Y' for yes or 'N' for no.")

    elif media_type =='T':
        imdb_id = get_tv_id()

        while True:
            tv_query = input("What season of the show are you looking for? Enter the season number - ")
            if tv_query.isdigit():
                search_text = "web-dl ^(?!.*(?:hdr|dv|dovi)).*(?:1080p|2160p).*$" # (can be modified)
                break
            else:
                print("Invalid input. Please enter a digit.")
    
    print("Please wait for around 2 minutes...")

    time.sleep(3)

    if imdb_id:
        url = get_url(media_type, imdb_id, tv_query)
        automate_webpage(url, search_text, media_type)

if __name__ == "__main__":
    main()
