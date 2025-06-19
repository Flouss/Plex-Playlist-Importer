# Plex Playlist Importer

**Version:** 06.2025
Forked from: https://github.com/TomHarkness/Plex-Playlist-Importer

## Overview

This script allows you to import multiple `.m3u` or `.m3u8` playlist files into your Plex music library.
The script optimizes performance by fetching and mapping media items from Plex only once per batch import, reducing redundant API calls when importing multiple playlists.

## Features

- Imports multiple playlists with one call
- Efficiently builds a media map with track paths only once per session
- Adds new tracks to existing playlists if they are missing
- Detailed logging for tracking playlist import statuses, errors, and performance metrics

## Requirements

- **Python 3.x**
- **PlexAPI** library (`pip install plexapi`)
- **Plex Server** with media access and a valid Plex token

### Logging
The script logs activities, errors, and performance details to `import.log`, with timestamps for each entry.

#### Log Structure
- **Media Map**: Logs the total paths added to the media map.
- **Track Matching**: Logs tracks that are matched and added to playlists.
- **Error Handling**: Logs any errors encountered during the import process, including unauthorized access and import failures.

### Error Handling
Errors are logged to `import.log`. Common errors include:

- **Unauthorized Access**: If access is denied, check the `PLEX_TOKEN` for correctness.
- **Playlist Not Found**: Paths in the playlist that do not match media items in Plex are logged with a warning.

### Performance Optimization
To improve performance, this script:
- Builds the media map once when importing multiple playlists.
- Uses concurrent processing to fetch track data in parallel.

### License
This project is open-source under the MIT License.

## Usage

### Setup venv

Setup venv and install requirements

```bash
python -m venv .venv
source .venv/bin/activate
pip install requirements.txt
```

### Configuration

Set the following constants in the `.env` (created it if missing, use `.env.example` as base) to match your Plex server configuration:

```.env
PLEX_URL = "http://plex.server.lan"
PLEX_TOKEN = "your token here"
PLAYLIST_FOLDER_PATH = "the playlist folder"
LIBRARY_ID = 1
```
### Running the Script

```bash
python3 playlistimport.py
```

