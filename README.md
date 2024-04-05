
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-blue.svg?style=flat-square)](https://www.python.org/)
[![License: GPL v3](https://img.shields.io/badge/License-GPL%203-blue.svg?style=flat-square)](https://github.com/maaximelh/cleanarr/blob/master/LICENSE.md)
[![last commit (develop)](https://img.shields.io/github/last-commit/maaximelh/cleanarr/develop.svg?colorB=177DC1&label=Last%20Commit&style=flat-square)](https://github.com/maaximelh/cleanarr/commits/develop)
[![Discord](https://img.shields.io/discord/381077432285003776.svg?colorB=177DC1&label=Discord&style=flat-square)](https://discord.io/cloudbox)
[![Contributing](https://img.shields.io/badge/Contributing-gray.svg?style=flat-square)](CONTRIBUTING.md)
[![Donate](https://img.shields.io/badge/Donate-gray.svg?style=flat-square)](#donate)

---

<!-- TOC depthFrom:1 depthTo:2 withLinks:1 updateOnSave:1 orderedList:0 -->

- [Introduction](#introduction)
- [Demo](#demo)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
  - [Sample](#sample)
  - [Foreword](#foreword)
  - [Details](#details)
- [Plex](#plex)
- [Usage](#usage)
- [Donate](#donate)

<!-- /TOC -->

---

# Introduction

Based on https://github.com/maaximelh/cleanarr repository
 
CleanArr simplifies library maintenance by automatically managing content based on customizable rules. Keep your Plex library clean and high-quality with ease.

You can also run this program by a cron job to keep your library clean and organized automatically.


# Requirements

1. Python 3.6+.

1. Required Python modules (see below).


# Installation

_Note: Steps below are for Debian-based distros (other operating systems will require tweaking to the steps)._

1. Install Python 3 and PIP

   ```
   sudo apt install python3 python3-pip
   ```

1. Clone the Cleanarr repo.

   ```
   sudo git clone https://github.com/MaaximeLH/Cleanarr /opt/Cleanarr
   ```

1. Find your user & group.

   ```
   id
   ```

1. Fix permissions of the Cleanarr folder (replace `user`/`group` with yours).

   ```
   sudo chown -R user:group /opt/Cleanarr
   ```

1. Go into the Cleanarr folder.

   ```
   cd /opt/Cleanarr
   ```

1. Install the required python modules.

   ```
   sudo python3 -m pip install -r requirements.txt
   ```

1. Create a shortcut for Cleanarr.

   ```
   sudo ln -s /opt/Cleanarr/cleanarr.py /usr/local/bin/cleanarr
   ```

1. Generate a `config.json` file.

   ```
   cleanarr
   ```

1. Fill in Plex URL and credentials at the prompt to generated a Plex Access Token (optional).

   ```
   Dumping default config to: /opt/Cleanarr/config.json
   Plex Server URL: http://localhost:32400
   Plex Username: your_plex_username
   Plex Password: your_plex_password
   Auto Delete duplicates? [y/n]: n
   Please edit the default configuration before running again!
   ```

1. Configure the `config.json` file.

   ```
   nano config.json
   ```


# Configuration

## Sample

```json
{
  "AUDIO_CODEC_SCORES": {
    "Unknown": 0,
    "aac": 1000,
    "ac3": 1000,
    "dca": 2000,
    "dca-ma": 4000,
    "eac3": 1250,
    "flac": 2500,
    "mp2": 500,
    "mp3": 1000,
    "pcm": 2500,
    "truehd": 4500,
    "wmapro": 200
  },
  "AUTO_DELETE": false,
  "MINIMUM_SCORE": 60000,
  "FILENAME_SCORES": {
    "*.avi": -1000,
    "*.ts": -1000,
    "*.vob": -5000,
    "*1080p*BluRay*": 15000,
    "*720p*BluRay*": 10000,
    "*HDTV*": -1000,
    "*PROPER*": 1500,
    "*REPACK*": 1500,
    "*Remux*": 20000,
    "*WEB*CasStudio*": 5000,
    "*WEB*KINGS*": 5000,
    "*WEB*NTB*": 5000,
    "*WEB*QOQ*": 5000,
    "*WEB*SiGMA*": 5000,
    "*WEB*TBS*": -1000,
    "*WEB*TROLLHD*": 2500,
    "*WEB*VISUM*": 5000,
    "*dvd*": -1000
  },
  "PLEX_LIBRARIES": [
    "Movies",
    "TV",
    "# Edit libraries here"
  ],
  "PLEX_SERVER": "https://plex.your-server.com",
  "PLEX_TOKEN": "",
  "SCORE_FILESIZE": true,
  "SKIP_LIST": [],
  "VIDEO_CODEC_SCORES": {
    "Unknown": 0,
    "h264": 10000,
    "h265": 5000,
    "hevc": 5000,
    "mpeg1video": 250,
    "mpeg2video": 250,
    "mpeg4": 500,
    "msmpeg4": 100,
    "msmpeg4v2": 100,
    "msmpeg4v3": 100,
    "vc1": 3000,
    "vp9": 1000,
    "wmv2": 250,
    "wmv3": 250
  },
  "VIDEO_RESOLUTION_SCORES": {
    "1080": 10000,
    "480": 3000,
    "4k": 20000,
    "720": 5000,
    "Unknown": 0,
    "sd": 1000
  }
}
```
## Foreword

The scoring is based on: non-configurable and configurable parameters.

  - Non-configurable parameters are: _bitrate_, _duration_, _height_, _width_, and _audio channel_.

  - Configurable parameters are: _audio codec scores_, _video codec scores_, _video resolution scores_, _filename scores_, and _file sizes_ (can only be toggled on or off).

  - Note: bitrate, duration, height, width, audio channel, audio and video codecs, video resolutions (e.g. SD, 480p, 720p, 1080p, 4K, etc), and file sizes are all taken from the metadata Plex retrieves during media analysis.

## Details

### Audio Codec Scores

- You can set `AUDIO_CODEC_SCORES` to your preference.

- The default settings should be sufficient for most.


### Auto Delete

- Under `AUTO_DELETE`, set your desired option.

  - `"AUTO_DELETE": true,`  - Cleanarr will run in automatic mode.

  - `"AUTO_DELETE": false,` -  Cleanarr will run in interactive mode. (Default)

    - Options:

      - Skip (i.e. keep both): `0`

      - Choose the best one (and delete the rest): `b`

      - Select the item to keep (and delete the rest): `#` (i.e. `1`, `2`, `3`, etc).


### Filename Scores

- You can set `FILENAME_SCORES` to your preference.

- The default settings should be sufficient for most.

### Plex Libraries

1. Go to Plex and get all the names of your Plex Libraries you want to find duplicates in.

   - Example Library:

     ![](https://i.imgur.com/JFRTD1m.png)

1. Under `PLEX_LIBRARIES`, list your Plex Libraries exactly as they are named in your Plex.

   - Format:

     ```json
     "PLEX_LIBRARIES": [
       "LIBRARY_NAME_1",
       "LIBRARY_NAME_2"
     ],
     ```
     or

     ```json
     "PLEX_LIBRARIES": ["LIBRARY_NAME_1", "LIBRARY_NAME_2"],
     ```
     
   - Example:

     ```json
     "PLEX_LIBRARIES": [
       "Movies",
       "TV"
     ],
     ```

### Plex Server URL

- Your Plex server's URL.

- This can be any format (e.g. <http://localhost:32400>, <https://plex.domain.ltd>).

### Plex Token

1. Obtain a Plex Access Token:

   - Fill in the Plex URL and Plex login credentials, at the prompt, on first run. This only occurs when there is no `config.json` present.

     or

   - Visit https://support.plex.tv/hc/en-us/articles/204059436-Finding-an-authentication-token-X-Plex-Token

1. Add the Plex Access Token to `"PLEX_TOKEN"` so that it now appears as `"PLEX_TOKEN": "abcd1234",`.

   - Note: Make sure it is within the quotes (`"`) and there is a comma (`,`) after it.

### Filesize Scores

- `"SCORE_FILESIZE": true` will add more points to the overall score based on the actual file size.

- The default settings should be sufficient for most.

- Note: In some situations (e.g. a bad encode resulting in a large size), this may be something you want to turn it off (i.e. `false`).

### Skip List

- In Auto Delete mode, any file paths matching the patterns (i.e folders), listed in `SKIP_LIST`, will be ignored.

- Example:

  ```json
  "SKIP_LIST": ["/Movies4K/"]
  ```

- The default settings should be sufficient for most.

### Video Codec Scores

- You can set `VIDEO_CODEC_SCORES` to your preference.

- The default settings should be sufficient for most.

### Video Resolution Scoring

- You can set `VIDEO_RESOLUTION_SCORES` to your preference.

- The default settings should be sufficient for most.

### Recommanded score for keeping 720p high quality content

- 65000 is a good score to keep 720p content, you can adjust it to your preference.

# Plex

You will need to make sure that **Allow media deletion** is enabled in Plex.

1. In Plex, click the **Settings** icon -> **Server** -> **Library**.

1. Set the following:

   - **Allow media deletion**: `enabled`

1. Click **SAVE CHANGES**.


![](http://i.imgur.com/D82n8vh.png)


# Usage

Simply run the script/command:

```
cleanarr
```
