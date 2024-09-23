# **Mediarr Automation**
*...through sailing the High Seas...*


# How to Use: The Easy Way

1. Go to Releases and download the latest version of `Mediarr.exe` into a folder
2. On first launch (you only have to do this ONCE), go to ***chrome://version/*** (or similar for other browsers) and locate `Profile Path`
3. The profile path is in the format of [ `driver name` \Users\ `system user name` \AppData\Local\Google\Chrome\User Data\ `profile directory name` ]
4. Based on the directory path shown, enter your `system user name` and `profile directory name` accordingly when prompted
5. Continue following each of the prompts shown
*Note: The executable is specifically made for use with Google Chrome on Windows. To make it compatible with other browsers (as long as they have support for WebDriver), you can download the source code and alter `non_ani.py` and then build with `Pyinstaller` using the command in `toBuild.txt`.*

# *Non-Anime*: Python Script for Real-Debrid

* This is a simple script for users to easily and instantly add the specific file (with the condition that it must be cached by Real-Debrid) of a movie or TV show that they want into their DMM Library by scraping results from Debrid Media Manager's search query
* Users enter the movie/TV show title along with its year (as well as specify the season for the TV show) and the script will output a list of available files (along with their respective file sizes) for you to select
* After selecting, it will automatically add the file into DMM Library and then open the Library page
* Note that the script is focused on Google Chrome for Windows, but it is not hard to tweak a few lines to make it compatible with other browsers (as long as the browser has support for WebDriver)

## Prerequisites: 
* Real-Debrid premium account 
* Web browser driver (e.g Chrome driver) corresponding to browser version (no manual installation required if using WebDriver Manager)
* Python 3.11 or later (enable *add Python to PATH* during installation)
* Relevant python modules (which require installation): Selenium (`pip install selenium`), IMDB (`pip install imdbpy`), WebDriver Manager (`pip install webdriver-manager`), PSUtil (`pip install psutil`)

> **Make sure all browser windows are closed before running the script**

> **Make sure you are logged into both Real-Debrid and Debrid Media Manager prior to running the script**

## Optional parameters to modify in source code (non_ani.py):
* Driver path (not needed if using Webdriver Manager -- automated)
* User profile path (default user name is `user`)
* User profile directory name (if default, then `Default`)
* Regex for movies/tv based on output device's media codec and format compatibilities (*advanced*)

## Usage Guide:
1. Download `non_ani.py` into a folder (optionally, download the entire ZIP of the project and extract all files into a folder)
2. Go to ***chrome://version/*** (or similar for other browsers) and locate `Profile Path`
3. Open `non_ani.py` in an IDE or Notepad
4. Change `user` in `chrome_profile_path` to the correct user name with reference to `Profile Path`
5. Change `Default` in `profile-directory` to the correct profile name with reference to `Profile Path`
6. Save changes to `main.py` and close
7. In the directory of where the files are, *right click* > *open in Terminal*
8. In the Terminal,
```python
python main.py
```
9. Follow each of the prompts shown

---


# *Anime*: Python Script to get Magnet Link

* A light and fast script for users to get the magnet link of the best possible current release of an anime through SeaDex or SubsPlease/Erai-raws
* Users enter an anime title and it will output a list of matching titles from the Anilist API for users to select (e.g a specific season for the anime)
* Depending on the status of the show, the script will then search in Seadex (Finished shows) for the Best Releases or in Nyaa for SubsPlease/Erai-raws releases (Airing shows)
* Users select their preferred file and a Magnet Link will be output, which users can choose to copy into their clipboard with a click of a key (using `Pyperclip`)
* **NO** Real-Debrid account is required (users are only getting a Magnet Link)

## Prerequisites:
* Python 3.11 or later (enable *add Python to PATH* during installation)
* Relevant python modules (which require installation): Requests (`pip install requests`), BeautifulSoup (`pip install beaufitulsoup4`), Pyperclip (`pip install pyperclip`)

## Optional parameters to modify in source code (ani.py):
* Alternative Source to `Subsplease`, currently using `Erai-raws`
* Input key to check alternative source, currently set to `C`
* Default Quality is set to `1080p` for the Nyaa queries, change it in `base_url`. Other options are `720p` and `480p` (may yield less results)
* Nyaa domain extension currently set to `nyaa.si`, can be changed to `nyaa.land` or others. For a list of working Nyaa proxies, visit [Nyaa Torrents](https://nyaatorrents.info/)

## Usage guide
1. Download `ani.py` into a folder (optionally, download the entire ZIP of the project and extract all files into a folder)
2. In the directory of where the files are, *right click* > *open in Terminal*
3. In the Terminal,
```python 
python animain.py
```
4. Follow each of the prompts shown