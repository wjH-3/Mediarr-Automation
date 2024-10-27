import mpv
import os
import sys
import pygetwindow as gw
import time

def get_mpv_path():
    """Get path to bundled MPV files"""
    if getattr(sys, 'frozen', False):
        # Running as compiled exe
        base_path = sys._MEIPASS
    else:
        # Running as script
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, 'mpv_files')

def play_in_mpv(link):
    """Simple function to play a video link in MPV"""
    mpv_path = get_mpv_path()

    player = mpv.MPV(
        input_default_bindings=True,
        input_vo_keyboard=True,
        osc=True,
        config=True,
        geometry="1280x720",

        # Point to bundled MPV files
        config_dir=mpv_path,
    )

    player['fullscreen'] = False  # Start windowed, can be toggled with 'f' key
    player['keep-open'] = True    # Don't close player when video ends

    # Give mpv a moment to open
    time.sleep(1)

    # Attempt to bring mpv window to front
    mpv_windows = [w for w in gw.getWindowsWithTitle('mpv') if w.isActive]
    if mpv_windows:
        mpv_windows[0].activate()

    try:
        player.play(link)
        player.wait_for_playback()
    finally:
        player.terminate()