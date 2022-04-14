from dotenv import load_dotenv
from pyvis.network import Network
import os
import requests
import json

# API token and playlist ID is stored in .env file (TOKEN and PLAYLIST)
# You can generate your own token here: https://developer.spotify.com/console/get-playlist-tracks/
# Just click "Get Token" and if you want to visualize private playlist, select  adequate scope
load_dotenv()
headers = {'Accept': 'application/json','Content-Type': 'application/json','Authorization': f'Bearer {os.environ["TOKEN"]}'}
params = {'market': 'PL', 'limit': '100'}

artists = {}
connections = {}
# Get info about artists from Spotify API and then count artists and their connections
def get_connections(link):
    response = requests.get(link, headers=headers, params=params)
    data = json.loads(response.text)
    for track in data["items"]:
        local_artists = []
        for artist in track["track"]["artists"]:
            local_artists.append(artist["name"])
        for artist in local_artists:
            artists[artist] = artists[artist] + 1 if artist in artists else 1
            if(artist not in connections):
                connections[artist] = {}
        for first_artist in local_artists:
            for second_artists in local_artists:
                if(first_artist is not second_artists):
                    connections[first_artist][second_artists] = connections[first_artist][second_artists] + 1 if second_artists in connections[first_artist] else 1
    next = data["next"]
    if(next != None):
        get_connections(next)

get_connections(f'https://api.spotify.com/v1/playlists/{os.environ["PLAYLIST"]}/tracks')

