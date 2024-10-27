import mpv

def play_in_mpv(link):
    """Simple function to play a video link in MPV"""
    player = mpv.MPV(
        input_default_bindings=True,
        input_vo_keyboard=True,
        osc=True,
        config=True,
        geometry="1280x720"
    )

    player['fullscreen'] = False  # Start windowed, can be toggled with 'f' key
    player['keep-open'] = True    # Don't close player when video ends

    try:
        player.play(link)
        player.wait_for_playback()
    finally:
        player.terminate()