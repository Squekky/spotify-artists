import spotipy
import os
import json
from dotenv import load_dotenv
from requests import post
from spotipy import SpotifyClientCredentials

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
playlist_id = os.getenv("PLAYLIST_ID")

spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

offset = 0
artistDict = {}
while True:
    songs = spotify.playlist_items(playlist_id, offset=offset)
    if len(songs['items']) < 1:
        break
    # Iterate through each song in the playlist, in sets of 100
    for song in songs['items']:
        try:
            artists = song['track']['artists']
        except TypeError:
            print(song)
        for artist in artists:
            artistName = artist['name']
            try:
                songName = song['track']['name']
            except TypeError:
                continue
            try:
                # Avoid counting duplicates
                if songName in artistDict[artistName]['songs']:
                    continue
                else:
                    # Avoid counting TV and original twice
                    if artistName == "Taylor Swift":
                        if "(Taylor's Version)" in songName:
                            # Don't count TV if original is already counted
                            if songName[:-19] in artistDict[artistName]['songs']:
                                print(songName)
                                continue
                        # Don't count original if TV is already counted
                        elif f"{songName} (Taylor's Version)" in artistDict[artistName]['songs']:
                            print(songName)
                            continue
                    artistDict[artistName]['appearances'] += 1
                    artistDict[artistName]['songs'].append(songName)
            except KeyError:
                artistDict[artistName] = {"appearances": 1, "songs": [songName]}              
    offset += 100

sortedArtists = dict(sorted(artistDict.items(), key = lambda x: x[1]['appearances'], reverse=True))

with open("topArtists.json", 'w') as file:
    json.dump(sortedArtists, file)

# Create the leaderboard
place = 0
leaderboardStr = ""
previousAmount = float('inf')
for artist in sortedArtists:
    amount = sortedArtists[artist]['appearances']
    if amount < previousAmount:
        previousAmount = amount
        place += 1
    leaderboardStr += f"{place}. {artist} - {amount}\n"

print(leaderboardStr)

# Export to text file
with open("artistLB.txt", 'w') as file:
    file.writelines(leaderboardStr)
