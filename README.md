# Minimal Spotify ~~Desktop~~ Taskbar Lyrics

**You can still tweak it to make it like a normal draggable lyrics widget though**

***UNDER DEVELOPMENT (maybe)***
***Only tested on my own pc. Can be buggy.***

**VERY PRETTY!**

| Layout |
|:------:|
| ![Layout](ExampleImages/layout.png) |


| Overview |
|:----------:|
| **Song/Artist Level Theme Customization** |
| ![song_change](gifs/charlixcx_everythingisromantic.gif) |
| **Easy Offset Setting & Auto Hide** |
| ![ctrl](gifs/lanadelrey_lovesong.gif) |
| **Lyrics Line Filter & Reformat** |
| ![fzl](gifs/yeule_softscars.gif) |
| **Sufjan Stevens** |
| ![sfj](gifs/sufjanstevens_chicago.gif) |

## Usage
```
pip install -r requirements.txt
(proxy setting)
python ./ui.py
```

## Made With
- PyQt5
- pyautogui
- pillow
- [syrics](https://github.com/akashrchandran/Syrics)
- [spotipy](https://github.com/spotipy-dev/spotipy)
- [pylrc](https://github.com/doakey3/pylrc)
- [winsdk](https://github.com/pywinrt/python-winsdk)

## With Reference To
- [This stackoverflow post](https://stackoverflow.com/questions/64290561/qlabel-correct-positioning-for-text-outline)
- [This stackoverflow post](https://stackoverflow.com/questions/79080076/how-to-set-a-qwidget-hidden-when-mouse-hovering-and-reappear-when-mouse-leaving)
- [Py Now Playing](https://github.com/ABUCKY0/py-now-playing)

## Theme Screenshots

| Default |
|:-------:|
| ![Default](ExampleImages/bigthief_littlethings.png) |

| Example 1 | Example 2 |
|:-----------:|:-----------:|
| ![Example 1](ExampleImages/bjork_armyofme.png) | ![Example 2](ExampleImages/charlixcx_ithinkaboutitallthetime.png) |
| **Example 3** | **Example 4** |
| ![Example 3](ExampleImages/lanadelrey_venicebitch.png) | ![Example 4](ExampleImages/rosalia_motomami.png) |
| **Example 5** | **Example 6** |
| ![Example 5](ExampleImages/sophie_immaterial.png) | ![Example 6](ExampleImages/yeule_softscars.png) |

- *Font not provided*


## Updates

- 20241012
    - Can stay on top of taskbar now
    - Spotify API is only called to get track id for more precised lyrics matching, playback information is handled with winsdk now
- 20241015
    - AutoHide: Stay on top of taskbar, hide when mouse hover
    - LyricsCopy: Hold ctrl when entering to copy the lyrics!
    - DefaultMode: Default mode does not need spotify API nor spotify lyrics API now!
    - LyricsCustomization:
        - Supports artist/song level customization
        - Supports line re-edit
        - Style Customization
            - font
            - background
            - entering animation

## Todo

- [x] Hide when hovered
- [x] Option for match lyrics without track id
- [x] Lyric lines filtering
- [x] Lyric customization
- [ ] Searching lyrics blocks the whole program ....
- [ ] Display behavior is not very stable (?)
- [ ] Long lyrics line scrollllllllllll