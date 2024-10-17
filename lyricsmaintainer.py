import logging
import sys
import time
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QMutex
from globalvariables import GLOBAL_OFFSET, LYRIC_FOLDER, PLAYING_INFO_PROVIDER, SP_DC, THIRD_PARTY_LYRICS_PROVIDERS, USE_SPOTIFY_LYRICS
from lyricmanager import FromSpotify, FromThirdParty, Lyrics, LyricsManager
from nowplaying import NowPlayingMixed, NowPlayingSpotify, NowPlayingSystem
from stylesheets import STYLES, get_style

class LyricsMaintainer():
    def __init__(self):
        super().__init__()
        self.now_playing = None
        if PLAYING_INFO_PROVIDER == "Spotify":
            self.now_playing = NowPlayingSpotify(update_callback=self.update_lyrics)
        elif PLAYING_INFO_PROVIDER == "System":
            self.now_playing = NowPlayingSystem(update_callback=self.update_lyrics)
        else:
            NowPlayingMixed(update_callback=self.update_lyrics)
        
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
        self.updateMutex = QMutex()
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
        # add delay
        # print("OFFSET: ", self.lyrics.offset, "+", self.global_offset)
        l = self.lyrics.get_line_with_timestamp(int(time.time()*1000) - self.now_playing.current_begin_time + 600 + self.global_offset)
        if l:
            # print(int(time.time()*1000) - self.now_playing.current_begin_time + 600 + self.global_offset, l.timestamp)
            return l
        return None
    
    def update_lyrics(self, playing_info=None):
        if not self.updateMutex.tryLock(timeout=0):
            # print("UPDATING SKIPPED")
            return
        if not self.now_playing.playing_info:
            # print("NO INFO")
            self.updateMutex.unlock()
            return
        if not self.now_playing.has_lyrics:
            # print("NOT FOUND LAST TIME")
            self.lyrics = None
            self.updateMutex.unlock()
            return
        if not self.now_playing.is_playing:
            # print("NOT PLAYING")
            # self.lyrics = None
            self.updateMutex.unlock()
            return
        print("GETTING LYRICS")
        self.lyrics = None
        if self.now_playing.current_track.artist == "" or self.now_playing.current_track.title == "":
            self.updateMutex.unlock()
            return
        self.manager.get_lyrics(self.now_playing.current_track, lambda x: self.set_lyrics(x))
        
    def next_source(self):
        if not self.updateMutex.tryLock(timeout=0):
            # print("UPDATING SKIPPED")
            return
        if not self.now_playing.has_lyrics:
            # print("NOT FOUND LAST TIME")
            self.lyrics = None
            self.updateMutex.unlock()
            return
        if not self.now_playing.is_playing:
            # print("NOT PLAYING")
            # self.lyrics = None
            self.updateMutex.unlock()
            return
        current_source = self.lyrics.source if self.lyrics else None
        next_source = None
        if current_source is None:
            next_source = list(self.providers.keys())
        else:
            current_idx = list(self.providers.keys()).index(current_source)
            next_source = list(self.providers.keys())[(current_idx + 1) % len(self.providers):]
        # print("GETTING LYRICS FROM NEXT SOURCE: ", next_source)
        self.manager.get_lyrics(self.now_playing.current_track, lambda x: self.set_lyrics(x, check_first=True), source=next_source)
        
    def set_empty_lyrics(self):
        self.lyrics = Lyrics([])
        self.lyrics.track = self.now_playing.current_track
        self.now_playing.has_lyrics = True
        self.manager.save_lyrics(self.now_playing.current_track, self.lyrics)
    
    @property
    def song_offset(self):
        if not self.now_playing.has_lyrics:
            return 0
        return self.lyrics.offset
    
    @song_offset.setter
    def song_offset(self, value):
        if not self.now_playing.has_lyrics:
            return
        self.lyrics.offset = value
        print("LYRIC OFFSET UPDATED: ", self.lyrics.offset)
        self.manager.save_lyrics(self.lyrics.track, self.lyrics)

    
    def set_lyrics(self, value, check_first=False):
        if check_first and not self.lyrics:
            return
        self.lyrics = value
        self.style = get_style(self.now_playing.current_track)
        if not self.lyrics:
            logging.info("LYRICS NOT FOUND")
            self.now_playing.has_lyrics = False
        else:
            self.now_playing.has_lyrics = True
        self.updateMutex.unlock()
        
        print("SET LYRICS: ", self.now_playing.current_track, self.lyrics is not None)

        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    lm = LyricsMaintainer()
    breakpoint()
    sys.exit(app.exec_())