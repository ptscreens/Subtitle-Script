import os
import re
import sys
import shutil
import requests
import pycountry
import subprocess

# For file dialog
import tkinter as tk
from tkinter import filedialog

# Initialize tkinter
root = tk.Tk()
root.withdraw()

# Replace 'YOUR_TMDB_API_KEY' with your actual TMDb API key
TMDB_API_KEY = 'YOUR_TMDB_API_KEY'

def validate_tmdb_api_key():
    """Validates the TMDb API key by making a test request."""
    if TMDB_API_KEY == 'YOUR_TMDB_API_KEY':
        print('TMDb API key not set. Please replace "YOUR_TMDB_API_KEY" with your actual TMDb API key in the script.')
        sys.exit(1)
    else:
        response = requests.get(
            'https://api.themoviedb.org/3/configuration',
            params={'api_key': TMDB_API_KEY}
        )
        if response.status_code != 200:
            print("Invalid TMDb API key. Please check your API key and try again.")
            sys.exit(1)
        # Do not print anything if the API key is valid.

def create_isubrip_config():
    r"""Creates the isubrip config file at %USERPROFILE%\.isubrip\config.toml with the specified contents."""
    user_profile = os.environ.get('USERPROFILE')
    if not user_profile:
        print("Could not determine USERPROFILE directory.")
        sys.exit(1)
    config_dir = os.path.join(user_profile, '.isubrip')
    os.makedirs(config_dir, exist_ok=True)
    config_path = os.path.join(config_dir, 'config.toml')

    # Construct the absolute path to the 'Input' directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(script_dir, 'Input')
    input_dir = os.path.abspath(input_dir)
    # Escape backslashes for TOML
    input_dir_escaped = input_dir.replace('\\', '\\\\')

    # Content of the config file
    config_content = f"""[general]
# Check for updates before running, and show a note if a new version exists.
# Value can be either 'true' or 'false'.
check-for-updates = true

[downloads]
# Folder to download files to.
# Use double backslashes in path to avoid escaping characters. Example: "C:\\\\Users\\\\<username>\\\\Downloads\\\\"
folder = "{input_dir_escaped}"

# A list of iTunes language codes to download.
# An empty array (like the one currently being used) will result in downloading all of the available subtitles.
# Example: ["en-US", "fr-FR", "he"]
languages = []

# Whether to overwrite existing subtitles files.
# If set to false, names of existing subtitles will have a number appended to them to avoid overwriting.
# Value can be either 'true' or 'false'.
overwrite-existing = false

# Save files into a zip archive if there is more than one matching subtitle.
# Value can be either 'true' or 'false'.
zip = false

[subtitles]
# Fix RTL for RTL languages (Arabic & Hebrew).
# Value can be either 'true' or 'false'.
#
# NOTE: This is off by default as some subtitles use other methods to fix RTL (like writing punctuations backwards).
#       Using this option on these type of subtitles can break the already-fixed RTL issues.
fix-rtl = false

# Remove duplicate paragraphs (same text and timestamps).
# Value can be either 'true' or 'false'.
remove-duplicates = true

# Whether to convert subtitles to SRT format.
# NOTE: This can cause loss of subtitles metadata that is not supported by SRT format.
convert-to-srt = true

[subtitles.webvtt]
# Whether to add a '{{\\an8}}' tag to lines that are aligned at the top when converting format from WebVTT to SubRip.
# Relevant only if 'subtitles.convert-to-srt' is set to 'true'.
# Value can be either 'true' or 'false'.
subrip-alignment-conversion = false

[scrapers]
# Timeout in seconds for requests sent by all scrapers.
# Will be overridden by scraper-specific timeout configuration, if set.
timeout = 10

# User-Agent to use by default for requests sent by all scrapers.
# Will be overridden by scraper-specific user-agent configuration, if set.
#user-agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"

# Whether to verify SSL certificates when making requests for all scrapers.
# Value can be either 'true' or 'false'.
# Will be overridden by scraper-specific verify-ssl configuration, if set.
verify-ssl = true

# The following are scraper-specific settings (can be set for each scraper separately).
# Replace 'enter-scraper-name-here' with the name of the scraper you want to configure.
# Available scrapers: itunes, appletv
[scrapers.enter-scraper-name-here]
# Timeout in seconds for requests sent by the scraper.
timeout = 10
"""

    # Write the config file
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(config_content)
    # Suppressing the print statement to avoid unnecessary output
    # print(f"Created isubrip config file at {config_path}")

def download_and_sync_subtitles():
    # Ensure the necessary directories exist
    INPUT_DIR = 'Input'
    COMPLETED_DIR = 'Completed Source Files'
    SYNCED_DIR = 'Synced'  # This will be used as the OUTPUT_DIR later

    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(COMPLETED_DIR, exist_ok=True)
    os.makedirs(SYNCED_DIR, exist_ok=True)

    # Prompt the user for the URL
    url = input("Please enter an iTunes movie URL: ")

    # Change to the Input directory and run 'isubrip' with the URL
    current_dir = os.getcwd()
    os.chdir(INPUT_DIR)

    try:
        result = subprocess.run(['isubrip', url], check=True)
    except subprocess.CalledProcessError as e:
        print("An error occurred while running isubrip.")
        sys.exit(1)
    finally:
        # Change back to the original directory even if an error occurs
        os.chdir(current_dir)

    # Prompt the user to select the reference file using a file dialog
    ref = filedialog.askopenfilename(title="Select Reference Subtitle File", filetypes=[("Subtitle files", "*.srt")])
    if not ref:
        print("No reference file selected. Exiting.")
        sys.exit(1)

    # Process each .srt file in the Input directory
    for filename in os.listdir(INPUT_DIR):
        if filename.lower().endswith('.srt'):
            input_file = os.path.join(INPUT_DIR, filename)
            output_file = os.path.join(SYNCED_DIR, filename)
            try:
                result = subprocess.run(['ffsubsync', ref, '-i', input_file, '-o', output_file], check=True)
            except subprocess.CalledProcessError as e:
                print(f"An error occurred while processing '{filename}'.")
                continue
            # Move the original input file to 'Completed Source Files'
            shutil.move(input_file, os.path.join(COMPLETED_DIR, filename))

def organize_subtitles():
    # Directory paths
    OUTPUT_DIR = 'Synced'  # Now we use 'Synced' as our OUTPUT_DIR

    # Tokens to ignore during parsing
    IGNORED_TOKENS = ['iT', 'WEB', 'BluRay', 'HDRip', 'HDTV', 'x264', '720p', '1080p', 'DVDRip']

    def extract_movie_info(filename):
        # Remove extension
        name = os.path.splitext(filename)[0]
        parts = name.split('.')
        title_parts = []
        year = None
        year_pattern = re.compile(r'^(19|20)\d{2}$')
        for part in parts:
            if part in IGNORED_TOKENS:
                continue
            if year_pattern.match(part):
                year = part
                break
            else:
                title_parts.append(part)
        title = ' '.join(title_parts)
        return title.strip(), year

    def search_movie(title, year=None):
        params = {
            'api_key': TMDB_API_KEY,
            'query': title,
            'language': 'en-US',
        }
        if year:
            params['year'] = year
        response = requests.get(f'https://api.themoviedb.org/3/search/movie', params=params)
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            if results:
                return results[0]
        return None

    def create_movie_directory(movie_title, movie_year):
        dir_name = f'{movie_title} ({movie_year})'
        dir_name = re.sub(r'[<>:"/\\|?*]', '', dir_name)
        movie_dir = os.path.join(dir_name)
        os.makedirs(movie_dir, exist_ok=True)
        return movie_dir

    def extract_language_info(filename):
        name = os.path.splitext(filename)[0]
        parts = name.split('.')
        lang_code = ''
        sub_type = ''
        for part in reversed(parts):
            part_lower = part.lower()
            if part in IGNORED_TOKENS or part_lower in IGNORED_TOKENS:
                continue
            if part_lower in ['cc', 'forced', 'sdh']:
                sub_type = part_lower
                continue
            if re.match(r'^[a-z]{2,3}(-[a-zA-Z0-9]{2,8})?$', part_lower):
                lang_code = part
                break
        return lang_code, sub_type

    def get_language_name(lang_code):
        try:
            # Custom mapping for non-standard codes
            custom_mappings = {
                'yue-Hant': 'Cantonese-Traditional',
                'cmn-Hans': 'Mandarin Chinese-Simplified',
                'cmn-Hant': 'Mandarin Chinese-Traditional',
                # Add more custom mappings as needed
            }
            if lang_code in custom_mappings:
                return custom_mappings[lang_code]

            # Handle language codes with hyphens (e.g., 'en-US')
            if '-' in lang_code:
                base_code = lang_code.split('-')[0]
            else:
                base_code = lang_code

            # Try to get the language name using alpha_2 code
            language = pycountry.languages.get(alpha_2=base_code)
            if language:
                language_name = language.name
            else:
                # Try alpha_3 code
                language = pycountry.languages.get(alpha_3=base_code)
                if language:
                    language_name = language.name
                else:
                    # If not found, return the language code
                    return lang_code

            # Append script or region if present
            if '-' in lang_code:
                variant = lang_code.split('-')[1]
                language_name = f"{language_name}-{variant}"

            return language_name
        except Exception:
            return lang_code

    def rename_subtitle_file(original_filepath, movie_title, movie_year, lang_code, sub_type):
        lang_name = get_language_name(lang_code)
        movie_title_formatted = movie_title.replace(' ', '.')
        if sub_type:
            new_filename = f'{movie_title_formatted}.{movie_year}.{lang_name}_{sub_type}.srt'
        else:
            new_filename = f'{movie_title_formatted}.{movie_year}.{lang_name}.srt'
        new_filename = re.sub(r'[<>:"/\\|?*]', '', new_filename)
        return new_filename

    # Process each subtitle file in the OUTPUT_DIR
    for filename in os.listdir(OUTPUT_DIR):
        if filename.lower().endswith('.srt'):
            filepath = os.path.join(OUTPUT_DIR, filename)

            # Extract movie info
            movie_title, movie_year = extract_movie_info(filename)

            # Search for the movie on TMDb
            movie = search_movie(movie_title, movie_year)
            if movie:
                official_title = movie['title']
                release_year = movie['release_date'].split('-')[0]
            else:
                official_title = movie_title
                release_year = movie_year or 'Unknown'

            # Create movie directory
            movie_dir = create_movie_directory(official_title, release_year)

            # Extract language code and subtitle type
            lang_code, sub_type = extract_language_info(filename)
            if not lang_code:
                lang_code = 'unknown'

            # Rename the subtitle file
            new_filename = rename_subtitle_file(filepath, official_title, release_year, lang_code, sub_type)
            dest_file = os.path.join(movie_dir, new_filename)

            # Check for existing files and append a number if necessary
            base_name, ext = os.path.splitext(new_filename)
            count = 1
            while os.path.exists(dest_file):
                dest_file = os.path.join(movie_dir, f'{base_name}_{count}{ext}')
                count += 1

            # Move and rename the file
            shutil.move(filepath, dest_file)
            print(f'Moved and renamed {filename} to {dest_file}')
            print('---')

    print("Subtitles have been downloaded, synced, named and organised.")
    
    
def main():
    validate_tmdb_api_key()
    create_isubrip_config()
    download_and_sync_subtitles()
    organize_subtitles()

if __name__ == '__main__':
    main()
