
import logging
from typing import List, Optional

from syncedlyrics.providers import Deezer, Lrclib, Musixmatch, NetEase, Megalobiz, Genius
from syncedlyrics.utils import save_lrc_file

logger = logging.getLogger(__name__)

def is_lrc_valid(
    lrc: str, allow_plain_format: bool = False, check_translation: bool = False
) -> bool:
    """Checks whether a given LRC string is valid or not."""
    if not lrc:
        return False
    lines = lrc.split("\n")[5:10]
    if not allow_plain_format:
        if not check_translation:
            conds = ["[" in l for l in lrc.split("\n")[5:10]]
            return all(conds)
        else:
            for i, line in enumerate(lines):
                if "[" in line:
                    if i + 1 < len(lines):
                        next_line = lines[i + 1]
                        if "(" not in next_line:
                            return False
    return True

def search(
    search_term: str,
    allow_plain_format: bool = False,
    save_path: Optional[str] = None,
    providers: Optional[List[str]] = None,
    lang: Optional[str] = None,
    enhanced: bool = False,
) -> Optional[str]:
    """
    Returns the synced lyrics of the song in [LRC](https://en.wikipedia.org/wiki/LRC_(file_format)) format if found.
    ### Arguments
    - `search_term`: The search term to find the track
    - `allow_plain_format`: Return a plain text (not synced) lyrics if not LRC was found
    - `save_path`: Path to save `.lrc` lyrics. No saving if `None`
    - `providers`: A list of provider names to include in searching; loops over all the providers as soon as an LRC is found
    - `lang`: Language of the translation along with the lyrics. **Only supported by Musixmatch**
    - `enhanced`: Returns word by word synced lyrics if available. **Only supported by Musixmatch**
    """
    # _providers = [
    #     Musixmatch(lang=lang, enhanced=enhanced),
    #     Lrclib(),
    #     Deezer(),
    #     NetEase(),
    #     Megalobiz(),
    #     Genius(),
    # ]
    _providers = [] 
    for provider in providers:
        if provider.lower() == "musixmatch":
            _providers.append(Musixmatch(lang=lang, enhanced=enhanced))
        elif provider.lower() == "lrclib":
            _providers.append(Lrclib())
        elif provider.lower() == "deezer":
            _providers.append(Deezer())
        elif provider.lower() == "netease":
            _providers.append(NetEase())
        elif provider.lower() == "megalobiz":
            _providers.append(Megalobiz())
        elif provider.lower() == "genius":
            _providers.append(Genius())
    if _providers == []:
        return None

    lrc = None
    for provider in _providers:
        logger.debug(f"Looking for an LRC on {provider.__class__.__name__}")
        try:
            _l = provider.get_lrc(search_term)
        except Exception as e:
            logger.error(
                f"An error occurred while searching for an LRC on {provider.__class__.__name__}"
            )
            logger.error(e)
            continue
        if enhanced and not _l:
            # Since enhanced is only supported by Musixmatch, break if no LRC is found
            break
        check_translation = lang is not None and isinstance(provider, Musixmatch)
        if is_lrc_valid(_l, allow_plain_format, check_translation):
            logger.info(
                f'synced-lyrics found for "{search_term}" on {provider.__class__.__name__}'
            )
            lrc = _l
            break
        else:
            logger.debug(
                f"Skip {provider.__class__.__name__} as the synced-lyrics is not valid. (allow_plain_format={allow_plain_format})"
            )
            logger.debug(f"Lyrics: {_l}")
            lrc = "[00:00.00]  ♬"
    if not lrc:
        logger.info(f'No synced-lyrics found for "{search_term}" :(')
        return None
    if save_path:
        save_path = save_path.format(search_term=search_term)
        save_lrc_file(save_path, lrc)
    return lrc
