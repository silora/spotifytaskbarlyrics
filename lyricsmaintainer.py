import logging
import sys
import time
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QMutex
from globalvariables import GLOBAL_OFFSET, LYRIC_FOLDER, PLAYING_INFO_PROVIDER, SP_DC, THIRD_PARTY_LYRICS_PROVIDERS, USE_SPOTIFY_LYRICS
from lyricmanager import FromSpotify, FromThirdParty, Lyrics, LyricsManager
from nowplaying import NowPlayingSystem, PlayingStatusTrigger
from stylesheets import STYLES, get_style
from enum import Enum


    


class LyricsMaintainer():
    def __init__(self, update_callback=None):
        super().__init__()
        
        self.update_callback = update_callback
        
        self.now_playing = None
        # if PLAYING_INFO_PROVIDER == "Spotify":
        #     self.now_playing = NowPlayingSpotify(update_callback=self.update_lyrics)
        # elif PLAYING_INFO_PROVIDER == "System":
        #     self.now_playing = NowPlayingSystem(update_callback=self.update_lyrics)
        # else:
        #     NowPlayingMixed(update_callback=self.update_lyrics)
        
        self.now_playing = NowPlayingSystem(update_callback=self.manager_callback, sync_interval=25, offset=150)
        
        self.providers = {}
        if USE_SPOTIFY_LYRICS:
            self.providers["Spotify"] = FromSpotify(SP_DC)
        if THIRD_PARTY_LYRICS_PROVIDERS and THIRD_PARTY_LYRICS_PROVIDERS != []:
            for provider in THIRD_PARTY_LYRICS_PROVIDERS:
                self.providers[provider] = FromThirdParty([provider])
        
        self.manager = LyricsManager(providers=self.providers)
        
        
        self._global_offset = GLOBAL_OFFSET
        
        self.lyrics = None
        self.style = STYLES["default"]
        self.style["name"] = "default"
        
        self.callback_mutex = QMutex()
        self.lyrics_mutex = QMutex()
        
        self.now_playing.start_loop()
        
    @property
    def global_offset(self):
        return self._global_offset
    
    @global_offset.setter
    def global_offset(self, value):
        print("GLOBAL OFFSET UPDATED: ", value)
        self._global_offset = value
    
    @property
    def line(self):
        # print(self.now_playing.__dict__)
        if not self.now_playing.has_lyrics:
            return None
        if not self.now_playing.current_begin_time:
            return None
        if not self.lyrics:
            return None
        if not self.now_playing.is_playing:
            return None
        l = self.lyrics.get_line_with_timestamp(int(time.time()*1000) - self.now_playing.current_begin_time - self.global_offset)
        if l:
            return l
        return None
    
    def manager_callback(self, value):
        if not self.callback_mutex.tryLock(timeout=0):
            # print("UPDATING SKIPPED")
            return
        if value == PlayingStatusTrigger.NEW_TRACK:
            self.lyrics = None
            if self.now_playing.current_track.artist == "" or self.now_playing.current_track.title == "":
                self.callback_mutex.unlock()
                return
            self.style = get_style(self.now_playing.current_track)
            if self.update_callback is not None:
                self.update_callback(value)
            self.manager.get_lyrics(self.now_playing.current_track, lambda x: self.set_lyrics(*x), lock=self.lyrics_mutex)
            self.callback_mutex.unlock()
            return
        if self.update_callback is not None:
            self.update_callback(value)
        self.callback_mutex.unlock()
        return
        
    def next_source(self):
        if not self.now_playing.has_lyrics:
            self.lyrics = None
            return
        if not self.now_playing.is_playing:
            return
        current_source = self.lyrics.source if self.lyrics else None
        next_source = None
        if current_source is None:
            next_source = list(self.providers.keys())
        else:
            current_idx = list(self.providers.keys()).index(current_source)
            next_source = list(self.providers.keys())[(current_idx + 1) % len(self.providers):]
        self.manager.get_lyrics(self.now_playing.current_track, lambda x: self.set_lyrics(*x, check_first=True), lock=self.lyrics_mutex, source=next_source)
        
    def set_empty_lyrics(self):
        self.lyrics = Lyrics([])
        self.lyrics.track = self.now_playing.current_track
        self.now_playing.has_lyrics = True
        self.manager.save_lyrics(self.now_playing.current_track, self.lyrics)
    
    @property
    def track_offset(self):
        if not self.now_playing.has_lyrics:
            return 0
        return self.lyrics.offset
    
    @track_offset.setter
    def track_offset(self, value):
        if not self.now_playing.has_lyrics:
            return
        self.lyrics.offset = value
        print("LYRIC OFFSET UPDATED: ", self.lyrics.offset)
        self.manager.save_lyrics(self.lyrics.track, self.lyrics)

    
    def set_lyrics(self, value, track=None, check_first=False):
        if check_first and not self.lyrics:
            return
        if track is not None:
            if self.now_playing.current_track != track:
                return
        self.lyrics = value
        if not self.lyrics:
            logging.info("LYRICS NOT FOUND")
            self.now_playing.has_lyrics = False
        else:
            self.now_playing.has_lyrics = True
        print("SET LYRICS: ", self.now_playing.current_track, self.lyrics is not None)

        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    lm = LyricsMaintainer()
    breakpoint()
    sys.exit(app.exec_())