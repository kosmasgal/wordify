from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="wordify",
    version="0.1.0",
    author="Kosmas Galanos",
    description="Generate word clouds from song lyrics with multilingual support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kosmasgal/wordify",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Natural Language :: Greek",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.6",
    install_requires=[
        "flask>=2.2.2",
        "spotipy>=2.22.1",
        "python-dotenv>=1.0.0",
        "beautifulsoup4>=4.12.2",
        "requests>=2.31.0",
        "numpy>=1.23.5",
        "pillow>=9.4.0",
        "matplotlib>=3.7.1",
        "wordcloud>=1.9.0",
        "nltk>=3.8.1",
    ],
    entry_points={
        'console_scripts': [
            'wordify=wordify.wordify:main',
        ],
    },
)
