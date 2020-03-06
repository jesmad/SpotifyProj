import json
import os
import sys
import spotipy
import webbrowser
import spotipy.util as util
from json.decoder import JSONDecodeError
from bs4 import BeautifulSoup
from functools import partial
import pygame
import datetime
import requests
import tkinter


#import vlc
#C:\Users\jmadr\Downloads\pygame-1.9.4-cp35-cp35m-win32.whl
#from pygame import mixer
#C:\Users\jmadr\Desktop\SpotifyProj\spotify2.py
#print(json.dumps(OBJECT, sort_keys=True, indent=4))

geniusAPI = "QM0uyGH_vtnAlWVoKChBeZr7ARcpb2UkOMySfNypFax7LZtQs2ZGKya-mKgyoqar"
geniusSecret = "3Tk5QTJSCqlf9I-6EBMRobEv4FTDWcWwJDsU5qTL1NjiTOkSPAV4psH4lNSsCzOQAViat4ioyi4M6ec_vY2xjg"
geniusToken = "1mOv7wcXKHY43ySP2UzCQM3kIPBuGI9e8sfG8NAp-91QlkxhzyXBHYFqQNX8x0AE"
button_identities = dict()
#devices = None

def get_user_ID():
    if len(sys.argv) == 2:
        return sys.argv[1]

    return '223zzazac4geeqx76lonsmmqy?si=VNYC3hF2TSahT90JCZs4UQ'

def format_time_duration(time):
    time = str(datetime.timedelta(milliseconds=time))       #"HR:MIN:SEC.MILLSEC"
    duration = time.split(":")
    formattedTime = duration[1] + ":" + duration[2][0:2]
    return formattedTime

def format_release_date(date):
    info = date.split("-")  #=> ["2019", "03", "08"]
    if (len(info) == 3):
        formattedDate = info[1] + "/" + info[2] + "/" + info[0]

    elif (len(info) == 2):
        formattedDate = info[1] + "/" + info[0]

    elif (len(info) == 1):
        formattedDate = info[0]
    else:
        formattedDate = "N/A"

    return formattedDate

def ask_user_permission(userName):
    permissions= "user-read-private user-read-playback-state user-modify-playback-state"

    authToken = util.prompt_for_user_token(userName, client_id='ce48c997120f4744a9bdc2bd9d65f315',
                client_secret='7ea6b9fbfab949d1bbd33ebd94ef18d4', scope= permissions, redirect_uri='http://google.com/')

    return authToken

def display_current_user(spotifyObject):
    userInfo = spotifyObject.current_user()
    print("User: {}".format(userInfo["display_name"]))
    print("Country: {}".format(userInfo["country"]))
    print("Account Type: {}".format(userInfo["product"].upper()))
    print("Number of Followers: {}".format(userInfo["followers"]["total"]))

def show_album_tracks(albumID, spotifyObject):
    #chcp 65001 <= issue this command on the command prompt to ensure encoding is utf-8 for the console
    albumTracks = spotifyObject.album_tracks(albumID, limit=50, offset=0)
    for track in albumTracks["items"]:
        explicitFlag = ""
        trackNumber = track["track_number"]
        trackName = track["name"]
        trackDuration = track["duration_ms"]
        formattedTime = format_time_duration(trackDuration)
        if track["explicit"]:
            explicitFlag += "EXPLICIT"

        print("{:<3} {:^75} ({}) {}".format(trackNumber, trackName, formattedTime, explicitFlag))

def show_artist_catalogue(artistID, spotifyObject):
    catalogue = spotifyObject.artist_albums(artistID, album_type='album', country='US', offset=0)
    #print(json.dumps(catalogue, sort_keys=True, indent=4))
    albums = set()      #Set to keep track of already seen albums
    print("Artist's Discography:")
    print()
    for album in catalogue["items"]:
        albumID = album["id"]
        albumName = album["name"]
        if albumName not in albums:
            print(albumName)
            show_album_tracks(albumID, spotifyObject)
        albums.add(albumName)
        print()

def show_top_tracks(artistID, spotifyObject):
    topTracks = spotifyObject.artist_top_tracks(artistID, country='US')
    print()
    print("Top 10 Popular Songs: ")
    for t in range(0, len(topTracks["tracks"])):
        print("{}. {}".format(t+1, topTracks["tracks"][t]["name"]))
        print("\t--from {}".format(topTracks["tracks"][t]["album"]["name"]))
##        linkToSong = topTracks["tracks"][t]["preview_url"]
##        openBrowser = webbrowser.open(linkToSong, new=1, autoraise=True)
    print()
    show_artist_catalogue(artistID, spotifyObject)

def search_artist(artistName, spotifyObject):
    searchResults = spotifyObject.search(q=artistName, limit=10, offset=0, type="artist")
    artistID = searchResults["artists"]["items"][0]["id"]
    print()
    print("Name: {}".format(searchResults["artists"]["items"][0]["name"]))
    print("Followers: {:,}".format(searchResults["artists"]["items"][0]["followers"]["total"]))
    print("Genres: {}".format("".join(["{} / ".format(g) for g in searchResults["artists"]["items"][0]["genres"]])))

    show_top_tracks(artistID, spotifyObject)
    print()

def search_album(albumName, spotifyObject):
    searchResults = spotifyObject.search(q=albumName, limit=10, offset=0, type="album")
    print()
    print("Showing album results for {}...".format(albumName))
    for album in searchResults["albums"]["items"]:
        print("Album Name: {}".format(album["name"]))
        print("Artist: {}".format("".join(["{}  ".format(artist["name"]) for artist in album["artists"]])))
        print("Number of Tracks: {}".format(album["total_tracks"]))
        print("Album-Type: {}".format(str(album["album_type"]).upper()))
        print("Release Date: {}".format(format_release_date(str(album["release_date"]))))
        print("Tracks: ")
        show_album_tracks(album["id"], spotifyObject)
        print("--------------------------------------------------------------------")

def play_track(devices, tracks):
    #devices => {"1" : "deviceID", "2" : ...}
    #tracks => {"1" : ("trackID", "trackName", "trackArtist"), ...}
    
    playSongFlag = input("Do you want to play one of these songs? Yes/No: ")
    if playSongFlag == "No":
        return
    
    trackNum = input("Enter song number that you want to play: ")
    deviceNum = input("Enter the number of the device you want play the track with: ")
    print()
    trackName = tracks[trackNum][1]
    trackArtist = tracks[trackNum][2]
    
    trackURIs = [tracks[str(trackNum)][0]]             #A list of URIs, where each element is a spotifyURI (aka track ID)
    spotifyObject.start_playback(devices[deviceNum], context_uri=None, uris=trackURIs, offset=None)
    response = request_song_info(trackArtist, trackName)
    foundLyricsJSON = get_lyrics(response, trackName, trackArtist)
    #print(json.dumps(foundLyrics, sort_keys=True, indent=4))
    if foundLyricsJSON == None:
        return None
    
    lyricsURL = foundLyricsJSON["result"]["url"]
    return lyricsURL

def search_track(songName, spotifyObject):
    searchResults = spotifyObject.search(q=songName, limit=10, offset=0, type='track')
    trackNum_ID = dict()    #Stores key=trackNumber : val=trackID
    print(json.dumps(searchResults, sort_keys=True, indent=4))
    trackNumber = 1
    for track in searchResults["tracks"]["items"]:
        explicitFlag = ""
        trackDuration = track["duration_ms"]
        formattedTime = format_time_duration(trackDuration)
        artists = "".join(["{} ".format(artist["name"]) for artist in track["artists"]])
        if track["explicit"]:
            explicitFlag += "EXPLICIT"

        print("{:<3} {:^75} ({}) {}".format(trackNumber, track["name"], formattedTime, explicitFlag))
        print("\t\t--by {} / {}".format(artists, track["album"]["name"]))
        print()
        trackNum_ID[str(trackNumber)] = (track["uri"], track["name"], track["artists"][0]["name"])  #ex: {"1" : (trackID, trackName, artist)}
        trackNumber += 1

    return trackNum_ID

def get_user_devices(spotifyObject):
    #pip3 install spotipy did not have devices()
    #had to manually download files from GitHub and extract them and
    #copy them to C:\Python35\Lib\site-packages\spotipy
    #Gives the devices where Spotify is being used
    devices = dict()    #{number : deviceID}
    deviceNum = 1
    userDevices = spotifyObject.devices()
    print("Devices running Spotify:")
    print()
    for device in userDevices["devices"]:
        print("Device ({})".format(deviceNum))
        print("Type: {}".format(device["type"]))
        print("Name: {}".format(device["name"]))
        print()
        devices[str(deviceNum)] = device["id"]
        deviceNum += 1

    return devices

def get_currently_playing_song(spotifyObject):
    #songPlaying = spotifyObject.currently_playing()
    songPlaying = spotifyObject.current_user_playing_track()
    print(json.dumps(songPlaying, sort_keys=True, indent=4))

########################################################################
#GENIUS
def request_song_info(artistName, songName):
    print("Playing {1} by {0}".format(artistName, songName))
    base_url = "https://api.genius.com"
    headers = {"Authorization": "Bearer " + geniusToken}
    search_url = base_url + "/search"
    data = {"q": songName + " " + artistName}
    response = requests.get(search_url, data=data, headers=headers)
    
    return response

def get_lyrics(responseObject, songName, artistName):
    geniusResponse = responseObject.json()
    trackFound = None
    #HTTP Request returns a number of hits, where each hit is a track that matched the query the user inputted
    #print(json.dumps(geniusResponse, sort_keys=True, indent=4))
    print()
    for hit in geniusResponse["response"]["hits"]:
        #hit["result"]["url"] will give the Genius website where the lyrics can be found
        
        print("Genius Result: track_name = {} // artist_name = {}".format(hit["result"]["title"], hit["result"]["primary_artist"]["name"]))
        print("Spotify Result: track_name = {} // artist_name = {}".format(songName, artistName))
        print("Genius song in spotify song name: {}".format(str(hit["result"]["title"]) in str(songName)))
        print("SpotifyArtist in GeniusArtist: {}".format(str(hit["result"]["primary_artist"]["name"]).find(str(artistName))))
        
        print()
        if hit["result"]["title"] in songName or artistName in hit["result"]["primary_artist"]["name"]:
            trackFound = hit
            return trackFound

    print("Lyrics not found")
    return trackFound

def scrape_lyrics_from_site(url):
    page = requests.get(url)
    htmlSoup = BeautifulSoup(page.text, 'html.parser')
    lyrics = htmlSoup.find('div', class_='lyrics').get_text()
    print(lyrics)
    return

def menu(spotifyObject):
    print()
    print("----------------------Welcome to Spotify----------------------------------")
    print()

    while True:
        print()
        print("You can do the following...")
        print("1 => search for artist, 2 => search for album, 3 => search and/or play a song, 4 => get current song playing, 5 => exit")
        option = input("Enter 1, 2, 3, 4, or 5: ")
        print()
        if option == "1":
            artistName = input("Enter artist name: ")
            search_artist(artistName, spotifyObject)

        elif option == "2":
            albumName = input("Enter album name: ")
            search_album(albumName, spotifyObject)

        elif option == "3": 
            songName = input("Enter song name: ")
            #Display the track results from the query
            tracks = search_track(songName, spotifyObject)  #Returns a dictionary where key=trackNum : val=(spotifyURI, songName, artistName)          
            devices = get_user_devices(spotifyObject)       #Returns a dictionary where key=deviceNum : val=deviceID
            lyricsURL = play_track(devices, tracks)         #Play the track and return the URL to the lyrics of the song

            if lyricsURL == None:
                continue

            #Display lyrics
            print("Lyrics from {}".format(lyricsURL))
            print(15*"-")
            scrape_lyrics_from_site(lyricsURL)
            
        elif option == "4":
            get_user_devices(spotifyObject)
            get_currently_playing_song(spotifyObject)

        elif option == "5":
            return
        
        else:
            print("Invalid action")

if __name__ == "__main__":
    userName = get_user_ID()
    token = ask_user_permission(userName)
    spotifyObject = spotipy.Spotify(auth=token)
    display_current_user(spotifyObject)
    menu(spotifyObject)
