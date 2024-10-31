# Plex Playlist Importer

**Version:** 0.16o

## Overview

This script allows you to import multiple `.m3u` or `.m3u8` playlist files into your Plex music library. This script optimizes performance by fetching and mapping media items from Plex only once per batch import, reducing redundant API calls when importing multiple playlists.

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

### Command-Line Arguments

- `--library-id`: (Required) The ID of the Plex music library to import playlists to.
- `playlist_file(s)`: (Required) One or more `.m3u` or `.m3u8` playlist files to import.

## Configuration

Update the following constants in the script to match your Plex server configuration:

```python
PLEX_URL = "https://your-plex-server-url"
PLEX_TOKEN = "your-plex-token"
```
### Running the Script

```bash
python3 playlistimportv0.16o.py --library-id 7 playlist1.m3u playlist2.m3u8
```
### Example Usage

Run the script to import multiple playlists into your Plex server’s specified library. This example uses library ID 7 and two playlist files:

```bash
python3 playlistimportv0.16o.py --library-id 7 ~/Music/Playlists/Chill.m3u ~/Music/Playlists/Rock.m3u8
```
