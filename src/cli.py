import click
from dotenv import load_dotenv
from spotipy import Spotify, SpotifyOAuth

from dependencies.click import valid_year_range
from dependencies.spotify.utils import get_spotify_songs, create_spotify_playlist
from dependencies.wikipedia.utils import get_billboard_hot_singles

load_dotenv()


@click.command(name="HotSinglesInYourArea")
@click.option("-s", "--start-year", type=valid_year_range, help="The year to start collecting songs from")
@click.option("-e", "--end-year", type=valid_year_range, help="The year to end collecting songs from")
@click.option("--limit", type=click.IntRange(min=1), default=300, help="The number of songs to use for the playlist")
def cli(start_year: int, end_year: int, limit: int):
    main(start_year, end_year, limit)


def main(start_year: int, end_year: int | None, limit: int):
    click.echo('CLI')
    end_year = end_year or start_year
    playlist_name = f"HotSinglesInYourArea {start_year} - {end_year}"
    singles = get_billboard_hot_singles(start_year, end_year)
    spotify_client = Spotify(auth_manager=SpotifyOAuth(scope="playlist-modify-public"))
    tracks = sorted(get_spotify_songs(singles, spotify_client), key=lambda t: t.popularity, reverse=True)
    create_spotify_playlist(tracks, spotify_client, playlist_name=playlist_name, limit=limit)


if __name__ == '__main__':
    main(2012, None, 300)
