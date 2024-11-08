# Subtitle Organizer and Synchronizer

This Python script automates the process of downloading, synchronizing, and organizing movie subtitle files. It integrates with external tools to download subtitles, synchronize them with a reference file, and organize them into directories named after the movies.



## Features

- **Download Subtitles**: Uses `isubrip` to download subtitles from any iTunes movie URL.
- **Synchronize Subtitles**: Utilizes `ffsubsync` to synchronize the downloaded subtitles with a reference `.srt` file.
- **Organize Subtitles**: Renames and organizes subtitles into directories based on movie titles and release years, retrieved from The Movie Database (TMDb) API.
- **Language Mapping**: Automatically maps language codes to descriptive language names using the `pycountry` library.


## Prerequisites

- **Windows**: This script is Windows only due to some dependencies, however, can be adapted easily if you wish.
- **Python 3.x**: Ensure you have Python 3 installed.
- **TMDb API Key**: Sign up for an API key at [The Movie Database (TMDb)](https://www.themoviedb.org/documentation/api).


## Installation

1. Download the repository as a .zip
2. Extract the .zip to a location of your choosing. (A separate sub-directory is **highly** recommended)


## Configuration

- The script automatically creates a configuration file for `isubrip` at `%USERPROFILE%\.isubrip\config.toml`. This file specifies the download folder and other settings.
- Make sure to update yout TMDb API key in the script.py file.



## Usage

1. Open a command prompt window within the current directory
2. Install requirements `pip install -r requirements.txt`
3. Run script with either provided `Start.bat` or `script.py`
4. Enter iTunes movie URL when requested (this script does not work with TV shows, as is the same with isubrip)
5. Select existing .srt file as extracted from existing movie file or converted using OCR
6. Script will quit when complete and files will be found in a directory named "Movie Name (Movie Year)"
7. Done


## Dependencies

-   **Python Packages**:
    -   `requests`
    -   `pycountry`
-   **External Tools**:
    -   `isubrip`
    -   `ffsubsync`
-   **System Libraries**:
    -   `tkinter` (usually included with Python)


## Notes

-   Ensure that both `isubrip` and `ffsubsync` are installed and accessible from your command line.
-   The script is designed for Windows systems due to the use of `%USERPROFILE%`. For Unix-based systems, modifications may be needed to use `$HOME` instead.
-   The script uses `tkinter` for the file dialog. If `tkinter` is not installed, you may need to install it separately.


## Troubleshooting

-   **Invalid TMDb API Key**: If the script exits with an error about the TMDb API key, ensure you've correctly replaced `'YOUR_TMDB_API_KEY'` with your actual API key.
-   **ModuleNotFoundError**: If you receive an error about missing modules, ensure all Python dependencies are installed using the `requirements.txt` file.
-   **External Tools Not Found**: If the script cannot find `isubrip` or `ffsubsync`, make sure they are installed and added to your system's PATH.


## License

This project is licensed under the MIT License.


## Acknowledgments

-   **[iSubRip](https://github.com/MichaelYochpaz/iSubRip)** for subtitle downloading capabilities.
-   **[ffsubsync](https://github.com/smacke/ffsubsync)** for subtitle synchronization.
-   **[The Movie Database (TMDb)](https://www.themoviedb.org/)** for movie data.
-   **[pycountry](https://pypi.org/project/pycountry/)** for language code mappings.
