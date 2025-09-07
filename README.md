# Wordify

A Python application that generates word clouds from song lyrics, with special support for multilingual (Greek/English) lyrics processing. Based on the implementation of [syrics-web](https://github.com/akashrchandran/syrics-web/tree/master).

## Features

- Fetch lyrics for any artist or specific album from Spotify
- Generate word clouds from song lyrics
- Language-specific processing:
  - Support for both Greek and English lyrics
  - Smart language detection and filtering
  - Proper handling of Greek accents and diacritics
  - Customizable stopwords for both languages
- Caching of lyrics data for faster subsequent runs
- Flexible output customization (size, colors, etc.)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/kosmasgal/wordify.git
cd wordify
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\Activate.ps1
# On Unix or MacOS:
source venv/bin/activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

The main script can be run with various options:

```bash
python wordify.py "Artist Name" [options]
```

### Options:
- `--album "Album Name"`: Generate word cloud for a specific album (optional)
- `--lang {english,greek,both}`: Specify the language for word cloud generation (default: both)

### Examples:

Generate word cloud for all songs by an artist:
```bash
python wordify.py "Artist Name"
```

Generate word cloud for a specific album in Greek:
```bash
python wordify.py "Artist Name" --album "Album Name" --lang greek
```

## Configuration

The word cloud generation can be customized by modifying parameters in `generate_wordcloud.py`:
- Word cloud dimensions
- Background color
- Font sizes
- Custom stopwords

## Credits

This project is based on the implementation of [syrics-web](https://github.com/akashrchandran/syrics-web/tree/master) by [akashrchandran](https://github.com/akashrchandran).

## Dependencies

- flask
- spotipy
- python-dotenv
- beautifulsoup4
- requests
- numpy
- pillow
- matplotlib
- wordcloud
- nltk

## License

This project is licensed under the MIT License - see the LICENSE file for details.
