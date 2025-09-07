import json
import re
import unicodedata
from collections import defaultdict
from .fetch_artist_lyrics import fetch_artist_data
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import nltk
from nltk.corpus import stopwords
import os

# Download required NLTK data
nltk.download('stopwords', quiet=True)

def strip_accents(text):
    """Remove accents from Greek text while preserving the letter case"""
    return ''.join(c for c in unicodedata.normalize('NFD', text)
                  if unicodedata.category(c) != 'Mn')

def normalize_greek_word(word):
    """Normalize a Greek word by removing accents and converting to lowercase"""
    return strip_accents(word.lower())

def get_stop_words(language='both'):
    """Get stop words for the specified language(s)"""
    stop_words = set()
    
    # Custom stop words for songs (both languages)
    custom_stop_words = {
        # English
        'chorus', 'verse', 'bridge', 'yeah', 'oh', 'uh', 'hey',
        'gonna', 'wanna', 'gotta', 'let', 'like', 'know', 'way',
        'make', 'made', 'say', 'said', 'get', 'got', 'one',
        # Greek - include both accented and non-accented versions
        'ρεφρέν', 'ρεφρεν', 'στίχος', 'στιχος', 'γέφυρα', 'γεφυρα',
        'είναι', 'ειναι', 'έχω', 'εχω', 'έχει', 'εχει',
        'είμαι', 'ειμαι', 'ήταν', 'ηταν', 'κάνω', 'κανω',
        'κάνει', 'κανει', 'πάει', 'παει', 'πάω', 'παω',
        'μου', 'σου', 'του', 'της', 'μας', 'σας', 'τους',
        'και', 'να', 'θα', 'τι', 'που', 'πως', 'γιατί', 'γιατι',
        'μην', 'ένα', 'ενα', 'μία', 'μια', 'ένας', 'ενας',
        'την', 'τον', 'εγώ', 'εγω', 'εσύ', 'εσυ',
        'αυτό', 'αυτο', 'αυτή', 'αυτη', 'αυτός', 'αυτος',
        'μα', 'μες', 'όλοι', 'ολοι', 'όλα', 'ολα',
        'έχεις', 'εχεις', 'κάτι', 'κατι', 'μέσα', 'μεσα',
        'πια', 'στους', 'είσαι', 'εισαι', 'όταν', 'οταν',
        # Additional Greek stopwords
        'απ', 'σ', 'πιο', 'κ', 'λες', 'λεω', 'στα', 'σαν', 
        'μονο', 'καθε', 'παντα', 'ποσο', 'ξανα', 'ξερω', 
        'αλλη', 'κατω', 'πανω', 'παλι', 'ποσο', 'εχουνε', 
        'ακομα', 'στις', 'λοιπον'
    }
    
    if language in ['english', 'both']:
        stop_words.update(set(stopwords.words('english')))
    
    if language in ['greek', 'both']:
        greek_stops = set(stopwords.words('greek'))
        # Convert Greek stop words to lowercase
        greek_stops = {word.lower() for word in greek_stops}
        stop_words.update(greek_stops)
    
    stop_words.update(custom_stop_words)
    return stop_words

def is_greek_text(text):
    """Check if text contains Greek characters"""
    # Regular expression for Greek characters
    greek_pattern = re.compile(r'[\u0370-\u03FF\u1F00-\u1FFF]')
    return bool(greek_pattern.search(text))

def is_english_text(text):
    """Check if text contains primarily English characters"""
    # Regular expression for English words (allowing for apostrophes and hyphens)
    english_pattern = re.compile(r'^[a-zA-Z\'-]+$')
    # Count words that match English pattern
    words = text.split()
    if not words:
        return False
    english_words = sum(1 for word in words if english_pattern.match(word))
    return english_words / len(words) > 0.5

def filter_lyrics_by_language(text, language):
    """Filter lyrics by language at the line level"""
    if language == 'both':
        return text
        
    lines = text.split('\n')
    filtered_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:  # Skip empty lines
            continue
            
        if language == 'greek' and is_greek_text(line):
            filtered_lines.append(line)
        elif language == 'english' and is_english_text(line):
            filtered_lines.append(line)
    
    return '\n'.join(filtered_lines)

def load_lyrics(artist_name, album_name=None):
    """Load lyrics from cache or fetch them if not available"""
    cache_file = f"{artist_name.replace(' ', '_').lower()}_lyrics.json"
    
    # Check if we need to fetch new lyrics
    if not os.path.exists(cache_file):
        artist_data = fetch_artist_data(artist_name)
        if artist_data:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(artist_data, f, indent=4, ensure_ascii=False)
    
    # Load the lyrics data
    with open(cache_file, 'r', encoding='utf-8') as f:
        artist_data = json.load(f)
    
    # Combine all lyrics based on album selection
    all_lyrics = []
    
    for album in artist_data.get('albums', []):
        if album_name is None or album['album_name'].lower() == album_name.lower():
            for track in album['tracks']:
                if track['lyrics'] != "No lyrics found for this track.":
                    all_lyrics.append(track['lyrics'])
    
    return '\n'.join(all_lyrics)

def generate_wordcloud(text, title, language='both'):
    """Generate and display a word cloud from the given text"""
    # Get stop words for the specified language(s)
    stop_words = get_stop_words(language)
    
    # If we're dealing with Greek text, normalize it
    if language in ['greek', 'both']:
        # Pre-process the text to normalize Greek words
        words = text.split()
        normalized_words = [normalize_greek_word(word) if is_greek_text(word) else word.lower() for word in words]
        text = ' '.join(normalized_words)
    
    # Create and generate a word cloud image
    wordcloud = WordCloud(
        width=1600, 
        height=800,
        background_color='white',
        stopwords=stop_words,
        min_font_size=10,
        max_font_size=150,
        random_state=42
    ).generate(text)
    
    # Display the word cloud
    plt.figure(figsize=(20,10))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title(title, fontsize=20, pad=20)
    plt.show()

def generate_artist_wordcloud(artist_name, album_name=None, language='both'):
    """Generate a word cloud for an artist's lyrics"""
    # Load lyrics
    lyrics_text = load_lyrics(artist_name, album_name)
    
    if not lyrics_text:
        raise ValueError(f"No lyrics found for {'album ' + album_name if album_name else 'artist ' + artist_name}")
    
    # Filter lyrics by language
    filtered_lyrics = filter_lyrics_by_language(lyrics_text, language)
    
    if not filtered_lyrics:
        raise ValueError(f"No lyrics found in {language} for {'album ' + album_name if album_name else 'artist ' + artist_name}")
    
    # Generate title
    title = f"Word Cloud for {artist_name}"
    if album_name:
        title += f" - {album_name}"
    title += f" ({language.title()} lyrics)"
    
    # Generate and display word cloud
    generate_wordcloud(filtered_lyrics, title, language)
