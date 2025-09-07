import yt_dlp
import re

def find_lyrics_in_description(description):
    """Extract lyrics from video description."""
    if not description:
        return None

    # Common patterns that indicate where lyrics start
    lyrics_markers = [
        r"(?i)LYRICS:", r"(?i)ΣΤΙΧΟΙ:", r"(?i)LYRICS\n",
        r"(?i)ΣΤΙΧΟΙ\n", r"(?i)---LYRICS---", r"(?i)---ΣΤΙΧΟΙ---",
        r"(?i)Lyrics:", r"(?i)Στίχοι:", r"(?i)lyrics-σίχοι:"
    ]

    # Try to find lyrics section using markers
    for marker in lyrics_markers:
        match = re.split(marker, description, flags=re.IGNORECASE)
        if len(match) > 1:
            # Take the part after the marker
            potential_lyrics = match[1].strip()

            # Try to find where lyrics end (before links, credits, etc.)
            end_markers = [
                r"(?i)follow us:", r"(?i)social media:", r"(?i)credits:",
                r"(?i)subscribe:", r"(?i)ακολουθήστε μας:", r"(?i)συντελεστές:",
                r"(?i)facebook:", r"(?i)instagram:", r"(?i)spotify:",
                r"(?i)music by:", r"(?i)μουσική:", r"(?i)directed by:",
                r"(?i)subscribe to"
            ]

            for end_marker in end_markers:
                potential_lyrics = re.split(end_marker, potential_lyrics, flags=re.IGNORECASE)[0].strip()

            # Clean up any empty lines and common artifacts
            lines = [line.strip() for line in potential_lyrics.split('\n') if line.strip()]
            cleaned_lyrics = '\n'.join(lines)

            # Only return if we have something substantial (more than just a few words)
            if len(cleaned_lyrics.split()) > 10:
                print("\nLyrics found!")
                return cleaned_lyrics

    return None


def get_video_description(video_url):
    """Get description from a specific YouTube video URL."""
    ydl_opts = {"quiet": True, "no_warnings": True}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(video_url, download=False)
            return info.get("description", "")
        except Exception as e:
            print(f"Error fetching video info: {e}")
            return None


def get_youtube_lyrics(track_name, artist_name):
    """Main function to get lyrics from YouTube video description."""
    try:
        search_query = f"{artist_name} {track_name}"
        
        # Configure yt-dlp options for search - use ytsearch2 to have a backup option
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'default_search': 'ytsearch2'  # Get 2 results in case first one is a full album
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch2:{search_query}", download=False)
            if info.get('entries'):
                # Try to find a video that's not a full album
                selected_video = None
                for video in info['entries']:
                    title = video.get('title', '').lower()
                    if 'full album' not in title:
                        selected_video = video
                        break
                
                if selected_video is None:
                    selected_video = info['entries'][0]  # Fall back to first video if all contain "full album"
                
                video_url = f"https://youtube.com/watch?v={selected_video['id']}"
                print(f"Found video: {video_url}")
                # Always use get_video_description to get the full description
                description = get_video_description(video_url)
                
                if description:
                    # print("\nRaw description:")
                    # print("-" * 50)
                    # print(description)
                    # print("-" * 50)
                    
                    print("\nAttempting to extract lyrics...")
                    lyrics = find_lyrics_in_description(description)
                    
                    if lyrics:
                        return lyrics
                    else:
                        print("\nNo lyrics found in description!")
                else:
                    print("Failed to fetch video description!")
        
        return "No lyrics found in YouTube description"
        
    except Exception as e:
        print(f"Error fetching YouTube lyrics: {e}")
        return f"Error fetching YouTube lyrics: {e}"
