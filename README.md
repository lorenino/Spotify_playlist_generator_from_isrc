# Spotify Playlist Generator from ISRC

This Python script generates a Spotify playlist from a list of ISRC codes provided in a CSV file. It uses the Spotify Web API to search for tracks by their ISRC codes and adds them to a new playlist.

## Features

- Reads ISRC codes from a CSV file.
- Creates a new Spotify playlist.
- Searches for tracks using ISRC codes and adds them to the playlist.
- Handles API rate limiting and retries on failures.

## Requirements

- Python 3.7 or higher
- Spotipy library
- pandas library
- tqdm library
- python-dotenv library

## Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/lorenino/Spotify_playlist_generator_from_isrc.git
    cd Spotify_playlist_generator_from_isrc
    ```

2. Create and activate a virtual environment (optional but recommended):

    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required libraries:

    ```sh
    pip install -r requirements.txt
    ```

4. Create a `.env` file in the project directory and add your Spotify API credentials:

    ```env
    SPOTIPY_CLIENT_ID=your_client_id
    SPOTIPY_CLIENT_SECRET=your_client_secret
    SPOTIPY_REDIRECT_URI=http://localhost:8888/callback
    ```

## Usage

1. Prepare a CSV file with a column named `ISRC` containing the ISRC codes of the tracks.

2. Run the script:

    ```sh
    python spotify_playlist_creator.py
    ```

3. When prompted, enter the path to your CSV file and the name of the new playlist.

## Example

Here's an example of how the CSV file should look: 

or extracted from https://www.tunemymusic.com : 

```csv
ISRC
USUM71704382
USUM71703361
USUM71702167
