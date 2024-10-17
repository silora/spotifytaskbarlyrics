
import regex as re
from lyricmanager import TrackInfo

def yeule_style(line):
    original = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    output = "ѧ𝛃ℂᴰ∃ፑᏀਮ𝕀لԟᒶṂℕ❍𝕡ℚ℟ᎦT⨿ᐺሡㄨ𝕐Ꮓ𝖆ƀ𝘤Ժ𝘦𝖋ցħɨڵꝂ╽₥դØᵱᒅ𝐫ક𝕥նᏤ⍵𝕏Ỿ𝐳"
    ret = ""
    line = line.replace("Softscars", "ₛof̷̢̨̛̙̦̮͖̘͍͆♰ꙅᶜà̵̡͈̥͚́̽͛̍̕͘ ̺ ̝ ʳₛ").replace("softscars", "ₛof̷̢̨̛̙̦̮͖̘͍͆♰ꙅᶜà̵̡͈̥͚́̽͛̍̕͘ ̺ ̝ ʳₛ")
    for char in line:
        if char in original:
            ret += output[original.index(char)]
        elif char == " ":
            ret += "  "
        else:
            ret += char
    return ret


def replace_all(line, matches, replacement, cap_first=True):
    line = line.strip()
    if matches is None:
        return line
    c_list = list(line)
    for match in matches:
        c_list[match.start()] = replacement
        if cap_first:
            if match.start() == 0:
                c_list[0] = c_list[0][:1].upper() + c_list[0][1:]
            else:
                i = match.start() - 1
                while i >= 0 and c_list[i] in " ":
                    i -= 1
                if c_list[i] in ".!?":
                    c_list[match.start()] = c_list[match.start()][:1].upper() + c_list[match.start()][1:]
        for i in range(match.start() + 1, match.end()):
            c_list[i] = ""
    return "".join(c_list)

def uncensor(line):
    uncensor_dict = {
        "fuck": r"(\*\*\*\*(?=( it|ing|er|'s sake| sake|'em | 'em| em| him| her| them)))|((?<=(as ))\*\*\*\*)|((F|(?<= )f)[^a-tw-yzA-TW-YZ]?[^abd-yzABD-YZ]?[^a-jl-yzA-JL-YZ]?(?=([ .!?'\"]|ed |ing |er |in |in' |ers|ed-up )))",
        "shit": r"((?<=(as ))\*\*\*\*)|((S|(?<= )s)[^a-gi-yzA-GI-YZ]?[^a-hj-yzA-HJ-YZ]?[^a-su-yzA-SU-YZ]?(?=[ .!?'\"]))",
        "bitch": r"(\*\*\*\*\*(?=(es| ass|-ass|ass| gon)))|((?<=(my |stupid |that ))\*\*\*\*\*)|((B|(?<= )b)[^a-hj-yzA-HJ-YZ]?[^a-su-yzA-SU-YZ]?[^abd-yzABD-YZ]?[^a-gi-yzA-GI-YZ]?(?=([ .!?'\"]|es )))",
    }
    for k, v in uncensor_dict.items():
        line = replace_all(line, re.finditer(v, line), k)
    return line

def default_formatter(line):
    if any([line.strip().startswith(_) for _ in ["作词", "编曲", "制作", "作曲", "混音", "人声", "母带", "监制", "词", "曲", "录", "附加制作", "鼓", "贝斯", "吉他"]]):
        return ""
    if line == "":
        return "♬"
    else:
        return uncensor(line)
    
STYLES = {
    "default": {
        "background-color": "#00000000",
        
        "font-color": "#bbbbbb",
        "font-family": "Consolas, ",
        "font-size": "30px",
        "font-weight": "regular",
        
        
        "line-color": "#b2b2b2",
        "line-width": 0.3,

        "use-shadow": True,
        "shadow-color": "#ffff97",
        "shadow-offset": [0, 0],
        "shadow-radius": 10,
        
        "flip-text": False,
        
        "format": default_formatter,
        
        "entering": "fadein"
    },
    "brat remix": {
        # "background-color": "#8bcc00",
        "background-color": "qradialgradient(spread:pad, cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0, stop:0 #8bcc00, stop:1 #00000000)",
        
        "font-color": "#000000",
        "font-family": "Arial Narrow",
        "font-size": "30px",
        
        "line-color": "#000000",
        "line-width": 0,

        "shadow-color": "#000000",
        "shadow-offset": [0, 0],
        "shadow-radius": 7,
        
        "flip-text": True,
        
        "rule": lambda track: (track.artist.lower() == "charli xcx" and any([all([s in track.title.lower().replace("‘", "'").replace("’", "'") for s in _ ]) for _ in [("360", "robyn"), ("club classics", "bb trickz"), ("sympathy is a knife", "ariana grande"), ("i might say something stupid", "the 1975"), ("talk talk", "troye sivan"), ("von dutch", "a. g. cook"), ("everything is romantic", "caroline polachek"), ("rewind", "bladee"), ("so i", "a. g. cook"), ("girl, so confusing", "lorde"), ("apple", "the japanese house"), ("b2b", "tinashe"), ("mean girls", "julian casablancas"), ("i think about it all the time", "bon iver"), ("365", "shygirl"), ("guess", "billie eilish"), ("spring breakers", "kesha")]]))
    },
    "brat": {
        # "background-color": "#8ace00",
        "background-color": "qradialgradient(spread:pad, cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0, stop:0 #8ace00, stop:1 #00000000)",
        
        "font-color": "#000000",
        "font-family": "Arial Narrow",
        "font-size": "30px",
        "font-weight": "thin",
        
        "line-color": "#000000",
        "line-width": 0,

        "shadow-color": "#000000",
        "shadow-offset": [0, 0],
        "shadow-radius": 7,
        
        "rule": lambda track: (track.artist.lower() == "charli xcx" and any([_ in track.title.lower().replace("‘", "'").replace("’", "'") for _ in ["360", "club classics", "sympathy is a knife", "i might say something stupid", "talk talk", "von dutch", "everything is romantic", "rewind", "so i", "girl, so confusing", "apple", "b2b", "mean girls", "i think about it all the time", "365", "guess", "spring breakers", "hello goodbye", "in the city"]]))
    },
    "crash": {
        "font-color": "#1640be",
        "font-family": "Onyx BT",
        "font-size": "40px",
        
        "line-color": "#e8ebf5",
        "line-width": 0,
        
        "use-shadow": False,

        "rule": lambda track: (track.artist.lower() == "charli xcx" and any([_ in track.title.lower().replace("‘", "'").replace("’", "'") for _ in ["crash", "new shapes", "good ones", "constant repeat", "beg for you", "move me", "baby", "lightning", "every rule", "yuck", "used to know me", "twice", "selfish girl", "how can i not know what i need right now", "sorry if i hurt you", "what you think about me"]]))
    }, 
    "vroom vroom": {
        "font-color": "#0000000099",
        "font-family": "Rawhide Raw 2012",
        "font-size": "27px",
        
        "line-color": "#e3e3e3",
        "line-width": 1.1,
        
        "shadow-color": "#757575",
        "shadow-offset": [1.5, 1.5],
        "shadow-radius": 3,
        
        "rule": lambda track: (track.artist.lower() == "charli xcx" and any([_ in track.title.lower().replace("‘", "'").replace("’", "'") for _ in ["vroom vroom", "paradise", "trophy", "secret"]])),
        
        "format": lambda line: "".join([_ for _ in line if _ in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ ,.-"]).upper().replace("R ", "r ")
    },
    "motomami": {   
        "font-color": "#FF0000",
        "font-family": "Motomami",
        "font-size": "65px",
        
        "line-color": "#ffffff",
        "line-width": 3,

        "shadow-color": "#FF0000",
        "shadow-offset": [0, 0],
        "shadow-radius": 30,
        
        "rule": lambda track: (track.artist.lower() in ["rosalia", "rosalía"] and any([_ in track.title.lower().replace("‘", "'").replace("’", "'") for _ in ["saoko", "candy", "la fama", "bulería", "buleria", "chicken teriyaki", "hentai", "bizcochito", "g3 n15", "motomami", "diablo", "delirio de grandeza", "cuuuuuuuuuute", "como un g", "abcdefg", "la combi versace", "sakura", "thank yu :)", "despechá", "despecha", "aislamiento", "la kilié", "la kilie", "lax", "chiri"]]))
    },
    "arca": {
        "font-color": "white",
        "font-family": "KiCk",
        "font-size": "60px",
        
        "line-color": "#858585",
        "line-width": 2,
        
        "shadow-color": "white",
        
        "rule": lambda track: (track.artist.lower() == "arca"),
        
        "format": lambda line: line.replace("ñ", "n").replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
    },
    "post": {
        "font-color": "#d58fe8",
        "font-family": "Bjork",
        "font-size": "40px",
        
        "line-color": "#a22929",
        "line-width": 1,
        
        "shadow-color": "#a22929",
        "shadow-offset": [2, 2],
        "shadow-radius": 8,
        
        "rule": lambda track: (track.artist.lower() in ["bjork", "björk"] and any([_ in track.title.lower().replace("‘", "'").replace("’", "'") for _ in ["army of me", "hyperballad", "hyper-ballad", "the modern things", "it's oh so quiet", "enjoy", "you've been flirting again", "isobel", "possibly maybe", "i miss you", "cover me", "headphones"]])),
        
        "format": lambda line: "".join([_ for _ in line if _ in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ ♬"])
    },
    "vespertine": {
        "font-color": "#ffffff",
        "font-family": "vespertine",
        "font-size": "40px",
        
        "line-width": 1,
        
        "use-shadow": False,
        
        "rule": lambda track: (track.artist.lower() in ["bjork", "björk"] and any([_ in track.title.lower().replace("‘", "'").replace("’", "'") for _ in ["hidden place", "cocoon", "it's not up to you", "undo", "pagan poetry", "frosti", "aurora", "an echo, a stain", "sun in my mouth", "heirloom", "harm of will", "unison", "stonemilker", "lionsong", "history of touches", "black lake", "family", "notget", "atom dance", "mouth mantra", "quicksand"]]))
    },
    "renaissance": {
        "font-color": "#e0e0e0",
        "font-family": "Roboto Mono",
        "font-size": "25px",
        
        "line-width": 1,
        
        "rule": lambda track: (track.artist.lower() in ["beyonce", "beyoncé"] and any([_ in track.title.lower().replace("‘", "'").replace("’", "'") for _ in ["i'm that girl", "cozy", "alien superstar", "cuff it", "energy", "break my soul", "church girl", "plastic off the sofa", "virgo's groove", "move", "heated", "thique", "all up in your mind", "america has a problem", "pure/honey", "summer renaissance", "ameriican requiem", "blackbiird", "16 carriages", "protector", "my rose", "smoke hour", "texas hold 'em", "bodyguard", "dolly p", "jolene", "daughter", "spaghettii", "alliigator tears", "smoke hour ii", "just for fun", "ii most wanted", "levii's jeans", "flamenco", "the linda martell show", "ya ya", "oh louisiana", "desert eagle", "riiverdance", "ii hands ii heaven", "tyrant", "sweet ★ honey ★ buckiin'", "amen"]])),
        
        "format": lambda line: line.upper()
    },
    "honeymoon": {
        "font-family": "Joanna Solotype CG",
        
        "rule": lambda track: (track.artist.lower() == "lana del rey" and any([_ in track.title.lower().replace("‘", "'").replace("’", "'") for _ in ["honeymoon", "music to watch boys to", "terrence loves you", "god knows i tried", "high by the beach", "art deco", "burnt norton", "religion", "salvatore", "the blackest day", "24", "swan song", "don't let me be misunderstood"]]) or track.title.lower().replace("‘", "'").replace("’", "'") in ["freak"])
    },
    "lfl": {
        "font-family": "LTCCaslonLongSwash",
        
        "rule": lambda track: (track.artist.lower() == "lana del rey" and (any([_ in track.title.lower().replace("‘", "'").replace("’", "'") for _ in ["lust for life", "13 beaches", "cherry", "white mustang", "summer bummer", "groupie love", "in my feelings", "coachella - woodstock in my mind", "god bless america - and all the beautiful people in it", "when the world was at war we kept dancing", "beautiful people beautiful problems", "tomorrow never came", "get free"]]) or track.title.lower().replace("‘", "'").replace("’", "'") in ["love", "change", "heroin"]))
    },
    "nfr": {
        "background-image": "images/nfr.png",
        
        "font-family": "CCBiffBamBoom",
        "font-color": "#e9dabd",
        
        "line-color": "#030101",
        "line-width": 1.5,
        
        "shadow-color": "#030101",
        "shadow-offset": [2, 2],
        "shadow-radius": 5,
        
        "entering": "zoomin_overscale",
        
        "rule": lambda track: (track.artist.lower() == "lana del rey" and any([_ in track.title.lower().replace("‘", "'").replace("’", "'") for _ in ["norman fucking rockwell", "mariners apartment complex", "venice bitch", "fuck it i love you", "doin' time", "love song", "cinnamon girl", "how to disappear", "california", "the next best american record", "the greatest", "bartender", "happiness is a butterfly", "hope is a dangerous thing for a woman like me to have - but i have it"]]))
    },
    "cotc": {
        "font-family": "Marons",
        "font-size": "40px",
        
        "shadow-color": "#000000",
        "shadow-offset": [3, 3],
        
        "rule": lambda track: (track.artist.lower() == "lana del rey" and any([_ in track.title.lower().replace("‘", "'").replace("’", "'") for _ in ["white dress", "chemtrails over the country club", "tulsa jesus freak", "let me love you like a woman", "wild at heart", "dark but just a game", "not all who wander are lost", "yosemite", "breaking up slowly", "dance till we die", "for free"]]))
    },
    "bb": {
        "font-family": "Modern No. 216 Heavy",
        
        "rule": lambda track: (track.artist.lower() == "lana del rey" and (any([_ in track.title.lower().replace("‘", "'").replace("’", "'") for _ in ["text book", "blue banisters", "arcadia", "interlude - the trio", "black bathing suit", "if you lie down with me", "violets for roses", "dealer", "thunder", "wildflower wildfire", "nectar of the gods", "living legend", "cherry blossom", "sweet carolina"]]) or track.title.lower().replace("‘", "'").replace("’", "'") in ["beautiful"]))
    },
    "blvd": {
        "font-family": "Futura Display",
        "font-color": "#f2db78",
        "font-size": "40px",
        
        "shadow-radius": 3,
        
        "rule": lambda track: (track.artist.lower() == "lana del rey" and (any([_ in track.title.lower().replace("‘", "'").replace("’", "'") for _ in ["the grants", "did you know that there's a tunnel under ocean blvd", "sweet", "a&w", "judah smith interlude", "candy necklace", "jon batiste interlude", "kintsugi", "fingertips", "paris, texas", "grandfather please stand on the shoulders of my father while he's deep-sea fishing", "let the light in", "margaret", "fishtail", "peppers", "taco truck x vb"]]) or track.title.lower().replace("‘", "'").replace("’", "'") in ["sweet"]))
    },
    "blonde": {
        "background-color": "qradialgradient(spread:pad, cx:0.5, cy:0.6, radius:0.5, fx:0.75, fy:0.25, stop:0 #e0e0e0, stop:1 #00000000)",
        
        "font-family": "Blonde",
        "font-color": "#000000aa",
        "font-size": "50px",
        
        "line-width": 0,
        
        "shadow-color": "#000000",
        "shadow-radius": 15,
        
        
        "rule": lambda track: (track.artist.lower() == "frank ocean" and any([_ in track.title.lower().replace("‘", "'").replace("’", "'") for _ in ["nikes", "ivy", "pink + white", "be yourself", "solo", "skyline to", "self control", "good guy", "nights", "solo (reprise)", "pretty sweet", "facebook story", "close to you", "white ferrari", "seigfried", "godspeed", "futura free"]])),
        
        "format": lambda line: "".join([_ for _ in line if _ in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ ♬"])
    },
    "immunity": {
        "background-image": "images/immunity.png",
        
        "font-family": "Astloch",
        "font-color": "#f3f2ef",
        "font-weight": "bold",
        "font-size": "40px",
        
        "line-width": 0,
        
        "shadow-color": "#bbb4a4",
        "shadow-radius": 10,
        
        "rule": lambda track: (track.artist.lower() == "clairo" and any([_ in track.title.lower().replace("‘", "'").replace("’", "'") for _ in ["alewife", "impossible", "closer to you", "north", "bags", "softly", "sofia", "white flag", "feel something", "sinking", "i wouldn't ask you"]]))
    },
    "charm": {
        "background-color": "qlineargradient(spread:pad, x1:0.5, y1:0, x2:0.5, y2:1, stop:0 #43340d, stop:1 #2a1502)",
        
        "font-family": "Xaltid",
        "font-color": "#8b893f",
        "font-weight": "bold",
        "font-size": "50px",
        
        "line-width": 0,
        
        "shadow-color": "#8b893f",
        
        "rule": lambda track: (track.artist.lower() == "clairo" and any([_ in track.title.lower().replace("‘", "'").replace("’", "'") for _ in ["nomad", "sexy to someone", "second nature", "slow dance", "thank you", "terrapin", "juna", "add up my love", "echo", "glory of the snow", "pier 4"]]))
    },
    
    
    
    
    "hikaru utada": {
        "background-image": "images/hikaruutada.png",
        
        "line-color": "#004aaf",
        "line-width": 2,
        
        "shadow-color": "#f63934",
        "shadow-radius": 10,
        
        "rule": lambda track: (track.artist.lower() in ["宇多田ヒカル", "hikaru utada", "宇多田光"])
    },
    "vampire weekend": {
        "font-color": "#ff7d32",
        "font-family": "Futura",
        
        "line-color": "#ffffff",
        "line-width": 0,
        
        "shadow-color": "#ffffff",
        "shadow-radius": 10,
        
        "rule": lambda track: (track.artist.lower() == "vampire weekend")
    },
    "cupcakke": {
        "font-color": "#e0ddb4",
        "font-family": "Feathergraphy clean",
        "font-size": "20px",
        
        "line-width": 0,
        
        "use-shadow": False,
        
        "rule": lambda track: (track.artist.lower() == "cupcakke")
    },
    "sophie": {
        "font-color": "#ffffff",
        "font-family": "Jean",
        
        "line-width": 0,
        
        "use-shadow": False,
        
        "rule": lambda track: (track.artist.lower() == "sophie")
    },
    "phoebe bridgers": {
        "font-family": "AGaramond",
        
        "rule": lambda track: (track.artist.lower() == "phoebe bridgers")
    },
    "caroline polachek": {
        "font-family": "Sinistre",
        "font-size": "40px",
        
        "line-color": "#704212",
        "line-width": 0,
        
        "shadow-color": "#fcce9e",
        "shadow-offset": [0, 0],
        "shadow-radius": 10,
        
        "rule": lambda track: (track.artist.lower() in ["caroline polachek", "chairlift"])
    },
    "sufjan stevens": {
        "background-color": "qradialgradient(spread:pad, cx:0.5, cy:0.5, radius:0.4, fx:0.5, fy:1, stop:0 #374a50, stop:1 #00000000)",
        
        "font-family": "NimbuSanTBolCon",
        "font-color": "#ffffff",
        "font-size": "45px",
        
        "line-width": 0,
        
        "shadow-color": "#c8e21f",
        "shadow-offset": [2, 2],
        "shadow-radius": 10,
        
        "rule": lambda track: (track.artist.lower() in ["sufjan stevens", "sisyphus"]),
        
        "entering": "zoomin_overscale"
    },
    "weyes blood": {
        "background-color": "qradialgradient(spread:pad, cx:0.5, cy:0.5, radius:0.5, fx:0.3, fy:0.5, stop:0 #0e214c, stop:1 #00000000)",
        "font-family": "Eckmann",
        "font-color": "#f8e3da55",
        "font-size": "40px",
        
        "line-color": "#dd6678",
        "line-width": 1,
        
        "shadow-color": "#ce848b",
        "shadow-radius": 15,
        
        "rule": lambda track: (track.artist.lower() == "weyes blood")
    },
    "faye webster": {
        "font-family": "TWS Modern French 25",
        "font-color": "#1d5fa3",
        "font-size": "25px",
        
        "line-color": "#a4abe0",
        "line-width": 1.25,
        
        "shadow-color": "#cecece",
        "shadow-offset": [3, 3],
        "shadow-radius": 5,
        
        "rule": lambda track: (track.artist.lower() == "faye webster")
    },
    "sabrina carpenter": {
        "background-color": "qradialgradient(spread:repeat, cx:0.5, cy:-0.5, radius:1, fx:0.5, fy:0, stop:0 #20199b, stop:1 #00000000)",
        "font-family": "Century-Old-Style",
        "font-color": "#dcca87",
        
        "rule": lambda track: (track.artist.lower() == "sabrina carpenter"),
        
        "entering": "zoomin"
    },
    "yeule": {
        "font-color": "#97befc",
        "font-family": "sans-serif, Gadugi",
        
        "rule": lambda track: (track.artist.lower() == "yeule"),
        
        "format": yeule_style
    },
    "lana del rey": {
        "font-family": "Rainbow",
        "font-size": "50px",
        
        "use-shadow": False,
        
        "rule": lambda track: (track.artist.lower() == "lana del rey")
    }
    
}

def hex_to_rgba(hex_color, alpha=255):
    hex_color = hex_color.lstrip('#')
    lv = len(hex_color)
    if lv % 3 == 0:
        return tuple(int(hex_color[i:i + lv // 3], 16) for i in range(0, lv, lv // 3)) + (alpha,)
    elif lv == 8:
        return tuple(int(hex_color[i:i + 2], 16) for i in range(0, 8, 2))
    return (0,0,0,0)

def get_style(track: TrackInfo):
    stl = STYLES["default"].copy()
    stl_name = "default"
    
    for name, style in STYLES.items():
        if name == "default":
            continue
        if style["rule"](track):
            stl_name = name
            print(f"Applying style {name}")
            stl.update(style)
            if "format" in style:
                stl["format"] = lambda line: (style["format"](STYLES["default"]["format"](line))) 
            break

    for key, value in stl.items():
        if 'color' in key:
            if isinstance(value, str) and re.match(r'^#[0-9a-fA-F]{3}([0-9a-fA-F]{3,5})?$', value):
                stl[key] = hex_to_rgba(value)
    stl.update({"name": stl_name})
    return stl
            