#!/usr/bin/env python
import argparse
from .generate_wordcloud import generate_artist_wordcloud

def main():
    parser = argparse.ArgumentParser(
        description='Generate word clouds from song lyrics',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Generate word cloud for all songs by an artist
    wordify "Iron Maiden"
    
    # Generate word cloud for a specific album
    wordify "Iron Maiden" --album "Powerslave"
    
    # Generate word cloud with specified language for stop words
    wordify "Pirates City" --lang "greek"
    """
    )
    
    parser.add_argument('artist', help='Name of the artist')
    parser.add_argument('--album', help='Optional: Name of the album to analyze', default=None)
    parser.add_argument('--lang', 
                       choices=['english', 'greek', 'both'],
                       default='both',
                       help='Language for stop words (default: both)')
    
    args = parser.parse_args()
    
    try:
        generate_artist_wordcloud(args.artist, args.album, args.lang)
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
