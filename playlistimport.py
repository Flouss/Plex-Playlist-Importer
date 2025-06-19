import os
import logging
import sys
from dotenv import load_dotenv, dotenv_values
from plexapi.server import PlexServer
from concurrent.futures import ThreadPoolExecutor, as_completed
from plexapi.exceptions import Unauthorized

# Version 06.2025

# Set up logging
logging.basicConfig(
    filename='import.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Plex configuration
load_dotenv()
plex_url = os.getenv("PLEX_URL")
plex_token = os.getenv("PLEX_TOKEN")
library_id = int(os.getenv("LIBRARY_ID"))
playlist_folder_path = os.getenv("PLAYLIST_FOLDER_PATH")

def connect_to_plex():
    """Connect to the Plex server."""
    try:
        logging.info("Connecting to Plex server...")
        plex = PlexServer(plex_url, plex_token)
        logging.info("Connected to Plex server.")
        return plex
    except Unauthorized:
        logging.error("Unauthorized access - check your Plex token.")
        sys.exit(1)

def retrieve_library_section(plex, section_id):
    """Retrieve the Plex library section by ID."""
    logging.info(f"Retrieving library section with ID {section_id}...")
    library_section = plex.library.sectionByID(section_id)
    logging.info(f"Library section '{library_section.title}' retrieved.")
    return library_section

def fetch_all_tracks_concurrently(library_section):
    """Fetch all tracks concurrently from the library section."""
    all_tracks = []

    albums = library_section.albums()
    logging.info(f"Fetching all tracks concurrently from {len(albums)} albums...")

    def fetch_tracks_from_album(album):
        try:
            return album.tracks()
        except Exception as e:
            logging.error(f"Error fetching tracks from album {album.title}: {e}")
            return []

    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(fetch_tracks_from_album, album): album for album in albums}
        for future in as_completed(futures):
            album = futures[future]
            try:
                tracks = future.result()
                all_tracks.extend(tracks)
            except Exception as exc:
                logging.error(f"Album {album.title} generated an exception: {exc}")

    logging.info(f"Fetched {len(all_tracks)} total tracks from all albums.")
    return all_tracks

def create_media_map(all_tracks):
    """Build a map of normalized paths to Plex media objects."""
    media_path_map = {}

    for idx, track in enumerate(all_tracks, 1):
        if hasattr(track, 'media'):
            for media in track.media:
                for part in media.parts:
                    full_path = os.path.join(*part.file.split(os.sep)[-2:]).lower().replace(' ', '').replace('(', '').replace(')', '').replace('+', '')
                    media_path_map[full_path] = track
                    logging.info(full_path)

        if idx % 1000 == 0:
            logging.info(f"Processed {idx} tracks...")

    logging.info(f"Total paths added to media map: {len(media_path_map)}")
    return media_path_map

def process_playlist_file(playlist_file):
    """Read the playlist file and return a list of file paths."""
    with open(playlist_file, 'r') as file:
        lines = [line.strip() for line in file if not line.startswith('#') and line.strip()]

    return lines

def match_tracks(playlist_paths, media_path_map):
    """Match the tracks in the playlist with media in the media map."""
    matched_tracks = []

    for path in playlist_paths:
        normalized_path = os.path.join(*path.split(os.sep)[-2:]).lower().replace(' ','').replace('(', '').replace(')', '').replace('+', '')

        if normalized_path in media_path_map:
            track = media_path_map[normalized_path]
            matched_tracks.append(track)
            logging.info(f"Track matched and added to playlist: {track.title}")
        else:
            logging.warning(f"Track not found in media map: {normalized_path}")

    logging.info(f"Total tracks collected for playlist: {len(matched_tracks)}")
    return matched_tracks

def create_or_update_playlist(plex, playlist_title, track_items):
    """Create or update a Plex playlist with matched tracks."""
    if not track_items:
        logging.error("No matched tracks to add to the playlist.")
        return

    try:
        # Check if playlist already exists
        existing_playlist = next((pl for pl in plex.playlists() if pl.title == playlist_title), None)
        if existing_playlist:
            existing_track_ids = {item.ratingKey for item in existing_playlist.items()}
            new_tracks = [track for track in track_items if track.ratingKey not in existing_track_ids]

            if new_tracks:
                existing_playlist.addItems(new_tracks)
                logging.info(f"Playlist '{playlist_title}' updated with {len(new_tracks)} new tracks.")
            else:
                logging.info(f"Playlist '{playlist_title}' already has all tracks. No update needed.")
        else:
            plex.createPlaylist(playlist_title, items=track_items)
            logging.info(f"Playlist '{playlist_title}' created successfully with {len(track_items)} tracks.")
    except Exception as e:
        logging.error(f"Failed to create or update playlist '{playlist_title}': {e}")

def main(library_id, playlist_folder_path):
    plex = connect_to_plex()
    library_section = retrieve_library_section(plex, library_id)

    # Fetch all tracks once for all playlists
    all_tracks = fetch_all_tracks_concurrently(library_section)
    media_map = create_media_map(all_tracks)

    # Process each playlist file
    playlist_files = [ os.path.join(playlist_folder_path, f) for f in os.listdir(playlist_folder_path) if f.endswith(".m3u") or f.endswith(".m3u8")]

    for playlist_file in playlist_files:
        logging.info(f"Processing playlist file: {playlist_file}")

        playlist_title = os.path.splitext(os.path.basename(playlist_file))[0]
        playlist_paths = process_playlist_file(playlist_file)

        matched_tracks = match_tracks(playlist_paths, media_map)

        create_or_update_playlist(plex, playlist_title, matched_tracks)

if __name__ == "__main__":
    main(library_id, playlist_folder_path)
