# Semi-Automated Python Script for Real-Debrid

## Prerequisites: 
* real-debrid premium account 
* browser driver (e.g chrome driver) corresponding to browser version
* python 3.11 or later
* relevant python modules (which require installation): Selenium (`pip install selenium`), IMDB (`pip install imdb`), WebDriver Manager (`pip install webdriver-manager`)

> **Make sure all browser windows are closed before running the script.**

> **Make sure you are logged into both Real-Debrid and Debrid Media Manager prior to running the script.**

## Optional parameters to modify in script code (main.py):
* driver path (not needed if using webdriver manager -- automated)
* user profile path (default user name is `user`)
* user profile directory name (if default, then `Default`)
* regex for movies/tv based on output device's codec and format compatibilities

## Usage Guide:
1. download zip of the project
2. extract all
3. in the directory of where the files are, *right click* > *open in Terminal*
4. in the Terminal, `python main.py`
5. follow each of the prompts shown