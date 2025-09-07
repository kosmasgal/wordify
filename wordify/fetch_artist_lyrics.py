import json
import os
import sys
import requests
from .spotify import sp
from .youtube_lyrics import get_youtube_lyrics


def get_cached_lyrics(track_id, cache_file):
    """Get lyrics from cache if available."""
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache = json.load(f)
                if (
                    track_id in cache
                    and cache[track_id] != "No lyrics found for this track."
                ):
                    return cache[track_id]
        except json.JSONDecodeError:
            pass
    return None

def save_to_cache(track_id, lyrics, cache_file):
    """Save lyrics to cache file."""
    cache = {}
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache = json.load(f)
        except json.JSONDecodeError:
            pass
    
    cache[track_id] = lyrics
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(cache, f, indent=4, ensure_ascii=False)

def get_lyrics(track_id, track_name, artist_name, cache_file='lyrics_cache.json'):
    """Fetches lyrics for a given track, first from cache, then Spotify, then YouTube if needed."""
    try:
        # First check cache
        cached_lyrics = get_cached_lyrics(track_id, cache_file)
        if cached_lyrics:
            return cached_lyrics, 'cache'
            
        # Try Spotify's lyrics
        response = requests.get(f"https://spotify-lyrics-api-pi.vercel.app/?trackid={track_id}&format=txt")
        if response.status_code == 200:
            data = response.json()
            if not data.get("error"):
                lyrics = "\n".join(line['words'] for line in data['lines'])
                save_to_cache(track_id, lyrics, cache_file)
                return lyrics, 'spotify'
        
        # If Spotify lyrics not found, try YouTube
        print(f"  - Spotify lyrics not found for '{track_name}', trying YouTube...")
        youtube_lyrics = get_youtube_lyrics(track_name, artist_name)
        if youtube_lyrics and youtube_lyrics != "No lyrics found in YouTube description":
            save_to_cache(track_id, youtube_lyrics, cache_file)
            return youtube_lyrics, 'youtube'
            
        no_lyrics = "No lyrics found for this track."
        save_to_cache(track_id, no_lyrics, cache_file)
        return no_lyrics, 'none'
        
    except requests.RequestException as e:
        error_msg = f"Error fetching lyrics: {e}"
        return error_msg, 'error'
    except Exception as e:
        error_msg = f"Error processing lyrics: {e}"
        return error_msg, 'error'


def fetch_artist_data(artist_name):
    """Fetches all albums and tracks with lyrics for a given artist."""
    # Stats tracking
    stats = {
        'total_tracks': 0,
        'spotify_lyrics': 0,
        'youtube_lyrics': 0,
        'cache_hits': 0,
        'no_lyrics': 0,
        'errors': 0
    }
    
    # 1. Search for the artist to get their Spotify ID
    results = sp.search(q=f"artist:{artist_name}", type="artist", limit=1)
    if not results["artists"]["items"]:
        print(f"Artist '{artist_name}' not found.")
        return None

    artist = results["artists"]["items"][0]
    artist_id = artist["id"]
    print(f"Found artist: {artist['name']} (ID: {artist_id})")

    # 2. Get all albums for the artist
    all_albums = []
    offset = 0
    while True:
        albums_page = sp.artist_albums(
            artist_id, album_type="album,single", limit=50, offset=offset
        )
        all_albums.extend(albums_page["items"])
        if not albums_page["next"]:
            break
        offset += 50

    print(f"Found {len(all_albums)} albums/singles. Fetching tracks and lyrics...")

    # 3. Process each album
    artist_data = {
        "artist_name": artist["name"],
        "artist_id": artist_id,
        "albums": [],
        "stats": stats  # Include stats in the output
    }

    for i, album_summary in enumerate(all_albums):
        album_id = album_summary["id"]
        album_details = sp.album(album_id)

        album_info = {
            "album_name": album_details["name"],
            "album_id": album_id,
            "release_date": album_details["release_date"],
            "total_tracks": album_details["total_tracks"],
            "tracks": [],
        }

        print(f"\nProcessing album {i+1}/{len(all_albums)}: {album_details['name']}")

        # 4. Get all tracks for the album
        tracks_page = sp.album_tracks(album_id, limit=50)
        while True:
            for track in tracks_page["items"]:
                stats['total_tracks'] += 1
                print(f"  - Fetching lyrics for '{track['name']}'...")
                lyrics, source = get_lyrics(track["id"], track["name"], artist["name"])
                
                # Update stats based on source
                if source == 'spotify':
                    stats['spotify_lyrics'] += 1
                elif source == 'youtube':
                    stats['youtube_lyrics'] += 1
                elif source == 'cache':
                    stats['cache_hits'] += 1
                elif source == 'none':
                    stats['no_lyrics'] += 1
                else:  # error
                    stats['errors'] += 1
                
                track_info = {
                    "track_name": track["name"],
                    "track_id": track["id"],
                    "track_number": track["track_number"],
                    "duration_ms": track["duration_ms"],
                    "lyrics": lyrics,
                    "lyrics_source": source
                }
                album_info["tracks"].append(track_info)

            if not tracks_page["next"]:
                break
            tracks_page = sp.next(tracks_page)

        artist_data["albums"].append(album_info)

    # Print final statistics
    print("\nLyrics Source Statistics:")
    print(f"Total tracks processed: {stats['total_tracks']}")
    print(f"- Found in Spotify: {stats['spotify_lyrics']} tracks")
    print(f"- Found in YouTube: {stats['youtube_lyrics']} tracks")
    print(f"- Retrieved from cache: {stats['cache_hits']} tracks")
    print(f"\nMissing Lyrics: {stats['no_lyrics']} tracks ({(stats['no_lyrics']/stats['total_tracks']*100):.1f}%)")
    if stats['errors'] > 0:
        print(f"Errors encountered: {stats['errors']} tracks")

    return artist_data
