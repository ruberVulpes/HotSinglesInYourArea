from dotenv import load_dotenv
from spotipy import Spotify, SpotifyOAuth

from dependencies.spotify import get_spotify_songs
from dependencies.wikipedia import get_billboard_hot_singles

load_dotenv()


def main(start_year=2021, end_year=2022):
    end_year = end_year or start_year
    playlist_name = f"HotSinglesInYourArea Popular {start_year} - {end_year}"
    singles = get_billboard_hot_singles(start_year, end_year)[28:]
    spotify_client = Spotify(auth_manager=SpotifyOAuth(scope="playlist-modify-public"))
    tracks = sorted(get_spotify_songs(singles, spotify_client), key=lambda t: t.popularity, reverse=True)
    # playlist_id = create_spotify_playlist(tracks, spotify_client, playlist_name=playlist_name, limit=300)
    print()


if __name__ == '__main__':
    main()
