import json
import os
import sys
import spotipy
import webbrowser
import spotipy.util as util
from json.decoder import JSONDecodeError
from bs4 import BeautifulSoup
from functools import partial
from PIL import ImageTk

import pygame
import datetime
import requests
import tkinter
import time

geniusAPI = "YOUR_KEY"
geniusSecret ="YOUR_KEY""
geniusToken = "YOUR_KEY""

#button_identities = dict()
#devices = None

def get_user_ID():
    if len(sys.argv) == 2:
        return sys.argv[1]

    return 'YOUR_SPOTIFY_ID'

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

    authToken = util.prompt_for_user_token(userName, client_id='YOUR_CLIENT_ID',
                client_secret='YOUR_CLIENT_SECRET', scope= permissions, redirect_uri='http://google.com/')

    return authToken

def display_current_user(spotifyObject):
    userInfo = spotifyObject.current_user()
    print("User: {}".format(userInfo["display_name"]))
    print("Country: {}".format(userInfo["country"]))
    print("Account Type: {}".format(userInfo["product"].upper()))
    print("Number of Followers: {}".format(userInfo["followers"]["total"]))
    
def show_album_tracks(albumID, spotifyObject, LowerFrame, button_identities, song_info, buttonNum, rowNumber, RootWindow):
    #chcp 65001 <= issue this command on the command prompt to ensure encoding is utf-8 for the console
    albumTracks = spotifyObject.album_tracks(albumID, limit=50, offset=0)
    currRow = rowNumber
    button_id = buttonNum
    #print(json.dumps(albumTracks, sort_keys=True, indent=4))
    for track in albumTracks["items"]:
        trackArtists = [artist["name"] for artist in track["artists"]]
        explicitFlag = ""
        trackNumber = track["track_number"]
        trackName = track["name"]
        trackDuration = track["duration_ms"]
        formattedTime = format_time_duration(trackDuration)
        if track["explicit"]:
            explicitFlag += "EXPLICIT"

        trackNameLabel = tkinter.Label(LowerFrame, width=64, bg='SeaGreen1', text=trackName)
        trackNameLabel.grid(row=currRow, column=0, sticky=tkinter.W)

        timeLabel = tkinter.Label(LowerFrame, width=6, bg='SeaGreen1', text=formattedTime)
        timeLabel.grid(row=currRow, column=1, sticky=tkinter.W)

        explicitLabel = tkinter.Label(LowerFrame, width=8, bg='SeaGreen1', text=explicitFlag)
        explicitLabel.grid(row=currRow, column=2, sticky=tkinter.W)
        

        playButton = tkinter.Button(LowerFrame, text="PLAY",
                                    command=partial(play_track, button_id, spotifyObject, button_identities, song_info, RootWindow))
        playButton.grid(row=currRow, column=3, sticky=tkinter.W)

        button_identities[button_id] = (playButton, track["uri"])
        song_info[button_id] = [trackName, trackArtists]
        currRow += 1
        button_id += 1
                           
    return (currRow, button_id)
    
def show_artist_catalogue(artistID, spotifyObject, LowerFrame, currentRow, RootWindow):
    catalogue = spotifyObject.artist_albums(artistID, album_type='album', country='US', offset=0)
    #print(json.dumps(catalogue, sort_keys=True, indent=4))
    albums = set()      #Set to keep track of already seen albums
    button_identities = dict()
    song_info = dict()
    buttonNum = 0
    print("show_artist_catalogue lastRow: {}".format(currentRow))
    tkinter.Label(LowerFrame, anchor='w', bg='SpringGreen2', text="\nArtist's Discography:\n").grid(row=currentRow, column=0, sticky=tkinter.W)
    rowsAdded = currentRow + 1

    for album in catalogue["items"]:
        albumID = album["id"]
        albumName = album["name"]
        if albumName not in albums:
            tkinter.Label(LowerFrame, bg='red', text=albumName).grid(row=rowsAdded, column=0, sticky=tkinter.W)
            rowsAdded += 1
            moreRows,moreButtons = show_album_tracks(albumID, spotifyObject, LowerFrame, button_identities, song_info, buttonNum, rowsAdded, RootWindow)
            albums.add(albumName)

            buttonNum = moreButtons
            rowsAdded = moreRows
            rowsAdded += 1

def show_top_tracks(artistID, spotifyObject, LowerFrame, RootWindow):
    button_identities = dict()
    song_info = dict()
    buttonNum = 0
    topTracks = spotifyObject.artist_top_tracks(artistID, country='US')

    tkinter.Label(LowerFrame, anchor='w', bg='SpringGreen2', text="\nTop 10 Popular Tracks:\n").grid(row=3, column=0, sticky=tkinter.W)
    tkinter.Label(LowerFrame, width=64, bg='SpringGreen2', text="\nTrack\n").grid(row=4, column=0, sticky=tkinter.W)
    tkinter.Label(LowerFrame, width=64, bg='SpringGreen2', text="\nAlbum\n").grid(row=4, column=1, sticky=tkinter.W)
    for t in range(0, len(topTracks["tracks"])):
        trackArtists = [artist["name"] for artist in topTracks["tracks"][t]["artists"]]
        print("track artists: {}".format(trackArtists))
        trackName = topTracks["tracks"][t]["name"]
        albumName = topTracks["tracks"][t]["album"]["name"]
        tkinter.Label(LowerFrame, width=64, bg='SpringGreen1', text=trackName).grid(row=5+t, column=0, sticky=tkinter.W)
        tkinter.Label(LowerFrame, width=64, bg='SpringGreen1', text=albumName).grid(row=5+t, column=1, sticky=tkinter.W)
        playButton = tkinter.Button(
            LowerFrame, text="PLAY",
            command=partial(play_track, buttonNum, spotifyObject, button_identities, song_info, RootWindow)).grid(row=5+t, column=3, sticky=tkinter.W)

        button_identities[buttonNum] = (playButton, topTracks["tracks"][t]["uri"])
        song_info[buttonNum] = [trackName, trackArtists]
        buttonNum += 1
        
##        linkToSong = topTracks["tracks"][t]["preview_url"]
##        openBrowser = webbrowser.open(linkToSong, new=1, autoraise=True)
        
    return len(topTracks["tracks"]) + 5     

def search_artist(artistName, spotifyObject, LowerFrame, PicCanvas, RootWindow):
    searchResults = spotifyObject.search(q=artistName, limit=10, offset=0, type="artist")
    #print("---------------------search_artist()------------------")
    #print(json.dumps(searchResults, sort_keys=True, indent=4))
    
    if len(searchResults["artists"]["items"]) == 0:
        errorMessage = "Artist not found. Check spelling and try again!"
        errorLabel = tkinter.Label(LowerFrame, width=64, bg='SpringGreen2', text=errorMessage)
        errorLabel.grid(row=0,  column=0)
        return 
    
    artistID = searchResults["artists"]["items"][0]["id"]
    artistName = "Name: {}".format(searchResults["artists"]["items"][0]["name"])
    artistFollowers = "Followers: {:,}".format(searchResults["artists"]["items"][0]["followers"]["total"])
    artistGenres = "Genres: {}".format("".join(["{} / ".format(g) for g in searchResults["artists"]["items"][0]["genres"]]))

    artistLabel = tkinter.Label(LowerFrame, anchor='w', bg='SpringGreen2', text=artistName)
    artistLabel.grid(row=0, column=0, sticky=tkinter.W)

    followersLabel = tkinter.Label(LowerFrame, anchor='w', bg='SpringGreen2', text=artistFollowers)
    followersLabel.grid(row=1, column=0, sticky=tkinter.W)

    genresLabel = tkinter.Label(LowerFrame, anchor='w', bg='SpringGreen2', text=artistGenres)
    genresLabel.grid(row=2, column=0, sticky=tkinter.W)
    
    currentFrameRow = show_top_tracks(artistID, spotifyObject, LowerFrame, RootWindow)
    print("lastRow before call to artist_catalogue: {}".format(currentFrameRow))
    discography = show_artist_catalogue(artistID, spotifyObject, LowerFrame, currentFrameRow, RootWindow)
    return

def search_album(albumName, spotifyObject, LowerFrame, PicCanvas, RootWindow):
    searchResults = spotifyObject.search(q=albumName, limit=10, offset=0, type="album")
    button_identities = dict()
    song_info = dict()
    buttonNum = 0
    rowNumber = 0
    title = "Showing album results for {}...\n".format(albumName)
    tkinter.Label(LowerFrame, anchor='w', bg='SpringGreen2', underline=0, text=title).grid(row=0, column=0, sticky=tkinter.W)
    rowNumber += 1
    for album in searchResults["albums"]["items"]:
        albumName = "\nAlbum Name: {}".format(album["name"])
        artistName = "Artist: {}".format("".join(["{}  ".format(artist["name"]) for artist in album["artists"]]))
        numTracks = "Total Tracks: {}".format(album["total_tracks"])
        releaseDate = "Date Released: {}".format(format_release_date(str(album["release_date"])))
        
        tkinter.Label(LowerFrame, anchor='w', bg='SpringGreen2', text=albumName).grid(row=rowNumber, column=0, sticky=tkinter.W)
        tkinter.Label(LowerFrame, anchor='w', bg='SpringGreen2', text=artistName).grid(row=rowNumber+1, column=0, sticky=tkinter.W)
        tkinter.Label(LowerFrame, anchor='w', bg='SpringGreen2', text=numTracks).grid(row=rowNumber+2, column=0, sticky=tkinter.W)
        tkinter.Label(LowerFrame, anchor='w', bg='SpringGreen2', text=releaseDate).grid(row=rowNumber+3, column=0, sticky=tkinter.W)

        rowNumber += 4
        #More rows and more buttons will be created in the frame so make sure to update the values
        moreRows,moreButtons = show_album_tracks(album["id"], spotifyObject, LowerFrame, button_identities, song_info, buttonNum, rowNumber, RootWindow)

        rowNumber = moreRows
        buttonNum = moreButtons

def get_artist_for_genius(trackName, listOfArtists):
    #Iterate over the artists of a track and append the artistname with the track name to
    #see if the track is recognized by Genius (will be trying each artist + track name)
    # => this is because Genius sometimes associates a song with multiple artists differently
    for artist in listOfArtists:
        #Returns a Response object from requests.get(url)
        geniusResponse = request_song_info(artist, trackName)
        lyricsJSON = get_lyrics(geniusResponse, trackName, artist)
        if lyricsJSON != None:
            return lyricsJSON

    return None

def play_track(buttonID, spotifyObject, button_identities, song_info, RootWindow):
    #Track will be played on the Spotify Desktop application.
    #Application must be running (i.e. not closed) in order for this program to recognize it
    button = (button_identities[buttonID][0])
    trackName = song_info[buttonID][0]
    listOfArtists = song_info[buttonID][1]
    devices = get_user_devices(spotifyObject)   #A dictionary of user devices
        
    trackURIs = [button_identities[buttonID][1]]             #A list of URIs, where each element is a spotifyURI (aka track ID)
    spotifyObject.start_playback(devices["1"], context_uri=None, uris=trackURIs, offset=None)

    #Create Second Window
    newWindow = tkinter.Toplevel(RootWindow)
    newWindow.geometry("1250x750")              #width x height
    newWindow.resizable(False, False)
    newWindow.configure(background='black')
    #newWindow.minsize(height=750, width=750)
    
    newWindowTitle = "{} -- Lyrics".format(trackName)
    newWindow.title(newWindowTitle)

    #Request a Genius webpage and return a JSON structure that contains the results 
    lyricsJSON = get_artist_for_genius(trackName, listOfArtists)
    if lyricsJSON != None:
        #Get URL
        lyricsURL = lyricsJSON["result"]["url"]
        #Parse Web page
        output = scrape_lyrics_from_site(lyricsURL)
    else:
        output = "NO LYRICS"
        
    #Create a frame for the Text and Scrollbar widgets
    frame = tkinter.Frame(newWindow, width=750, height=750, bg='turquoise4')
    frame.pack(fill="both", expand=True)
    frame.grid_propagate(False)

    #Create a text box
    textBox = tkinter.Text(frame, borderwidth=3, state='disabled', bg='turquoise2')
    textBox.place(relx=0.1, rely=0.1, relwidth=0.8, relheight=0.8)

    #Create scroll bars and associate it with the text box
    scrBarVertical = tkinter.Scrollbar(frame, command=textBox.yview)
    scrBarVertical.place(relx=0.9, rely=0.1, relheight=0.8)
    scrBarHorizontal = tkinter.Scrollbar(frame, orient='horizontal', command=textBox.xview)
    scrBarHorizontal.place(relx=0.1, rely=0.9, relwidth=0.8)
        
    textBox["yscrollcommand"] = scrBarVertical.set
    textBox["xscrollcommand"] = scrBarHorizontal.set

    #Add the lyrics to the text box
    textBox.configure(state='normal')
    textBox.insert("1.0", output)
    textBox.configure(state='disabled')
    
def search_track(songName, spotifyObject, TextWidget, LowerFrame, PicCanvas, RootWindow):
    searchResults = spotifyObject.search(q=songName, limit=30, offset=0, type='track')
    #print(json.dumps(searchResults, sort_keys=True, indent=4))
    var = tkinter.StringVar()
    button_identities = dict()
    song_info = dict()
    buttonNum = 0
    rowNum = 0

    for track in searchResults["tracks"]["items"]:
        #var = tkinter.StringVar()
        explicitFlag = ""
        trackName = track["name"]
        trackDuration = track["duration_ms"]
        formattedTime = format_time_duration(trackDuration)
        listOfArtists = track["artists"]
        trackArtists = [artist["name"] for artist in listOfArtists]
        artists = "".join(["{} ".format(artist["name"]) for artist in track["artists"]])
        
        if track["explicit"]:
            explicitFlag += "EXPLICIT"

        #Artist Label
        artistLabel = tkinter.Label(LowerFrame, width=32, bg='SeaGreen1', text=listOfArtists[0]["name"])
        artistLabel.grid(row=rowNum, column=0)
        #Track Name Label
        trackNameLabel = tkinter.Label(LowerFrame, width=64, bg='SeaGreen1', text=track["name"])
        trackNameLabel.grid(row=rowNum, column=1)
        #Track Length Label
        timeLabel = tkinter.Label(LowerFrame, width=6, bg='SeaGreen1', text=formattedTime)
        timeLabel.grid(row=rowNum, column=2)
        #Explicit Flag Label
        explicitLabel = tkinter.Label(LowerFrame, width=8, bg='SeaGreen1', text=explicitFlag)
        explicitLabel.grid(row=rowNum, column=3)
        #Play-Track Button
        playButton = tkinter.Button(LowerFrame, text="PLAY",
                                    command=partial(play_track, buttonNum, spotifyObject, button_identities, song_info, RootWindow))
        playButton.grid(row=rowNum, column=4)
        #button_identities is a dict where key=integer : val=(Button, trackURI)
        button_identities[buttonNum] = (playButton, track["uri"])
        #song_info is a dict where key=integer : val= [trackName, ["artists"]]
        song_info[buttonNum] = [trackName, trackArtists] 

        rowNum += 1
        buttonNum += 1

    return ""
    


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

    # I added this while loop and try except clause because Genius servers will actively block requests
    # if the requests are a lot and happen frequently
    response = ''
    while response == '':
        try:
            response = requests.get(search_url, data=data, headers=headers)
            break

        except requests.exceptions.ConnectionError:
            print("Connection refused by the server...")
            print("Sleeping for 10 seconds")
            time.sleep(10)
            print("Finished sleeping, attempting to request page again")
            continue
    
    return response

def get_lyrics(responseObject, songName, artistName):
    geniusResponse = responseObject.json()
    trackFound = None
    #HTTP Request returns a number of hits, where each hit is a track that matched the query the user inputted
    #print(json.dumps(geniusResponse, sort_keys=True, indent=4))
    print()
    for hit in geniusResponse["response"]["hits"]:
        #hit["result"]["url"] will give the Genius website where the lyrics can be found
##        
##        print("Genius Result: track_name = {} // artist_name = {}".format(hit["result"]["title"], hit["result"]["primary_artist"]["name"]))
##        print("Spotify Result: track_name = {} // artist_name = {}".format(songName, artistName))
##        print("Genius song in spotify song name: {}".format(str(hit["result"]["title"]) in str(songName)))
##        print("SpotifyArtist in GeniusArtist: {}".format(str(hit["result"]["primary_artist"]["name"]).find(str(artistName))))
##        
##        print()
        if hit["result"]["title"] in songName or artistName in hit["result"]["primary_artist"]["name"]:
            trackFound = hit
            return trackFound

    print("Lyrics not found")
    return trackFound

def scrape_lyrics_from_site(url):
    #Will scrape the lyrics from the web page
    page = requests.get(url)
    htmlSoup = BeautifulSoup(page.text, 'html.parser')
    lyrics = htmlSoup.find('div', class_='lyrics').get_text()
    return lyrics

def onFrameConfigure(Canvas):
    Canvas.configure(scrollregion=Canvas.bbox("all"))

class SpotifyGUI:
    def __init__(self, spotifyObject):
        self._spotify = spotifyObject
        self._rootWindow = tkinter.Tk()
        self._lowerFrame = None
        self._optionChosen = None
        self._queryBox = None
        self._display_box = None
        self._search_button = None
        self._query = None
        ##############
        self._canvas = None
        self._picCanvas = None
        
    def _selected(self, var):
        self._optionChosen = var.get()
    
    def _store_query_and_display(self):
        #Get the query that the user inputted
        self._query = self._queryBox.get()

        #Get rid of buttons and labels that might be in the Bottom Frame (i.e. the results box)
        listWidgets = self._lowerFrame.grid_slaves()
        for widget in listWidgets:
           widget.destroy()

        print("Search Button Clicked")
        print("Option chosen: {}".format(self._optionChosen))
        print("Query: {}".format(self._query))
        
        if str(self._optionChosen) == "1":
            #Option == "Artist"
            #Artist info + top ten songs + discography will be outputted
            output = search_artist(self._query, self._spotify, self._lowerFrame, self._picCanvas, self._rootWindow)

        elif str(self._optionChosen) == "2":
            #option == "Album"
            #Album info + tracks (there will be multiple albums that are related to the query)
            output = search_album(self._query, self._spotify, self._lowerFrame, self._picCanvas, self._rootWindow)

        elif str(self._optionChosen) == "3":
            #Option == "Track"
            #25 tracks relating to the query will be displayed
            output = search_track(self._query, self._spotify, self._display_box, self._lowerFrame, self._picCanvas, self._rootWindow)
            
        else:
            print("NO OPTION CHOSEN")
            self._display_box.configure(state='normal')
            self._display_box.insert("1.0", "Click on an option above to narrow your search.\n")
            self._display_box.configure(state='disabled')


    def _reset(self, event):
        if self._queryBox.get() == "Search an artist, album, or track...":
            self._queryBox.delete(0, 'end')
            self._queryBox.insert(0, '')
            self._queryBox.config(fg='black')



    def setup_window(self):
        #devices = get_user_devices(self._spotify)
        self._rootWindow.geometry("1250x750")
        self._rootWindow.title("Spotify2")
        self._rootWindow.resizable(False, False)
        self._rootWindow.configure(background="black")

        #Add Image to the background
        self._picCanvas = tkinter.Canvas(self._rootWindow, height=750, width=1250)
        self._picCanvas.place(relx=0, rely=0, relwidth=1, relheight=1)

        backImage = ImageTk.PhotoImage(file="C:\\Users\\jmadr\\Desktop\\SpotifyProj\\landscape.png")
        backgroundLabel = tkinter.Label(self._rootWindow, image=backImage)
        backgroundLabel.place(relheight=1, relwidth=1)

        #Upper Frame (includes option bubbles, search box, and search button
        upperFrame = tkinter.Frame(self._rootWindow, bg='SpringGreen2', bd=5)
        upperFrame.place(relx=0.5, rely=0.1, relwidth=0.75, relheight=0.1, anchor='n')

        #Search option bubbles
        var = tkinter.IntVar()
        option1 = tkinter.Radiobutton(upperFrame, bg='SpringGreen2', text="Artist", variable=var, value=1, command=lambda : self._selected(var))
        option2 = tkinter.Radiobutton(upperFrame, bg='SpringGreen2', text="Album", variable=var, value=2, command=lambda : self._selected(var))
        option3 = tkinter.Radiobutton(upperFrame, bg='SpringGreen2', text="Track", variable=var, value=3, command=lambda : self._selected(var))   
        option1.grid(row=0, column=0)
        option2.grid(row=0, column=1)
        option3.grid(row=0, column=2)

        #Search Box
        self._queryBox = tkinter.Entry(upperFrame, font=40)
        self._queryBox.place(rely=0.5, relwidth=0.75, relheight=0.5)
        self._queryBox.insert(0, "Search an artist, album, or track...")
        self._queryBox.bind("<Button-1>", self._reset)
        self._queryBox.config(fg="grey")

        #Search Button
        self._search_button = tkinter.Button(upperFrame, text="Search", command=self._store_query_and_display, relief="raised")
        self._search_button.place(relx=0.80, rely=0.5, relwidth=0.2, relheight=0.5)

        #Botton Frame (with Canvas)
        self._canvas = tkinter.Canvas(self._rootWindow, borderwidth=5, background='SpringGreen2')
        self._canvas.place(relx=0.5, rely=0.25, relwidth=0.75, relheight=0.70, anchor='n')
            
        self._lowerFrame = tkinter.Frame(self._canvas, bg='SpringGreen2')   #Frame will contain the widgets

        #Scrollbars for the Bottom Frame
        verticalBar = tkinter.Scrollbar(self._rootWindow, command=self._canvas.yview)
        verticalBar.place(relx=0.87, rely=0.25, relheight=0.70)
        horizontalBar = tkinter.Scrollbar(self._rootWindow, orient="horizontal", command=self._canvas.xview)
        horizontalBar.place(relx=0.125, rely=0.95, relwidth=0.75)

        #Following lines will ensure that the Frame can contain widgets and that it has the scrolling functionality
        self._canvas.configure(yscrollcommand=verticalBar.set)
        self._canvas.configure(xscrollcommand=horizontalBar.set)

        self._canvas.create_window((4,4), window=self._lowerFrame, anchor='nw')
        self._lowerFrame.bind("<Configure>", lambda event, canvas=self._canvas: onFrameConfigure(self._canvas))

        #Command to ensure the program execution is concentrated on the GUI application
        self._rootWindow.mainloop()


if __name__ == "__main__":
    userName = get_user_ID()
    token = ask_user_permission(userName)
    spotifyObject = spotipy.Spotify(auth=token)
    display_current_user(spotifyObject)

    spotifyGUI = SpotifyGUI(spotifyObject)
    spotifyGUI.setup_window()

