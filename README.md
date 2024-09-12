# **Media Automation using Python (Anime & Non-Anime)**
*...through sailing the High Seas...*

---

# **Non-Anime**: Python Script for Real-Debrid

* This is a simple script for users to easily and instantly add the specific file (with the condition that it must be cached by Real-Debrid) of a movie or TV show that they want into their DMM Library by scraping results from Debrid Media Manager's search query.
* Users enter the movie/TV show title along with its year (as well as specify the season for the TV show) and the script will output a list of available files (along with their respective file sizes) for you to select.
* After selecting, it will automatically add the file into DMM Library and then open the Library page.
* Note that the script is focused on Google Chrome for Windows, but it is not hard to tweak a few lines to make it compatible with other browsers (as long as the browser has support for WebDriver).

## Prerequisites: 
* Real-Debrid premium account 
* Web browser driver (e.g Chrome driver) corresponding to browser version (no manual installation required if using WebDriver Manager)
* Python 3.11 or later (enable *add Python to PATH* during installation)
* Relevant python modules (which require installation): Selenium (`pip install selenium`), IMDB (`pip install imdbpy`), WebDriver Manager (`pip install webdriver-manager`)

> **Make sure all browser windows are closed before running the script.**

> **Make sure you are logged into both Real-Debrid and Debrid Media Manager prior to running the script.**

## Optional parameters to modify in source code (main.py):
* Driver path (not needed if using webdriver manager -- automated)
* User profile path (default user name is `user`)
* User profile directory name (if default, then `Default`)
* Regex for movies/tv based on output device's media codec and format compatibilities (*Advanced*)

## Usage Guide:
1. Download `main.py` into a folder (optionally, download the entire ZIP of the project and extract all files into a folder)
2. Go to ***chrome://version/*** (or similar for other browsers) and locate `Profile Path`
3. Open `main.py` in an IDE or Notepad
4. Change `user` in `chrome_profile_path` to the correct user name with reference to `Profile Path`
5. Change `Default` in `profile-directory` to the correct profile name with reference to `Profile Path`
6. Save changes to `main.py` and close
7. In the directory of where the files are, *right click* > *open in Terminal*
8. In the Terminal, `python main.py`
9. Follow each of the prompts shown

---

# **Anime**: Python Script to Get a Best Release's Magnet Link

* A light and fast script for users to get the magnet link of the best possible current release of an anime through SeaDex or SubsPlease/Erai-raws.
* Users enter an anime title and it will output a list of matching titles from the Anilist API for users to select (e.g a specific season for it)
* Depending on the status of the show, the script will then search in Seadex (Finished shows) for the Best Releases or in Nyaa for SubsPlease/Erai-raws releases (Airing shows)
* Users select their preferred file and a Magnet Link will be output, which users can choose to copy into their clipboard with a click of a key if they want to (using `Pyperclip`)
* **NO** Real-Debrid account is required (users are only getting a Magnet Link)

## Prerequisites:
* Python 3.11 or later (enable *add Python to PATH* during installation)
* Relevant python modules (which require installation): Requests (`pip install requests`), BeautifulSoup (`pip install beaufitulsoup4`), Pyperclip (`pip install pyperclip`)

## Optional parameters to modify in source code (animain.py):
* Alternative Source to `Subsplease`, currently using `Erai-raws`
* Input key to check alternative source, currently set to `C`

## Usage guide
1. Download `animain.py` into a folder (optionally, download the entire ZIP of the project and extract all files into a folder)
2. In the directory of where the files are, *right click* > *open in Terminal*
3. In the Terminal, `python animain.py`
4. Follow each of the prompts shown