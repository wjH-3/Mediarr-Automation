# **Mediarr**

***Sail the High Seas...***

A simple CLI Python app that utilises the API of [Real-Debrid](https://real-debrid.com/) and [Debrid Media Manager](https://debridmediamanager.com/). It allows users to access a suite of Real-Debrid's main features, as well as get any Non-anime or Anime content, whether it be movies or shows, in a fast and automated way all within the Terminal itself. 


## Features:

* **Search for Non-Anime** movies/TV shows: <br />
    Scrape a particular movie/show (using its `IMDb` ID) from DMM's API, displaying the relevant files in a list for users to choose from
    * query a specific season of a show (also auto-detect show's airing status with `TVMaze` API to either retrieve complete seasons or single episodes)
    * `RTN` (Rank Torrent Name) and `PTT` (Parsett) integration for title matching the files and filtering out garbage torrents
    * own custom filter for another layer of filtering to improve quality of files (remove duplicates, no upscaled content, only 1080p and 2160p files etc.)
    * after getting all Instantly Available files, it will cross-check with your Torrent Library to see if there are any matching torrents. If yes, it will be shown and you have the option to get the file directly from your library if you choose to
    * dynamic regex filtering to group files into lists of different quality groups
    * integration of `TRaSH Guides` HQ Release Groups to detect files with the best release groups and prioritization of higher tier release groups over lower tiers
    * determine the best torrent file (file with the highest tier release group) for movies and complete TV show seasons. if it exists, you will have the option to auto-select it; for single episodes files, it will show all files with good release groups in its own section
* **Search for Anime**: 
    * use `AniList` API to search for your desired Anime (along with its airing status)
    * use `SeaDex` API to get the magnet links of a Best Release of the specified Anime (if Finished Airing)
    * query `Nyaa` for SubsPlease/Erai-raws releases of Currently Airing Anime
* **MPV Integration**: <br />
    `MPV` comes prepackaged with Mediarr to automatically open a stream link. It uses custom configs (`ModernX` OSC script for a modern UI, Eng subtitles (non  SDH, non Forced) prioritization and auto-selection, auto hardware decoding etc.)
* **Get DL Link instantly**: <br />
    After selecting the file you want, Mediarr will automatically get the RD links for the torrent and unrestrict them, outputting a DL Link that's copied into your clipboard using `Pyperclip`. Then it automatically opens MPV to stream the file (if single link, i.e Movie files and files of Individual Episodes of a TV Show)
* **Add your own Magnet Link**: <br />
    Input your own magnet link in and it will first check for **Instant Availability**, i.e if the torrent is cached in RD. If it is, it will automatcially proceed to add the torrent and then unrestrict it and output the DL Links. If it is not, it will inform you and asks if you still want to proceed to download the torrent
* **Unrestrict Link**: <br />
    Similarly, you can paste in any link from RD's supported hosters and it will unrestrict and output the DL Link for you
* **Access Torrent Library**: <br />
    If you already have an existing torrent added in RD, Mediarr allows you to search for the file by name (e.g the movie/TV show title) and will display the matching torrents for you to select and then output the DL Links. This is particularly useful if you want to continue a TV show/Movie that you haven't finished watching
* **Binge Watch a Series Conveniently**: <br />
    For torrents that have multiple files in them (e.g TV Show/Anime Episodes), when you unrestrict the torrent (whether it be a newly added torrent or one that is already in your Library), it will first display the files of the torrent in a list for you to choose, i.e like an episode list of the show. Selecting one will then unrestrict the particular file and output its DL Link and open it in MPV, and then the selection prompt will appear again for you to choose another file if you wish
    * This is very useful because once you have finished an episode of a show, you can simply select the next episode's file and it will once again output its corresponding DL link for you and open the stream link in MPV

All of this can be done right on the terminal, and no other installation is required except for the executable `Mediarr.exe`.

---


## Usage:

1. Go to [Releases](https://github.com/wjH-3/Mediarr-Automation/releases) and download the latest version of `Mediarr.exe` into a folder <br />
**Note: The executable has a fairly large size because both `Chromium` for `Playwright` and `MPV` are bundled together inside for convenience*
2. When opening the executable for the first time, you might get the message that Windows doesn't recognize it -- *click on 'More info'* > *Run anyway*
3. On first launch (you only have to do this ONCE), get your Real-Debrid API Token from the [Real-Debrid Website](https://real-debrid.com/apitoken) and input it when prompted (the token is stored in a JSON file locally, namely `token.json`)
4. When first searching for Non-Anime content (you only have to do this ONCE), you will be prompted to login to DMM on a Chromium browser using `Playwright`. After logging in successfully, the logged in browser session will then be saved in a JSON file locally, namely `session.json` (so that you won't have to login repeatedly each time)
5. You will be greeted with an Options Menu whenever you open `Mediarr`. Choose your preferred option and continue following each of the prompts shown

---


## Build:

If you want to alter any of the regex filters, file quality groups, RTN and PTT parameters/settings, MPV configs etc. to your personal preference, you can bulld `Mediarr.exe` yourself.
1. Download latest Source Code from [Releases](https://github.com/wjH-3/Mediarr-Automation/releases)
2. The MPV components are not included in the Source Code (will make size too large otherwise) so building the executable would mean you would need to include them in a folder named `mpv_files` in the same directory as all the other Python component files (whether you intend to change the MPV config files or not -- unless you alter the Python files to not use MPV, which is possible too)
3. `mpv_files` need to contain the following files and folders: `fonts`, `scripts`, `input.conf`, `mpv.conf`, `libmpv-2.dll`, `mpv.exe`
4. Playwright components are also not in the Source code. First make sure you have the `playwright` python module installed in your system. Then, navigate to your projects directory in a bash terminal (e.g Git Bash)
5. `export PLAYWRIGHT_BROWSERS_PATH=0` then `playwright install chromium` and ensure it finishes installing
6. Main Python files for altering are: `non_aniV2,py`, `ani.py` and `mpv_auto.py`
7. Nyaa domain (currently set to `nyaa.si`) can be changed to other working proxy domains from [Nyaa Torrents](https://nyaatorrents.info/)
8. After finish altering all the source code, build using the build instructions in `toBuild.txt` (`Pyinstaller` is needed). Make sure to change `{user}` to your actual system user name
