##### APPEARANCE
TAKSBAR_HEIGHT = 70

##### OFFSET
GLOBAL_OFFSET = 0

##### LYRIC FOLDER
LYRIC_FOLDER = "lyrics"

##### PROXY

### If you need to use proxy, like vpn......(iykyk)
HTTP_PROXY = ""
HTTPS_PROXY = ""

##### TRACKING APP (Only works for System Playing Info Provider)

### I also tried PotPlayer/Arc Browser and it kinda works?!?!
TRACKING_APP = "Spotify.exe"

##### LYRIC PROVIDER

### Track ID is needed to get lyrics from Spotify
### Spotify lyrics can be out of sync at a lot of times, but it prevents mixing up lyrics from different versions
USE_SPOTIFY_LYRICS = False
# If True, you need to set SP_DC
SP_DC = ""

### Third party lyrics providers
### AVAILABLE PROVIDERS (from syncedlyrics): Musixmatch, Lrclib, Deezer, NetEase, Megalobiz, Genius
### Netease DOES NOT PROVIDE BJORK SONGS!!!!!
THIRD_PARTY_LYRICS_PROVIDERS = ["Lrclib", "NetEase", "Musixmatch"]

### DOES NOT conflict with each other, but spotify lyrics are prioritized, then third party lyrics providers in the list order


##### PLAYIING INFO PROVIDER

### AVAILABLE OPTIONS: Spotify, System, Mixed

### Spotify: (Not Available Now) Uses Spotify API to get the current playing track. If the interval is set too long, it's much irresponsive to playstate changes (e.g. pause, next track, progress). If the interval is set too short, too much request can lead to rate limiting :( . DOES PROVIDE TRACK ID.
### System: Use Windows Runtime API to get the current playing track. You can call them as frequently as you want, but the actual song progress information is updated every four second (at least on my pc, you are welcomed to test it on yours. I dont know whether its a winsdk thing). Song changes are instant, pausing can sometimes be delayed for whatever reason. DOES NOT PROVIDE TRACK ID.
### Mixed: (Not Available Now) Uses Spotify API to get the current playing track id, then uses System to get all the rest information. Spotify API is only called on track change. DOES PROVIDE TRACK ID.
PLAYING_INFO_PROVIDER = "System"

### If you are using Spotify as the playing info provider, you need to set the Spotify API information (or not? I did remember there is a login popup, anyway chi....)
SPOTIPY_CLIENT_ID = ""
SPOTIPY_CLIENT_SECRET = ""
SPOTIPY_REDIRECT_URI = ""

