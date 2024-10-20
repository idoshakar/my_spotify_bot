import os
import time
import spotipy
import tweepy
import praw
from spotipy.oauth2 import SpotifyOAuth
import random
import pandas as pd
import json
import requests

# dict of all clients
sp_client = None
Clients = {}
subreddits = {}

def fb():
    url = ("https://graph.facebook.com/v21.0/122103483638572442?access_token=EAAHf56tyeq8BOzFI4ajelFmlj0uLmRa8hZAJ8O48"
           "41ZCVwks0vK0qgUKNaNByS2bEfDcZAjopioKUyGhlxlwzwvysMzSr5h76m5QeQN7Mz771DsM4mhj81KUd9mZC9lMdwMQr6byFLsqEpnRd8h"
           "eAICYAaA0Kd2oD0uezzSOKngIu9d7ESMt2RQFIMQ7xZA5v4SkuZCB95ZCE0UNxJAICa6PP7xq51N8ocQg6HMEA3ZB0kJ5yHRTAydtK5fAiu"
           "dNhmldhzNV4wZDZD")
    response = requests.get(url)
    print(response.content)

def setup_clients():
    """
    extracts tokens dictionary from json file and calls defs to set
    up clients for each interface
    """
    with open('tokens.json') as f:
        tokens_dict = json.load(f)
    setup_twitter(tokens_dict['twitter'])
    setup_reddit(tokens_dict['reddit'])
    setup_spotify(tokens_dict['spotify'])
    print("clients created")

def setup_spotify(sp_tokens_dict):
    """
    sets up spotify client, updates Clients dictionary
    :param sp_tokens_dict: dictionary of necessary tokens
    """
    sp_client_id = sp_tokens_dict['CLIENT_ID']
    sp_client_secret = sp_tokens_dict['CLIENT_SECRET']
    sp_redirect_uri = sp_tokens_dict['REDIRECT_URI']
    global sp_client
    sp_client = spotipy.Spotify(
        auth_manager=SpotifyOAuth(client_id=sp_client_id, client_secret=sp_client_secret, redirect_uri=sp_redirect_uri,
                                  scope="playlist-modify-public"))

def setup_twitter(x_tokens_dict):
    """
    sets up Twitter client and updates Clients dictionary
    :param x_tokens_dict: dictionary of necessary tokens
    """
    api_key = x_tokens_dict['API_KEY']
    api_secret = x_tokens_dict['API_SECRET']
    bearer_token = x_tokens_dict['BEARER_TOKEN']
    access_token = x_tokens_dict['ACCESS_TOKEN']
    access_token_secret = x_tokens_dict['ACCESS_TOKEN_SECRET']
    x_client = tweepy.Client(bearer_token, api_key, api_secret, access_token, access_token_secret)
    x_auth = tweepy.OAuthHandler(api_key, api_secret, access_token, access_token_secret)
    api = tweepy.API(x_auth)
    Clients['twitter'] = x_client

def setup_reddit(red_tokens_dict):
    """
    sets up Reddit client and updates Clients dictionary
    :param red_tokens_dict: dictionary of necessary tokens
    """
    user_name = red_tokens_dict['USER_NAME']
    password = red_tokens_dict['PASSWORD']
    client_id = red_tokens_dict['CLIENT_ID']
    client_secret = red_tokens_dict['CLIENT_SECRET']

    client = praw.Reddit(client_id=client_id,
                         client_secret=client_secret,
                         username=user_name,
                         password=password,
                         user_agent="Spotify Bot v1.0")
    Clients['reddit'] = client
    global subreddits
    subreddits = []
    while True:
        subreddit = input("add subreddit, press enter. (to stop q): ")
        if subreddit == 'q':
            break
        subreddits.append(subreddit)
    if len(subreddits) == 0:
        print("****error, no subreddits were added***")

def post_to_media(title, text):
    Clients['twitter'].create_tweet(text)

    for subreddit in subreddits:
        sub = Clients['reddit'].subreddit(subreddit)
        sub.submit(title=title, selftext=text)


def convert_to_uri_list(playlist_url):
    """
    converts a -playlist to list of uri's.
    :param playlist_url: the playlist to be converted
    :return: a list of uri's.
    """
    tracks = Clients['spotify'].playlist_items(playlist_url)['items']
    return [track['track']['uri'] for track in tracks if track['track']]


def add_random_songs(main_playlist_url, source_playlist_url, num=1):
    """
    adds a random sing from a source playlist to a target playlist.
    :param num: number of songs to be added.
    :param main_playlist_url: target playlist
    :param source_playlist_url: source playlist
    """
    source_list = convert_to_uri_list(source_playlist_url)
    main_playlist_id = main_playlist_url.split('/')[-1].split('?')[0]

    if not source_list:
        print("The source playlist is empty or invalid.")
        return
    unique_indexes = random.sample(range(1, len(source_list)), num)
    for index in unique_indexes:
        new_track = source_list[index]
        if sp_client is None:
            print("spotify client not defined!")
            return
        sp_client.playlist_add_items(main_playlist_id, [new_track])
    print("songs added successfully.")


def get_playlist_data(playlist_url):
    """
    saves data of songs in playlist in csv with name "playlist_name_data".
    if csv exists appends data, else creates it.
    columns: track_name, artists, popularity, release_date, current_date
    :param playlist_url: the url of the playlist
    """
    playlist_df = pd.DataFrame()
    playlist_name = Clients['spotify'].playlist(playlist_url)['name']
    file_path = f"data/{playlist_name}_data.csv"

    current_time = time.localtime()
    current_date = time.strftime("%d-%m-%Y", current_time)
    for item in Clients['spotify'].playlist_items(playlist_url)['items']:
        track = item['track']
        if track is None:
            continue

        new_row = pd.DataFrame({"track_name": [track['name']],
                                "artists": [', '.join([artist['name'] for artist in track['artists']])],
                                "album": [track['album']['name']],
                                "popularity": [track['popularity']],
                                "release_date": [track['album']['release_date']],
                                "current_date": [current_date], })
        playlist_df = pd.concat([playlist_df, new_row], ignore_index=True)
    if os.path.isfile(file_path):
        playlist_df.to_csv(file_path, mode='a', header=False, index=False)
    else:
        playlist_df.to_csv(file_path, mode='w', header=False, index=False)
    print("data saved successfully.")


def add_song(playlist_url, track_url, position=None):
    """
    adds a song to a playlist, if position is given then adds it to the given position.
    :param playlist_url: the target playlist
    :param track_url: the track to be added.
    :param position: the desired position of the song to be added, could be None.
    """
    playlist_id = playlist_url.split('/')[-1].split('?')[0]
    sp_client.playlist_add_items(playlist_id, [track_url], position=position - 1)
    print("song added successfully")


if __name__ == '__main__':
    exp_playlist_url = "https://open.spotify.com/playlist/2HZtSbeoCdSvOnROAK6XVt"
    mac_miller_playlist_url = "https://open.spotify.com/playlist/37i9dQZF1EIZobirLlpmBa"
    trans_url = "https://open.spotify.com/playlist/58IdYbheI5ak15uxlbLZDN"
    figure_it_out_url = "https://open.spotify.com/track/0RQDBCsED70Qfq1CdRvavd?si=4568c6dfd1874c23"
    # print(os.listdir())
    setup_clients()
    add_song(exp_playlist_url, figure_it_out_url, 1)
    # fb()