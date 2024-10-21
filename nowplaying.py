import asyncio
from dataclasses import dataclass
from datetime import timedelta
from enum import Enum
import hashlib
import time
from winsdk.windows.media.control import (
    GlobalSystemMediaTransportControlsSessionManager as MediaManager,
)
from winsdk.windows.storage.streams import DataReader
import subprocess
import json
from PyQt5.QtCore import QMutex, QObject, QTimer
from PyQt5.QtWidgets import QApplication
import sys
import logging
import spotipy
import os

from globalvariables import HTTP_PROXY, HTTPS_PROXY, SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, TRACKING_APP

# logging.basicConfig(level=logging.INFO)

os.environ["SPOTIPY_CLIENT_ID"] = SPOTIPY_CLIENT_ID
os.environ["SPOTIPY_CLIENT_SECRET"] = SPOTIPY_CLIENT_SECRET
os.environ["SPOTIPY_REDIRECT_URI"] = SPOTIPY_REDIRECT_URI

# if HTTP_PROXY and HTTP_PROXY != "":
#     os.environ["http_proxy"] = HTTP_PROXY
#     os.environ["HTTP_PROXY"] = HTTP_PROXY
# if HTTPS_PROXY and HTTPS_PROXY != "":
#     os.environ["https_proxy"] = HTTPS_PROXY
#     os.environ["HTTPS_PROXY"] = HTTPS_PROXY

class PlayingStatusTrigger(Enum):
    PAUSE = 1
    RESUME = 2
    NEW_TRACK = 3
    

@dataclass
class TrackInfo:
    artist: str = None
    id: str = None
    title: str = None
    length: int = None
    _hash: str = None

    def __str__(self):
        return f"{self.artist} - {self.title} [{self.id}] ({self.length})"

    def __eq__(self, value: "TrackInfo") -> bool:
        if self.id is not None and value.id is not None:
            return self.id == value.id
        if (
            self.artist is not None
            and value.artist is not None
            and self.title is not None
            and value.title is not None
        ):
            return self.artist == value.artist and self.title == value.title
        return False

    def to_json(self):
        return json.dumps(self.__dict__)
    
    def get_hash(self):
        h = hashlib.new('sha256')
        h.update(f'{self.artist} - {self.title}'.encode())
        return h.hexdigest()

    @property
    def hash_id(self):
        if self._hash is None:
            self._hash = self.get_hash()
        return self._hash

@dataclass
class PlayingInfo:
    current_track: TrackInfo
    current_begin_time: int
    is_playing: bool
    progress: int
    has_lyrics: bool = True

    @property
    def current_track_artist(self):
        return self.current_track.artist

    @current_track_artist.setter
    def current_track_artist(self, value):
        self.current_track.artist = value

    @property
    def current_track_id(self):
        return self.current_track.id

    @current_track_id.setter
    def current_track_id(self, value):
        self.current_track.id = value

    @property
    def current_track_title(self):
        return self.current_track.title

    @current_track_title.setter
    def current_track_title(self, value):
        self.current_track.title = value

    @property
    def current_track_length(self):
        return self.current_track.length

    @current_track_length.setter
    def current_track_length(self, value):
        self.current_track.length = value


class NowPlaying(QObject):
    def __init__(self, sync_interval=60000, update_callback=None):
        super().__init__()
        self.update_callback = update_callback
        self.playing_info = None
        self.sync_mutex = QMutex()
        self.sync_timer = QTimer(self)
        self.sync_timer.timeout.connect(self.sync)
        self.sync_interval = sync_interval

    def start_loop(self):
        self.sync_timer.start(self.sync_interval)

    def sync(self):
        pass

    @property
    def is_playing(self):
        return self.playing_info.is_playing if self.playing_info is not None else False

    @property
    def current_track(self):
        return self.playing_info.current_track if self.playing_info is not None else None
    
    @property
    def current_track_id(self):
        return (
            self.playing_info.current_track_id
            if self.playing_info is not None
            else None
        )

    @property
    def current_track_artist(self):
        return (
            self.playing_info.current_track_artist
            if self.playing_info is not None
            else None
        )

    @property
    def current_track_title(self):
        return (
            self.playing_info.current_track_title
            if self.playing_info is not None
            else None
        )

    @property
    def current_track_length(self):
        return (
            self.playing_info.current_track_length
            if self.playing_info is not None
            else None
        )

    @property
    def current_begin_time(self):
        return (
            self.playing_info.current_begin_time
            if self.playing_info is not None
            else None
        )

    @property
    def progress(self):
        return self.playing_info.progress if self.playing_info is not None else None

    @property
    def has_lyrics(self):
        return self.playing_info.has_lyrics if self.playing_info is not None else False

    @has_lyrics.setter
    def has_lyrics(self, value):
        self.playing_info.has_lyrics = value


class NowPlayingSystem(NowPlaying):
    def __init__(self, sync_interval=50, update_callback=None, offset=0):
        super().__init__(sync_interval, update_callback)
        self.manager = asyncio.run(self.get_media_manager())
        self.spotify_id = asyncio.run(self.get_spotify_id())
        self.has_running_process = self.spotify_id is not None
        self.is_initialized = False
        self.offset = offset

    def update_check(self, old_playing_info, new_playing_info):
        if old_playing_info is None:
            return True
        if new_playing_info.is_playing != old_playing_info.is_playing:
            return True
        if new_playing_info.current_track != old_playing_info.current_track:
            return True
        if new_playing_info.progress != old_playing_info.progress:
            return True
        return False
    
    def track_check(self, old_playing_info, new_playing_info):
        if old_playing_info is None or new_playing_info is None:
            return True
        if old_playing_info.current_track == new_playing_info.current_track:
            if old_playing_info.current_track_id is not None:
                new_playing_info.current_track_id = old_playing_info.current_track_id
            return False
        return True

    def sync(self):
        logging.debug("TRY SYNC WITH SYSTEM")
        if not self.sync_mutex.tryLock(timeout=0):
            logging.debug("SYNCING SKIPPED")
            return
        info = asyncio.run(self.get_now_playing_info())
        
        if not self.is_initialized and (info is None or not info.is_playing):
            logging.info("WAITING FOR SPOTIFY")
            self.is_initialized = True
            self.playing_info = None
            if self.update_callback is not None:
                self.update_callback(PlayingStatusTrigger.PAUSE)
            self.sync_mutex.unlock()
            return
        self.is_initialized = True
        if info is None and self.playing_info is not None:
            logging.info("SPOTIFY DOWN")
            self.is_initialized = True
            self.playing_info = None
            if self.update_callback is not None:
                self.update_callback(PlayingStatusTrigger.PAUSE)
            self.sync_mutex.unlock()
            return
        if info is None:
            self.sync_mutex.unlock()
            return
        if not info.is_playing and (self.playing_info is not None and self.playing_info.is_playing):
            logging.info("PAUSING")
            self.playing_info = info
            if self.update_callback is not None:
                self.update_callback(PlayingStatusTrigger.PAUSE)
            self.sync_mutex.unlock()
            return
        if info.is_playing and (self.playing_info is None or self.track_check(self.playing_info, info)):
            logging.info("NEW TRACK: ", info.current_track)
            self.playing_info = info
            if self.update_callback is not None:
                self.update_callback(PlayingStatusTrigger.NEW_TRACK)
            self.sync_mutex.unlock()
            return
        if info.is_playing and not self.playing_info.is_playing:
            logging.info("RESUMING")
            self.playing_info = info
            if self.update_callback is not None:
                self.update_callback(PlayingStatusTrigger.RESUME)
        if self.playing_info and self.update_check(self.playing_info, info):
            logging.info("SYNCING")
            self.playing_info = info
        self.sync_mutex.unlock()

    async def get_media_manager(self):
        return await MediaManager.request_async()

    async def get_spotify_id(self):
        logging.debug("GETTING SPOTIFY ID")
        sessions = self.manager.get_sessions()
        sessions = [session.source_app_user_model_id for session in sessions]
        print(sessions)
        if TRACKING_APP not in sessions:
            return None
        amuids = subprocess.check_output(
            ["powershell.exe", "Get-StartApps | ConvertTo-Json"],
            shell=False,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        amuids = json.loads(amuids.decode("gbk").replace("\r\n", "\n"))
        for app in amuids:
            if app["AppID"].split("\\")[-1] == TRACKING_APP:
                return TRACKING_APP
        return None

    async def get_now_playing_info(self):
        if self.spotify_id is None:
            self.spotify_id = await self.get_spotify_id()
        if self.spotify_id is None:
            logging.debug("SPOTIFY DOWN")
            return None
        sessions = self.manager.get_sessions()
        session = next(
            filter(lambda s: s.source_app_user_model_id == self.spotify_id, sessions),
            None,
        )
        if session is not None:
            info_dict = dict()
            try:
                info = await session.try_get_media_properties_async()
            except Exception as e:
                logging.debug(e)
                return None
            if info is not None:
                info_dict.update(
                    {
                        song_attr: info.__getattribute__(song_attr)
                        for song_attr in dir(info)
                        if not song_attr.startswith("_")
                    }
                )
            info = session.get_timeline_properties()
            current_time = int(time.time() * 1000)
            if info is not None:
                info_dict.update(
                    {
                        song_attr: info.__getattribute__(song_attr)
                        for song_attr in dir(info)
                        if not song_attr.startswith("_")
                    }
                )
            info = session.get_playback_info()
            if info is not None:
                info_dict.update(
                    {
                        song_attr: info.__getattribute__(song_attr)
                        for song_attr in dir(info)
                        if not song_attr.startswith("_")
                    }
                )
            if "playback_status" not in info_dict:
                return None
            return PlayingInfo(
                current_track=TrackInfo(
                    artist=info_dict["artist"] if "artist" in info_dict else None,
                    id=info_dict["track_id"] if "track_id" in info_dict else None,
                    title=info_dict["title"] if "title" in info_dict else None,
                    length=(
                        (info_dict["max_seek_time"] / timedelta(milliseconds=1))
                        if "max_seek_time" in info_dict
                        else None
                    ),
                ),
                current_begin_time=(
                    (current_time - info_dict["position"] / timedelta(milliseconds=1) + self.offset)
                    if "position" in info_dict
                    else None
                ),
                is_playing=(info_dict["playback_status"] == 4),
                progress=info_dict["position"] if "position" in info_dict else None,
            )
        return None


# class NowPlayingSpotify(NowPlaying):
#     def __init__(self, sync_interval=100000000, update_callback=None):
#         super().__init__(sync_interval, update_callback)
#         self.scope = "user-read-currently-playing"
#         self.spotify_connector = spotipy.Spotify(
#             auth_manager=spotipy.SpotifyOAuth(scope=self.scope)
#         )

#     def update_check(self, old_playing_info, new_playing_info):
#         if old_playing_info is None:
#             return True
#         if new_playing_info.is_playing != old_playing_info.is_playing:
#             return True
#         if new_playing_info.current_track != old_playing_info.current_track:
#             return True
#         if new_playing_info.progress != old_playing_info.progress:
#             return True
#         return False

#     def sync(self):
#         if self.playing_info is not None and self.playing_info.is_playing:
#             logging.debug(
#                 f"NOW PLAYING: {self.playing_info.current_track_artist} - {self.playing_info.current_track_title} ({int(time.time()*1000) - self.playing_info.current_begin_time}/{self.playing_info.current_track_length})"
#             )
#         logging.debug("TRY SYNC WITH SPOTIFY")
#         if not self.sync_mutex.tryLock(timeout=0):
#             logging.debug("SYNCING SKIPPED")
#             return
#         info = None
#         try:
#             info = asyncio.run(self.get_now_playing_info())
#         except:
#             self.sync_mutex.unlock()
#             return
#         if self.update_check(self.playing_info, info):
#             logging.debug("SYNCING")
#             self.playing_info = info
#             if self.update_callback is not None:
#                 self.update_callback(self.playing_info)
#         self.sync_mutex.unlock()

#     async def get_now_playing_info(self):
#         info, current_time = None, int(time.time() * 1000)
#         try:
#             info = self.spotify_connector.current_user_playing_track()
#         except Exception as e:
#             logging.info(e)
#             logging.info("SPOTIFY CONNECTION FAILED")
#             return None
#         if info is None:
#             return None
#         return PlayingInfo(
#             current_track=TrackInfo(
#                 artist=(
#                 info["item"]["artists"][0]["name"]
#                 if "artists" in info["item"]
#                 and len(info["item"]["artists"]) > 0
#                 and "name" in info["item"]["artists"][0]
#                 else None
#                 ),
#                 id=(
#                     info["item"]["id"] if "item" in info and "id" in info["item"] else None
#                 ),
#                 title=(
#                     info["item"]["name"]
#                     if "item" in info and "name" in info["item"]
#                     else None
#                 ),
#                 length=(
#                     info["item"]["duration_ms"]
#                     if "item" in info and "duration_ms" in info["item"]
#                     else None
#                 )
#             ),
#             current_begin_time=(
#                 (current_time - info["progress_ms"]) if "progress_ms" in info else None
#             ),
#             is_playing=info["is_playing"] if "is_playing" in info else None,
#             progress=info["progress_ms"] if "progress_ms" in info else None,
#         )


# class NowPlayingMixed(NowPlaying):
#     def __init__(self, sync_interval=50, update_callback=None):
#         super().__init__(sync_interval, update_callback)
#         self.system = NowPlayingSystem(-1, update_callback)
#         self.spotify = NowPlayingSpotify(-1, update_callback)
#         self.system_begin_time = None
#         self.synced_with_spotify = False

#     def update_check(self, old_playing_info, new_playing_info):
#         if old_playing_info is None:
#             return True
#         if new_playing_info.is_playing != old_playing_info.is_playing:
#             return True
#         if (
#             new_playing_info.current_track_artist
#             != old_playing_info.current_track_artist
#         ):
#             return True
#         if new_playing_info.current_track_title != old_playing_info.current_track_title:
#             return True
#         if new_playing_info.progress != old_playing_info.progress:
#             return True
#         return False

#     def track_check(self, old_playing_info, new_playing_info):
#         if old_playing_info is None or new_playing_info is None:
#             return True
#         if old_playing_info.current_track == new_playing_info.current_track:
#             if old_playing_info.current_track_id is not None:
#                 new_playing_info.current_track_id = old_playing_info.current_track_id
#             return False
#         return True

#     def sync(self):
#         # if self.playing_info is not None and self.playing_info.is_playing:
#         #     logging.info(
#         #         f"NOW PLAYING: {self.playing_info.current_track_artist} - {self.playing_info.current_track_title} ({int(time.time()*1000) - self.playing_info.current_begin_time}/{self.playing_info.current_track_length})"
#         #     )
#         logging.info("TRY SYNC WITH SYSTEM")
#         if not self.sync_mutex.tryLock(timeout=0):
#             logging.info("SYNCING SKIPPED")
#             return
#         info = asyncio.run(self.system.get_now_playing_info())
#         if info is None:
#             self.sync_mutex.unlock()
#             return
#         if not info.is_playing:
#             logging.info("PAUSING")
#             self.playing_info = info
#             if self.update_callback is not None:
#                 self.update_callback(self.playing_info)
#             self.sync_mutex.unlock()
#             return
#         if self.track_check(self.playing_info, info):
#             print("NEW TRACK: ", info.current_track)
#             self.playing_info = info
#             self.synced_with_spotify = False
#         if not self.synced_with_spotify:
#             logging.info("TRY SYNCING WITH SPOTIFY TO GET ID")
#             onlineinfo = asyncio.run(self.spotify.get_now_playing_info())
#             if onlineinfo is None or onlineinfo.current_track_id is None:
#                 self.synced_with_spotify = False
#                 logging.info("FAILED TO SYNC WITH SPOTIFY")
#                 self.sync_mutex.unlock()
#                 return
#             if self.playing_info.current_track != onlineinfo.current_track:
#                 self.synced_with_spotify = False
#                 logging.info("SPOTIFY NOT UPDATED YET")
#                 self.sync_mutex.unlock()
#                 return
#             self.playing_info.current_track_id = onlineinfo.current_track_id
#             self.synced_with_spotify = True
#             print("NEW TRACK: ", info.current_track)
#             if self.update_callback is not None:
#                 self.update_callback(self.playing_info)
#         elif self.system.update_check(self.playing_info, info):
#             logging.info("SYNCING")
#             self.playing_info = info
#         self.sync_mutex.unlock()


if __name__ == "__main__":
    
    def callback(trigger):
        if trigger == PlayingStatusTrigger.PAUSE:
            print("PAUSE")
        elif trigger == PlayingStatusTrigger.RESUME:
            print("RESUME")
        elif trigger == PlayingStatusTrigger.NEW_TRACK:
            print("NEW TRACK")
    
    app = QApplication(sys.argv)
    np = NowPlayingSystem(update_callback=callback)
    np.start_loop()
    breakpoint()
    sys.exit(app.exec_())
