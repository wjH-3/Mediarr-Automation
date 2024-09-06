# Semi-Automated Python Script for Real-Debrid

* This is a simple script for users to easily and instantly add the specific file (with the condition that it must be cached by Real-Debrid) of a movie or TV show that they want into their DMM Library by scraping results from Debrid Media Manager's search query.
* Users enter the movie/TV title along with its year and the script will output a list of available files for you to select.
* After selecting, it will automatically add the file into DMM Library and then open the Library page.
* Note that the script is focused on Google Chrome for Windows, but it is not hard to tweak a few lines to make it compatible with other browsers (as long as the browser has support for WebDriver).

## Prerequisites: 
* Real-Debrid premium account 
* Browser driver (e.g chrome driver) corresponding to browser version
* Python 3.11 or later (enable *add Python to PATH* during installation)
* Relevant python modules (which require installation): Selenium (`pip install selenium`), IMDB (`pip install imdbpy`), WebDriver Manager (`pip install webdriver-manager`)

> **Make sure all browser windows are closed before running the script.**

> **Make sure you are logged into both Real-Debrid and Debrid Media Manager prior to running the script.**

## Optional parameters to modify in script code (main.py):
* Driver path (not needed if using webdriver manager -- automated)
* User profile path (default user name is `user`)
* User profile directory name (if default, then `Default`)
* Regex for movies/tv based on output device's codec and format compatibilities (*Advanced*)

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