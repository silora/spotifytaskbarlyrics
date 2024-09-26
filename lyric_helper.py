
SP_DC = "USE_UR_OWN"

import json
import os
import time

## I DON'T KNOW IF THIS IS NECESSARY
# os.environ['SPOTIPY_CLIENT_ID'] = 'USE_UR_OWN'
# os.environ['SPOTIPY_CLIENT_SECRET'] = 'USE_UR_OWN'
# os.environ['SPOTIPY_REDIRECT_URI'] = 'USE_UR_OWN'

## IF YOU ARE USING PROXY
# os.environ['http_proxy'] = 'USE_UR_OWN'
# os.environ['https_proxy'] = 'USE_UR_OWN'
# os.environ['HTTP_PROXY'] = 'USE_UR_OWN'
# os.environ['HTTPS_PROXY'] = 'USE_UR_OWN'



import spotipy
scope = "user-read-currently-playing"
sp = spotipy.Spotify(auth_manager=spotipy.SpotifyOAuth(scope=scope))
from syrics.api import Spotify as LyricsSpotify
lrc = LyricsSpotify(SP_DC)


def get_time():
    info = sp.current_user_playing_track()["progress_ms"]
def get_track_id():
    return sp.current_user_playing_track()["item"]["id"]

def get_info(keys):
    info = sp.current_user_playing_track()
    vs = []
    for ks in keys:
        v = info
        for k in ks:
            if k in v:
                v = v[k]
            else:
                v = None
                break
        vs.append(v)
    return vs
            
            

def save_lyrics(track_id, lyrics):
    if not os.path.exists("lyrics"):
        os.makedirs("lyrics")
    if os.path.exists("lyrics/" + track_id + ".json"):
        return
    json.dump(lyrics, open("lyrics/" + track_id + ".json", "w", encoding="utf-8"))
    
def get_lyrics(track_id):
    if not os.path.exists("lyrics/" + track_id + ".json"):
        lyrics = lrc.get_lyrics(track_id)
        if lyrics is not None:
            save_lyrics(track_id, lyrics)
        else:
            print(">> LYRICS NOT FOUND")
        return lyrics
    return json.load(open("lyrics/" + track_id + ".json", "r", encoding="utf-8"))

def get_line_with_timestamp(track_id, timestamp):
    all_lyrics = get_lyrics(track_id)
    if (all_lyrics is None) or ("lyrics" not in all_lyrics) or ("syncType" not in all_lyrics["lyrics"]) or (all_lyrics["lyrics"]["syncType"] != "LINE_SYNCED"):
        return ""
    lastline = None
    for l in all_lyrics["lyrics"]["lines"]:
        if int(l["startTimeMs"]) <= int(time.time()*1000) - timestamp:
            lastline = l["words"]
        else:
            return lastline
        
def filter_line_with_timestamp(all_lyrics, timestamp):
    if (all_lyrics is None) or ("lyrics" not in all_lyrics) or ("syncType" not in all_lyrics["lyrics"]) or (all_lyrics["lyrics"]["syncType"] != "LINE_SYNCED"):
        return ""
    lastline = None
    for l in all_lyrics["lyrics"]["lines"]:
        if int(l["startTimeMs"]) <= int(time.time()*1000) - timestamp:
            lastline = l["words"]
        else:
            return lastline
    
    
def current_lyrics():
    track_id = get_track_id()
    all_lyrics = get_lyrics(track_id)
    cur_time = get_time()
    if (all_lyrics is None) or ("lyrics" not in all_lyrics) or ("syncType" not in all_lyrics["lyrics"]) or (all_lyrics["lyrics"]["syncType"] != "LINE_SYNCED"):
        return ""
    lastline = None
    for l in all_lyrics["lyrics"]["lines"]:
        if int(l["startTimeMs"]) <= cur_time:
            lastline = l["words"]
        else:
            return lastline

if __name__ == '__main__':
    breakpoint()
