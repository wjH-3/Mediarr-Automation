from playwright.sync_api import sync_playwright
import json
import re
import os

# Define URLs
LOGIN_URL = "https://debridmediamanager.com/realdebrid/login"
MOVIE_URL = "https://debridmediamanager.com/movie/tt0816692"
SESSION_FILE = "session.json"  # File to save session state


# Regular expression to capture dmmProblemKey and solution from the URL
key_solution_pattern = re.compile(r"dmmProblemKey=([a-zA-Z0-9\-]+)&solution=([a-zA-Z0-9]+)")

# Log in to DMM and save session cookies if not already saved
def login_and_save_session():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Non-headless for login
        context = browser.new_context()

        # Load the login page
        page = context.new_page()
        page.goto(LOGIN_URL)
        print("Please log in and then press Enter here once you're logged in.")
        input("Press Enter to continue...")

        # Save session state (cookies and storage) to file
        context.storage_state(path=SESSION_FILE)
        browser.close()
        print("Session saved successfully!")

class DMMKeyManager:
    def __init__(self):
        self.dmmProblemKey = None
        self.solution = None
        self.key_solution_pattern = re.compile(r"dmmProblemKey=([a-zA-Z0-9\-]+)&solution=([a-zA-Z0-9]+)")

        # Check if session.json exists, and if not, prompt login
        if not os.path.exists(SESSION_FILE):
            print("Session file not found. Please log in.")
            login_and_save_session()
        
    def get_new_key_hash(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(storage_state=SESSION_FILE)
            page = context.new_page()

            def handle_response(response):
                if response.url.startswith("https://debridmediamanager.com/api/torrents/"):
                    match = self.key_solution_pattern.search(response.url)
                    if match:
                        self.dmmProblemKey, self.solution = match.groups()
                        #print(f"\nKey: {self.dmmProblemKey}, Hash: {self.solution}")

            page.on("response", handle_response)
            page.goto(MOVIE_URL)
            page.wait_for_timeout(2000)  # Wait for response to be captured
            browser.close()
            
        return self.dmmProblemKey, self.solution

# Create a global instance
key_manager = DMMKeyManager()
