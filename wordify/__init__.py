"""
Wordify - Generate word clouds from song lyrics with multilingual support
"""

from .generate_wordcloud import (
    generate_artist_wordcloud,
    generate_wordcloud,
    get_stop_words,
    normalize_greek_word
)

__version__ = '0.1.0'
__author__ = 'Kosmas Galanos'
