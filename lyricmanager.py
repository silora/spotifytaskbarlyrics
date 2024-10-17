import asyncio
from dataclasses import dataclass
import json
import logging
import os
import re
import syncedlyricspatch as syncedlyrics
from pylrc.parser import synced_line_regex, validateTimecode
from syrics.api import Spotify as LyricsSpotify

from globalvariables import SP_DC
from nowplaying import TrackInfo

@dataclass
class LyricLine:
    timestamp: int
    text: str

    def __init__(self, timestamp, text):
        self.timestamp = timestamp
        self.text = self.clean_text(text)
        
    def __lt__(self, other: "LyricLine"):
        return self.timestamp < other.timestamp

    def __eq__(self, other: "LyricLine"):
        if other is None:
            return False
        return self.timestamp == other.timestamp

    def __str__(self):
        return f"{self.timestamp} {self.text}"

    def shift(self, milliseconds=0):
        self.timestamp += milliseconds
        
    @classmethod
    def from_formatted_time(cls, time, text):
        if "." in time:
            minutes, seconds, milliseconds = re.match(r"\[(\d+):(\d+).(\d+)\]", time).groups()
            return cls(int(minutes) * 60000 + int(seconds) * 1000 + int(milliseconds), text)
        else:
            minutes, seconds = re.match(r"\[(\d+):(\d+)\]", time).groups()
            return cls(int(minutes) * 60000 + int(seconds) * 1000, text)
         
    def clean_text(self, text):
        text = text.strip()
        text = text.replace(u"е", "e")
        return text
        
@dataclass
class Lyrics:
    lines: list = None
    offset: int = 0
    artist: str = None
    title: str = None
    track_id: str = None
    track: TrackInfo = None
    source: str = None
    # album: str = ""
    # length: int = 0
    
    def get_line_with_timestamp(self, timestamp):
        lastline = None
        for l in self.lines:
            if int(l.timestamp + self.offset) <= timestamp:
                lastline = l
            else:
                return lastline
        return lastline
    
    @classmethod
    def from_json(cls, jsn, track: TrackInfo = None):
        lyrics = cls()
        items = []
        
        for line in jsn["lyrics"]["lines"]:
            start_time = int(line["startTimeMs"])
            items.append(LyricLine(start_time, line["words"]))
        lyrics.lines = sorted(items)
        if "offset" in jsn:
            lyrics.offset = jsn["offset"]
        lyrics.track = track
        return lyrics
    
    @classmethod
    def from_lrc(cls, lrc, track: TrackInfo = None):
        lyrics = cls()
        items = []

        for line in lrc.split("\n"):
            if not line:
                continue
            elif line.startswith('[ar:'):
                lyrics.artist = line.rstrip()[4:-1].lstrip()
            elif line.startswith('[ti:'):
                lyrics.title = line.rstrip()[4:-1].lstrip()
            # elif line.startswith('[al:'):
            #     lyrics.album = line.rstrip()[4:-1].lstrip()
            # elif line.startswith('[length:'):
            #     lyrics.length = int(line.rstrip()[8:-1].lstrip())
            elif line.startswith('[offset:'):
                lyrics.offset = int(line.rstrip()[8:-1].lstrip())
            elif synced_line_regex.match(line):
                text = ""
                first = True
                for split in reversed(line.split(']')):
                    if validateTimecode(split + "]"):
                        lyric_line = LyricLine.from_formatted_time(split + "]", text=text)
                        items.append(lyric_line)
                    else:
                        if not first:
                            split += "]"
                        else:
                            first = False
                        text = split + text

        lyrics.lines = sorted(items)
        lyrics.track = track
        return lyrics
    
    def to_json_file(self, jsn_file_path):
        jsn = {"lyrics": {"syncType": "LINE_SYNCED", "lines": [{"startTimeMs": l.timestamp, "words": l.text, "endTimeMs": "0"} for l in self.lines]}, "offset": self.offset}
        json.dump(jsn, open(jsn_file_path, "w", encoding="utf-8"), ensure_ascii=False)


class LyricsProvider:
    def __init__(self):
        pass
    def get_lyrics(self, track: TrackInfo) -> Lyrics:
        pass
    
class FromSpotify(LyricsProvider):
    def __init__(self, sp_dc):
        self._pvd = None
        self.sp_dc = sp_dc
        
    @property
    def pvd(self):
        if self._pvd is None:
            self._pvd = LyricsSpotify(self.sp_dc)
        return self._pvd
    
    def get_lyrics(self, track: TrackInfo) -> Lyrics:
        if track.id is None:
            return None
        lyrics = None
        try:
            lyrics = self.pvd.get_lyrics(track.id)
        except Exception as e:
            logging.error(e)
        if (lyrics is None) or ("lyrics" not in lyrics) or ("syncType" not in lyrics["lyrics"]) or (lyrics["lyrics"]["syncType"] != "LINE_SYNCED"):
            return None
        return Lyrics.from_json(lyrics, track)
        
class FromThirdParty(LyricsProvider):
    def __init__(self, third_parties=["Lrclib", "NetEase", "Musixmatch"]):
        self.third_parties = third_parties
    
    def get_lyrics(self, track: TrackInfo) -> Lyrics:
        lrc = None
        try:
            lrc = syncedlyrics.search(f"{track.title} {track.artist}", allow_plain_format=False, providers=self.third_parties, enhanced=False)
        except Exception as e:
                logging.error(e)
        if lrc is None:
            try:
                lrc = syncedlyrics.search(f"{track.artist} {track.title}", allow_plain_format=False, providers=self.third_parties, enhanced=False)
            except Exception as e:
                logging.error(e)
        if lrc is None:
            return None
        lyrics = Lyrics.from_lrc(lrc, track)
        if lyrics.artist is not None and lyrics.artist!= track.artist or lyrics.title is not None and lyrics.title!= track.title:
            return None
        return lyrics

class LyricsManager():
    def __init__(self, cache_dir="lyrics", providers=[]):
        self.cache_dir = cache_dir
        self.providers = providers
        self.getter = None
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        # self.loop.
    
    def get_lyrics(self, track: TrackInfo, callback: callable = None, force_refresh=False, source=None):
        # if self.getter is not None:
        #     self.getter.cancel()
        # print(">>>Getting Lyrics")
        # self.getter = self.loop.create_task(self.get_lyrics_async(track, callback))
        # print(">>>Got Lyrics")
        # # if callback is not None:
        # #     self.getter.add_done_callback(callback)
        print("GETTING LYRICS FOR ", str(track), "FROM ", source)
        callback(self.loop.run_until_complete(self.get_lyrics_async(track, force_refresh=force_refresh, source=source)))

    def save_lyrics(self, track: TrackInfo, lyrics: Lyrics):
        if lyrics is None:
            json.dump({}, open(f"{self.cache_dir}/{track.hash_id}.json", "w", encoding="utf-8"), ensure_ascii=False)
        if track.id is not None:
            lyrics.to_json_file(f"{self.cache_dir}/{track.id}.json")
        lyrics.to_json_file(f"{self.cache_dir}/{track.hash_id}.json")
        
    async def get_lyrics_async(self, track: TrackInfo, callback: callable = None, force_refresh=False, source=None):
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        ret = None
        if not force_refresh and not source:
            if track.id is not None and os.path.exists(f"{self.cache_dir}/{track.id}.json"):
                jsn = json.load(open(f"{self.cache_dir}/{track.id}.json", "r", encoding="utf-8"))
                if jsn is not None and "lyrics" in jsn and "syncType" in jsn["lyrics"] and jsn["lyrics"]["syncType"] == "LINE_SYNCED":
                    ret = Lyrics.from_json(jsn, track)    
                    if callback is not None:
                        callback(ret)
                    return ret
            if os.path.exists(f"{self.cache_dir}/{track.hash_id}.json"):
                jsn = json.load(open(f"{self.cache_dir}/{track.hash_id}.json", "r", encoding="utf-8"))
                if jsn is not None and "lyrics" in jsn and "syncType" in jsn["lyrics"] and jsn["lyrics"]["syncType"] == "LINE_SYNCED":
                    ret = Lyrics.from_json(jsn, track)
                    if callback is not None:
                        callback(ret)
                    return ret
        print(source)
        if source is None:
            source = list(self.providers.keys())
        elif isinstance(source, str):
            source = [source if source in self.providers else None]
        else:
            source = [s if s in self.providers else None for s in source]
        print("Fetching lyrics from ", source)
        for name in source:
            print("Trying ", name)
            provider = self.providers[name]
            lyrics = provider.get_lyrics(track)
            if lyrics is not None:
                self.save_lyrics(track, lyrics)
                lyrics.source = name
                ret = lyrics
            if ret is not None:
                logging.info(f"LYRICS FOUND: {track.artist} - {track.title} from {provider.__class__.__name__}")
                break
        if callback is not None:
            callback(ret)
        return ret
                
if __name__ == "__main__":
    lm = LyricsManager(providers=[FromSpotify(SP_DC), FromThirdParty()])
    breakpoint()