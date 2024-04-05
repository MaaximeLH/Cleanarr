#!/usr/bin/env python3
import logging
import os
import sys
from fnmatch import fnmatch


from config import cfg

try:
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urljoin

from plexapi.server import PlexServer
import requests

############################################################
# INIT
############################################################

# Setup logger
log_filename = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), 'activity.log')
logging.basicConfig(
    filename=log_filename,
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logging.getLogger('urllib3.connectionpool').disabled = True
log = logging.getLogger("Cleanarr")

# Setup PlexServer object
try:
    plex = PlexServer(cfg['PLEX_SERVER'], cfg['PLEX_TOKEN'])
except:
    log.exception("Exception connecting to server %r with token %r", cfg['PLEX_SERVER'], cfg['PLEX_TOKEN'])
    print(f"Exception connecting to {cfg['PLEX_SERVER']} with token: {cfg['PLEX_TOKEN']}")

    exit(1)


############################################################
# PLEX METHODS
############################################################

def get_all_items(plex_section_name):
    sec_type = get_section_type(plex_section_name)
    dupe_search_results = plex.library.section(plex_section_name).search(duplicate=False, libtype=sec_type)
    return dupe_search_results


def get_section_type(plex_section_name):
    try:
        plex_section_type = plex.library.section(plex_section_name).type
    except Exception:
        log.exception("Exception occurred while trying to lookup the section type for Library: %s", plex_section_name)
        exit(1)
    return 'episode' if plex_section_type == 'show' else 'movie'


def get_score(media_info):
    score = 0
    # score audio codec
    for codec, codec_score in cfg['AUDIO_CODEC_SCORES'].items():
        if codec.lower() == media_info['audio_codec'].lower():
            score += int(codec_score)
            log.debug("Added %d to score for audio_codec being %r", int(codec_score), str(codec))
            break
    # score video codec
    for codec, codec_score in cfg['VIDEO_CODEC_SCORES'].items():
        if codec.lower() == media_info['video_codec'].lower():
            score += int(codec_score)
            log.debug("Added %d to score for video_codec being %r", int(codec_score), str(codec))
            break
    # score video resolution
    for resolution, resolution_score in cfg['VIDEO_RESOLUTION_SCORES'].items():
        if resolution.lower() == media_info['video_resolution'].lower():
            score += int(resolution_score)
            log.debug("Added %d to score for video_resolution being %r", int(resolution_score), str(resolution))
            break
    # score filename
    for filename_keyword, keyword_score in cfg['FILENAME_SCORES'].items():
        for filename in media_info['file']:
            if fnmatch(os.path.basename(filename.lower()), filename_keyword.lower()):
                score += int(keyword_score)
                log.debug("Added %d to score for match filename_keyword %s", int(keyword_score), filename_keyword)
    # add bitrate to score
    score += int(media_info['video_bitrate']) * 2
    log.debug("Added %d to score for video bitrate", int(media_info['video_bitrate']) * 2)
    # add duration to score
    score += int(media_info['video_duration']) / 300
    log.debug("Added %d to score for video duration", int(media_info['video_duration']) / 300)
    # add width to score
    score += int(media_info['video_width']) * 2
    log.debug("Added %d to score for video width", int(media_info['video_width']) * 2)
    # add height to score
    score += int(media_info['video_height']) * 2
    log.debug("Added %d to score for video height", int(media_info['video_height']) * 2)
    # add audio channels to score
    score += int(media_info['audio_channels']) * 1000
    log.debug("Added %d to score for audio channels", int(media_info['audio_channels']) * 1000)
    # add file size to score
    if cfg['SCORE_FILESIZE']:
        score += int(media_info['file_size']) / 100000
        log.debug("Added %d to score for total file size", int(media_info['file_size']) / 100000)
    return int(score)


def get_media_info(item):
    info = {
        'id': 'Unknown',
        'video_bitrate': 0,
        'audio_codec': 'Unknown',
        'audio_channels': 0,
        'video_codec': 'Unknown',
        'video_resolution': 'Unknown',
        'video_width': 0,
        'video_height': 0,
        'video_duration': 0,
        'file': [],
        'multipart': False,
        'file_size': 0
    }
    # get id
    try:
        info['id'] = item.id
    except AttributeError:
        log.debug("Media item has no id")
    # get bitrate
    try:
        info['video_bitrate'] = item.bitrate if item.bitrate else 0
    except AttributeError:
        log.debug("Media item has no bitrate")
    # get video codec
    try:
        info['video_codec'] = item.videoCodec if item.videoCodec else 'Unknown'
    except AttributeError:
        log.debug("Media item has no videoCodec")
    # get video resolution
    try:
        info['video_resolution'] = item.videoResolution if item.videoResolution else 'Unknown'
    except AttributeError:
        log.debug("Media item has no videoResolution")
    # get video height
    try:
        info['video_height'] = item.height if item.height else 0
    except AttributeError:
        log.debug("Media item has no height")
    # get video width
    try:
        info['video_width'] = item.width if item.width else 0
    except AttributeError:
        log.debug("Media item has no width")
    # get video duration
    try:
        info['video_duration'] = item.duration if item.duration else 0
    except AttributeError:
        log.debug("Media item has no duration")
    # get audio codec
    try:
        info['audio_codec'] = item.audioCodec if item.audioCodec else 'Unknown'
    except AttributeError:
        log.debug("Media item has no audioCodec")
    # get audio channels
    try:
        for part in item.parts:
            for stream in part.audioStreams():
                if stream.channels:
                    log.debug(f"Added {stream.channels} channels for {stream.title if stream.title else 'Unknown'} audioStream")
                    info['audio_channels'] += stream.channels
        if info['audio_channels'] == 0:
            info['audio_channels'] = item.audioChannels if item.audioChannels else 0

    except AttributeError:
        log.debug("Media item has no audioChannels")

    # is this a multi part (cd1/cd2)
    if len(item.parts) > 1:
        info['multipart'] = True
    for part in item.parts:
        info['file'].append(part.file)
        info['file_size'] += part.size if part.size else 0

    return info


def delete_item(show_key, media_id):
    delete_url = urljoin(cfg['PLEX_SERVER'], '%s/media/%d' % (show_key, media_id))
    log.debug("Sending DELETE request to %r" % delete_url)
    if requests.delete(delete_url, headers={'X-Plex-Token': cfg['PLEX_TOKEN']}).status_code == 200:
        print("\t\tDeleted media item: %r" % media_id)
    else:
        print("\t\tError deleting media item: %r" % media_id)


############################################################
# MISC METHODS
############################################################

decision_filename = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), 'decisions.log')

def write_decision(title=None, keeping=None, removed=None):
    lines = []
    if title:
        lines.append('\nTitle    : %s\n' % title)
    if keeping:
        lines.append('\tKeeping  : %r\n' % keeping)
    if removed:
        lines.append('\tRemoving : %r\n' % removed)

    with open(decision_filename, 'a') as fp:
        fp.writelines(lines)
    return



############################################################
# MAIN
############################################################

if __name__ == "__main__":
    print("""
______  _      _____ __   __   _____  _      _____   ___   _   _  _____ ______
| ___ \| |    |  ___|\ \ / /  /  __ \| |    |  ___| / _ \ | \ | ||  ___|| ___ \
| |_/ /| |    | |__   \ V /   | /  \/| |    | |__  / /_\ \|  \| || |__  | |_/ /
|  __/ | |    |  __|  /   \   | |    | |    |  __| |  _  || . ` ||  __| |    /
| |    | |____| |___ / /^\ \  | \__/\| |____| |___ | | | || |\  || |___ | |\ \
\_|    \_____/\____/ \/   \/   \____/\_____/\____/ \_| |_/\_| \_/\____/ \_| \_|


#########################################################################
# Author:   MaaximeLH - Forked from l3uddz                              #
# URL:      https://github.com/maaximelh/Cleanarr                       #
# --                                                                    #
#########################################################################
#                   GNU General Public License v3.0                     #
#########################################################################
""")
    print("Initialized")
    process_later = {}
    # process sections
    print("Finding items...")
    for section in cfg['PLEX_LIBRARIES']:
        items = get_all_items(section)
        print("Found %d total items for section %r" % (len(items), section))
        # loop returned duplicates
        for item in items:
            parts = {}
            for part in item.media:
                part_info = get_media_info(part)
                part_info['score'] = get_score(part_info)  # Calculate score for this part

                if part_info['score'] < cfg['MINIMUM_SCORE']:
                    print(part_info['file'][0], "has a score of", part_info['score'], "which is below the minimum score of", cfg['MINIMUM_SCORE'])
                    if not cfg['AUTO_DELETE']:
                        keep_item = input("\nDo you want to delete this item? (y/n): ")
                        if keep_item.lower() == 'n':
                            continue

                    delete_item(item.key, part_info['id'])
                    write_decision(title=part_info['file'][0], removed=True)

    print('Your plex server is now clean!')
