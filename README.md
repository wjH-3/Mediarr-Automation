# **Mediarr**
***Sail the High Seas...***


A simple CLI Python app that utilises the [Real-Debrid](https://real-debrid.com/) API alongside [Debrid Media Manager](https://debridmediamanager.com/). It allows users to access a suite of Real-Debrid's main features, as well as get any Non-anime or Anime content, whether it be movies or shows, in a fast and automated way all within the Terminal itself. 

## Features:
* Search for **Non-Anime** movies/TV shows: Scrape a particular movie/show from DMM, displaying the relevant files in a list for users to choose from
    * query a specific season of a show
    * dynamic regex filtering to scrape only the highest quality files first and then automatically change up the filters if files are not found
* **Anime**: makes use of the AniList and SeaDex API to get the magnet links of a Best Release of the specified anime, as well as query Nyaa for SubsPlease/Erai-raws releases of currently airing anime
* **Get DL Link instantly**: After selecting the file you want, Mediarr will automatically get the RD links for the torrent and unrestrict them, outputting a DL Link that's copied into your clipboard using `Pyperclip`. From there, you can simply paste the link into your Video Player to stream the content right away or download it if you want
* **Paste your own Magnet Link**: Paste your own magnet link in and it will first check for **Instant Availability**, i.e if the torrent is cached in RD. If it is, it will automatcially proceed to add the torrent and then unrestrict it and output the DL Links. If it is not, it will inform you and asks if you still want to proceed to download the torrent
* **Unrestrict Link**: Similarly, you can paste in any link from RD's supported hosters and it will unrestrict and output the DL Link for you
* **Access Torrent Library**: If you already have an existing torrent added in RD, Mediarr allows you to search for the file by name (e.g the movie/TV show title) and will display the matching torrents for you to select and then output the DL Links. This is particularly useful if you want to continue a TV show/Movie that you haven't finished watching
* **Binge Watch a Series Conveniently**: For torrents that have multiple files in them (e.g TV Show/Anime Episodes), when you unrestrict the torrent (whether it be a newly added torrent or one that is already in your Library), it will first display the files of the torrent in a list for you to choose, i.e like an episode list of the show. Selecting one will then unrestrict the particular file and output its DL Link, and then the selection prompt will appear again for you to choose another file if you wish
    * This is very useful because once you have finished an episode of a show, you can simple select the next episode's file and it will once again output the DL link for you to paste into your Video Player to continue watching
* **Access DMM Library**: Opens the DMM Library, which provides a good interface for your torrent library, allowing you to manage your torrents


All of this can be done right on the terminal, and no other installation is required except for the executable `Mediarr.exe`.

*Note: You can also choose to use either the non-anime or anime script by itself. For more info on how to do so, head over to their respective sections where there are instructions and also more details about the script themselves.*

---


# Setup Guide:

1. Go to [Releases](https://github.com/wjH-3/Mediarr-Automation/releases) and download the latest version of `Mediarr.exe` into a folder
2. For the first time opening the executable, you might get the message that Windows doesn't recognize it -- *click on 'More info'* > *Run anyway*
3. On first launch (you only have to do this ONCE), go to ***chrome://version/*** on Google Chrome (or similar for other browsers) and locate `Profile Path`
4. The profile path is in the format of [`driver name`\Users\ `system user name`\AppData\Local\Google\Chrome\User Data\ `profile directory name`]
5. Based on the directory path shown, enter your `system user name` and `profile directory name` accordingly when prompted (these information variables are stored in a JSON file locally, namely `config.json`)
6. On first launch (you only have to do this ONCE), get your Real-Debrid API Token from the [Real-Debrid Website](https://real-debrid.com/apitoken) and input it when prompted (the token is stored in a JSON file locally, namely `token.json`)
7. After the first-time setup, you will be greeted with an Options Menu. Choose your preferred option and continue following each of the prompts shown.

*Note: The executable is specifically made for use with Google Chrome on Windows. To make it compatible with other browsers (as long as they have support for WebDriver), you can download the source code and alter `non_ani.py` and then build with `Pyinstaller` using the command in `toBuild.txt`.*

---

# Individual Scripts:
More about non_ani.py and ani.py.
<details>
<summary><b>Non-Anime: Python Script for DMM</b></summary>

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

## Optional parameters to modify in source code (non_animain.py):
* Driver path (not needed if using Webdriver Manager -- automated)
* User profile path (default user name is `user`)
* User profile directory name (if default, then `Default`)
* Regex for movies/tv based on output device's media codec and format compatibilities (*advanced*)

## Usage Guide:
1. Download `non_animain.py` into a folder (optionally, download the entire ZIP of the project and extract all files into a folder)
2. Go to ***chrome://version/*** (or similar for other browsers) and locate `Profile Path`
3. Open `non_animain.py` in an IDE or Notepad
4. Change `user` in `chrome_profile_path` to the correct user name with reference to `Profile Path`
5. Change `Default` in `profile-directory` to the correct profile name with reference to `Profile Path`
6. Save changes to `non_animain.py` and close
7. In the directory of where the files are, *right click* > *open in Terminal*
8. In the Terminal,
```python
python non_animain.py
```
9. Follow each of the prompts shown
</details>


<details>
<summary><b>Anime: Python Script to get Magnet Link</b></summary>

* A light and fast script for users to get the magnet link of the best possible current release of an anime through SeaDex or SubsPlease/Erai-raws
* Users enter an anime title and it will output a list of matching titles from the Anilist API for users to select (e.g a specific season for the anime)
* Depending on the status of the show, the script will then search in Seadex (Finished shows) for the Best Releases or in Nyaa for SubsPlease/Erai-raws releases (Airing shows)
* Users select their preferred file and a Magnet Link will be output, which users can choose to copy into their clipboard with a click of a key (using `Pyperclip`)
* **NO** Real-Debrid account is required (users are only getting a Magnet Link)

## Prerequisites:
* Python 3.11 or later (enable *add Python to PATH* during installation)
* Relevant python modules (which require installation): Requests (`pip install requests`), BeautifulSoup (`pip install beaufitulsoup4`), Pyperclip (`pip install pyperclip`)

## Optional parameters to modify in source code (animain.py):
* Alternative Source to `Subsplease`, currently using `Erai-raws`
* Input key to check alternative source, currently set to `C`
* Default Quality is set to `1080p` for the Nyaa queries, change it in `base_url`. Other options are `720p` and `480p` (may yield less results)
* Nyaa domain extension currently set to `nyaa.si`, can be changed to `nyaa.land` or others. For a list of working Nyaa proxies, visit [Nyaa Torrents](https://nyaatorrents.info/)

## Usage Guide:
1. Download `animain.py` into a folder (optionally, download the entire ZIP of the project and extract all files into a folder)
2. In the directory of where the files are, *right click* > *open in Terminal*
3. In the Terminal,
```python 
python animain.py
```
4. Follow each of the prompts shown
</details>