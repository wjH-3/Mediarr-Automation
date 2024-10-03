from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
import psutil
import sys
import os

# Check if 'user' and 'profile' variables exist in sys.argv
def get_user_profile():
    if len(sys.argv) >= 3:
        return sys.argv[1], sys.argv[2]
    else:
        print("Error: Missing arguments for user and profile")
        input("Press Enter to Exit...")
        return

# Check if browser window(s) open
def browser_open(browser='chrome'):
    for process in psutil.process_iter(['name']):
        if browser in process.info['name'].lower():
            return True
    return False

def go_library(user, profile):

    library_url = 'https://debridmediamanager.com/library'
    
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
        # Open the URL
        driver.get(library_url)
        driver.maximize_window()

        input("\nPress Enter to terminate the script and browser window...\n")
    except WebDriverException:
        print(f"\nError: '{library_url}' could not be reached. The script will now terminate...")
        input("Press Enter to Exit...")
        return
    except Exception as e:
        print(f"\nAn unexpected error occurred. Details:\n{str(e)}")

def main():
    user, profile = get_user_profile()

    print("\nReminder: Make sure you are logged into Real-Debrid (real-debrid.com) and Debrid Media Manager (debridmediamanager.com).")
    input("Press Enter to continue...")

    if browser_open():
        print("\nWarning: Browser window detected. Please close all browser windows before continuing.")
        input("Press Enter to continue...")

    print("\nOpening DMM Library...")

    go_library(user, profile)

if __name__ == "__main__":
    main()