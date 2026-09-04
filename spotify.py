import argparse
import json
import random
import os
import sys
import time
from typing import List
import pickle

from dotenv import load_dotenv
import spotipy
import requests
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

ROOT_PATH = os.path.dirname(os.path.realpath(__file__))
#Defina SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRETe SPOTIFY_REDIRECT_URI mo .env antes de rodar o script.

CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.environ.get("SPOTIFY_REDIRECT_URI")

if not all([CLIENT_ID, CLIENT_SECRET, REDIRECT_URI]):
    sys.exit(
        "Erro: defina as variáveis de ambiente SPOTIFY_CLIENT_ID, "
        "SPOTIFY_CLIENT_SECRET e SPOTIFY_REDIRECT_URI antes de rodar o script."
    )


def main(artist: str, track: str, save: bool = None):
    #Gerar playlist de 25 múscias baseada na música escohida no input.
    seeds = search_artist_track(artist, track)
    json_response = query_api(seeds)
    if save is not None:
        try:
            print_output(json_response)
            playlist = create_playlist(artist, track)
            add_tracks_to_playlist(json_response, playlist)
        except Exception:
            print("Couldn't add to playlist...")
    else:
        print_output(json_response)


def add_tracks_to_playlist(json_response: dict, playlist_name: str):
    playlist_id = fetch_playlist_id(playlist_name)
    uris = []
    for i, j in enumerate(json_response['tracks']):
        uris.append(j['uri'])
    scope = "playlist-modify-public"
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                                    client_secret=CLIENT_SECRET,
                                                    redirect_uri=REDIRECT_URI,
                                                    scope=scope))
    sp.playlist_add_items(playlist_id, uris)
    print(' ')
    print("Playlist salva!")


def fetch_playlist_id(playlist_name):
    scope = "playlist-modify-public"
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                                    client_secret=CLIENT_SECRET,
                                                    redirect_uri=REDIRECT_URI,
                                                    scope=scope))
    playlists = sp.current_user_playlists()
    for playlist in playlists['items']:
        if playlist['name'] == playlist_name:
            return playlist['id']


def create_playlist(artist: str, track: str):
    scope = "playlist-modify-public"
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                                    client_secret=CLIENT_SECRET,
                                                    redirect_uri=REDIRECT_URI,
                                                    scope=scope))
    playlist_name = f"SM - Playlist baseada em {track} de {artist}"
    user_id = sp.me()['id']
    sp.user_playlist_create(user_id, playlist_name)
    return playlist_name


def acquire_token():
    token_cache_dir = os.path.join(ROOT_PATH, "cache")
    token_cache_file = os.path.join(token_cache_dir, "token.p")

    if os.path.exists(token_cache_file):
        current_time = time.time()
        if current_time - os.path.getmtime(token_cache_file) < 3600:
            with open(token_cache_file, "rb") as fid:
                token = pickle.load(fid)
            return token
        else:
            return _refresh_token(token_cache_dir, token_cache_file)
    else:
        return _refresh_token(token_cache_dir, token_cache_file)


def _refresh_token(token_cache_dir, token_cache_file):
    grant_type = 'client_credentials'
    body_params = {'grant_type': grant_type}
    url = 'https://accounts.spotify.com/api/token'
    response = requests.post(url, data=body_params, auth=(CLIENT_ID, CLIENT_SECRET))
    token_raw = json.loads(response.text)
    token = token_raw["access_token"]
    os.makedirs(token_cache_dir, exist_ok=True)
    with open(token_cache_file, "wb") as fid:
        pickle.dump(token, fid)
    return token


def fetch_artist_genre(artist_id: str):
    endpoint_url = f'https://api.spotify.com/v1/artists/{artist_id}'
    query = f'{endpoint_url}'
    settings = define_settings()
    response = requests.get(query,
                             headers={"Content-Type": "application/json",
                                      "Authorization": f"Bearer {settings[1]}"})
    json_response = response.json()
    genres = json_response['genres']
    try:
        index = random.randint(0, len(genres) - 1)
    except Exception:
        print("Spotify doesn't store genres for this artist, please try another one!")
        sys.exit()
    genre = genres[index]
    return genre


def search_artist_track(artist: str, track: str):
    track = track.replace(" ", "+")
    settings = define_settings()
    endpoint_url = "https://api.spotify.com/v1/search?"
    query = f'{endpoint_url}'
    query += f'q=track%3A{track}%20artist%3A{artist}&type=track'
    response = requests.get(query, headers={"Content-Type": "application/json",
                                             "Authorization": f"Bearer {settings[1]}"}
                             )
    json_response = response.json()
    seeds = get_track_artist_id_from_json(json_response)
    return seeds


def get_track_artist_id_from_json(json_response: dict):
    try:
        artist_id = json_response['tracks']['items'][0]['artists'][0]['id']
    except Exception:
        print("Whoops, something went wrong fetching the artist info - please try again")
        sys.exit()
    track_id = json_response['tracks']['items'][0]['id']
    genre = fetch_artist_genre(artist_id)
    seeds = [(artist_id), (track_id), (genre)]
    return seeds


def define_settings():
    endpoint_url = "https://api.spotify.com/v1/recommendations?"
    token = acquire_token()
    settings = [endpoint_url, token]
    return settings


def define_filters(seeds: List):
    limit = 25
    market = "BR"
    seed_genres = seeds[2]
    seed_artists = seeds[0]
    seed_tracks = seeds[1]
    filters = [limit, market, seed_genres, seed_artists, seed_tracks]
    return filters


def query_api(seeds: List):
    settings = define_settings()
    filters = define_filters(seeds)
    query = f'{settings[0]}limit={filters[0]}&market={filters[1]}&seed_genres={filters[2]}'
    query += f'&seed_artists={filters[3]}'
    query += f'&seed_tracks={filters[4]}'
    response = requests.get(query,
                             headers={"Content-Type": "application/json",
                                      "Authorization": f"Bearer {settings[1]}"})
    json_response = response.json()
    return json_response


def print_output(json_response: dict):
    print(' ')
    print('Playlist: ')
    print(' ')
    for i, j in enumerate(json_response['tracks']):
        print(f"{i+1}) {j['artists'][0]['name']} - {j['name']} ")


def parse_options():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artist", dest="artist", required=True)
    parser.add_argument("--track", dest="track", action="store", type=str,
                         required=True, help="Track name.")
    parser.add_argument("-s", dest="save", action="store_true",
                         required=False, help="Save playlist.")
    options = parser.parse_args()
    return options


if __name__ == "__main__":
    OPTIONS = parse_options()
    if OPTIONS.save:
        main(OPTIONS.artist, OPTIONS.track, OPTIONS.save)
    else:
        main(OPTIONS.artist, OPTIONS.track)