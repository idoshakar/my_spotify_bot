import time

import dateutil.utils
import spotipy
from spotipy import SpotifyException
from spotipy.oauth2 import SpotifyOAuth
import openpyxl
import random

my_clientID = "7bb19174e95a40dfa5c49973e5dda65c"
my_client_secret = "eabd795b500d4b73a03a940fbd1a4da1"
my_redirect_uri = "http://localhost:8888/callback"

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(client_id=my_clientID, client_secret=my_client_secret, redirect_uri=my_redirect_uri,
                              scope="playlist-modify-public"))


def convertToUriList(PlaylistURL):
    playlistURI = PlaylistURL[-22:]
    tracks = sp.playlist(playlistURI)['tracks']['items']

    tracksLists = [track['track']['uri'] for track in tracks]
    return tracksLists


def add_songs(main_playlist_url, source_playlist_url):
    source_list = convertToUriList(source_playlist_url)
    index = random.randint(0, len(source_list) - 1)
    new_track = source_list[index]
    sp.playlist_add_items(main_playlist_url[-22:], [new_track])


if __name__ == '__main__':
    main_url = "https://open.spotify.com/playlist/2HZtSbeoCdSvOnROAK6XVt"
    source_url = "https://open.spotify.com/playlist/37i9dQZF1EIZobirLlpmBa"
    while True:
        add_songs(main_url, source_url)
        time.sleep(60)
