from dotenv import load_dotenv
from pyvis.network import Network
import os
import requests
import json
from time import sleep

# API token and playlist ID is stored in .env file (TOKEN and PLAYLIST)
# You can generate your own token here: https://developer.spotify.com/console/get-playlist-tracks/
# Just click "Get Token" and if you want to visualize private playlist, select  adequate scope
load_dotenv()
headers = {'Accept': 'application/json','Content-Type': 'application/json','Authorization': f'Bearer {os.environ["TOKEN"]}'}
params = {'market': 'PL', 'limit': '100'}
cooldown = 0.5

artists = {}
connections = {}
artist_id = {}
def get_playlist_name(playlist_id):
    response = requests.get(f'https://api.spotify.com/v1/playlists/{playlist_id}', headers=headers, params=params)
    data = json.loads(response.text)
    sleep(cooldown) # For API rate limits
    return data["name"]

# Get artist photo, resolutions : 640, 320, 160
def get_artist_photo(artist_id, resolution=640):
    response = requests.get(f'https://api.spotify.com/v1/artists/{artist_id}', headers=headers, params=params)
    data = json.loads(response.text)
    id = 0
    match resolution:
        case 320:
            id = 1
        case 160:
            id = 2
    sleep(cooldown) # For API rate limits
    return data["images"][id]['url']

# Get info about artists from Spotify API and then count artists and their connections
def get_connections(link):
    response = requests.get(link, headers=headers, params=params)
    data = json.loads(response.text)
    for track in data["items"]:
        local_artists = []
        for artist in track["track"]["artists"]:
            name = artist["name"]
            local_artists.append(name)
            artist_id[name] =  artist["id"]
        for artist in local_artists:
            artists[artist] = artists[artist] + 1 if artist in artists else 1
        main_artist = local_artists[0]
        additional_artists = local_artists[1:]
        if(main_artist not in connections):
            connections[main_artist] = {}
        for additional_artist in additional_artists:
            connections[main_artist][additional_artist] = connections[main_artist][additional_artist] + 1 if additional_artist in connections[main_artist] else 1
    next = data["next"]
    sleep(cooldown) # For API rate limits
    if(next != None):
        get_connections(next)
get_connections(f'https://api.spotify.com/v1/playlists/{os.environ["PLAYLIST"]}/tracks')

# Visualize a playlists as a network
net = Network('1080px', '1920px')

total_songs = 0
for i in artists:
    total_songs += artists[i]
for artist in artists:
    songs = artists[artist]
    if(songs / total_songs >= 0.01 or songs >= 25):
        net.add_node(n_id=artist, name=artist, size=songs, shape='circularImage', image=get_artist_photo(artist_id=artist_id[artist]))
    else:
        net.add_node(n_id=artist, name=artist, size=songs)
artists_with_edges = {}
for first_artist in connections:
    for second_artist in connections[first_artist]:
        if(first_artist in artists_with_edges):
            if(second_artist in artists_with_edges[first_artist]):
                artists_with_edges[first_artist][second_artist] += connections[first_artist][second_artist]
            else:
                artists_with_edges[first_artist][second_artist] = connections[first_artist][second_artist]
        elif(second_artist in artists_with_edges):
            if(first_artist in artists_with_edges[second_artist]):
                artists_with_edges[second_artist][first_artist] += connections[first_artist][second_artist]
            else:
                artists_with_edges[second_artist][first_artist] = connections[first_artist][second_artist]
        else:
            artists_with_edges[first_artist] = {second_artist : connections[first_artist][second_artist]}
for first_artist in artists_with_edges:
    for second_artist in artists_with_edges[first_artist]:
        if(first_artist is second_artist):
            continue
        net.add_edge(first_artist, second_artist, value=artists_with_edges[first_artist][second_artist])


net.show_buttons(filter_=['physics'])
net.show(f'Playlist - {get_playlist_name(os.environ["PLAYLIST"])}.html')

