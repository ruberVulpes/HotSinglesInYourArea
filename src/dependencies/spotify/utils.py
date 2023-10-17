import concurrent
import math
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from functools import cache

from spotipy import Spotify
from tqdm import tqdm

from dependencies.spotify.models import Track
from dependencies.wikipedia.models import Single


def get_spotify_track_from_single(single: Single, spotify_client: Spotify, use_artist=True) -> tuple[float, Track]:
    if items := spotify_client.search(q=single.spotify_search_string(use_first_artist=True))["tracks"]["items"]:
        tracks = Track.coalesce_tracks([Track(**_) for _ in items])
        if fuzz_track := single.fuzz_spotify_tracks(tracks):
            return fuzz_track
    if items := spotify_client.search(q=single.spotify_search_string(use_first_artist=False))["tracks"]["items"]:
        tracks = Track.coalesce_tracks([Track(**_) for _ in items])
        if fuzz_track := single.fuzz_spotify_tracks(tracks):
            return fuzz_track


def get_spotify_track_from_single_replace_artist(single: Single, spotify_client: Spotify) -> tuple[float, Track]:
    single = deepcopy(single)
    single.artists = [spotify_client.search(q=single.artist_query, type="artist")["artists"]["items"][0]["name"]]
    return get_spotify_track_from_single(single, spotify_client, use_artist=True)


@cache
def get_artist_top_tracks(artist_id: str, spotify_client: Spotify) -> list[Track]:
    return Track.coalesce_tracks([Track(**_) for _ in spotify_client.artist_top_tracks(artist_id)["tracks"]])


def get_spotify_tracks_from_artist(single: Single, spotify_client: Spotify) -> tuple[float, Track]:
    artist_id = spotify_client.search(q=single.artist_query, type="artist")["artists"]["items"][0]["id"]
    tracks = get_artist_top_tracks(artist_id, spotify_client)
    if fuzz_track := single.fuzz_spotify_tracks(tracks):
        return fuzz_track


def get_spotify_track_with_fallback(single: Single, spotify_client: Spotify) -> Track:
    tracks = list()
    if track := get_spotify_track_from_single(single, spotify_client):
        tracks.append(track)
    if track := get_spotify_tracks_from_artist(single, spotify_client):
        tracks.append(track)
    if not tracks:
        if track := get_spotify_track_from_single_replace_artist(single, spotify_client):
            tracks.append(track)
    result = max(tracks, key=lambda tup: tup[0])
    return result[-1]


def get_spotify_songs(singles: list[Single], spotify_client: Spotify) -> list[Track]:
    tracks = [None] * len(singles)
    with ThreadPoolExecutor() as executor:
        future_to_single = {executor.submit(get_spotify_track_with_fallback, single, spotify_client): single for single
                            in singles}
        with tqdm(total=len(singles), desc="Finding Spotify Tracks") as pbar:
            for future in concurrent.futures.as_completed(future_to_single):
                single = future_to_single[future]
                tracks[single.number - 1] = future.result()
                pbar.update(1)
    if None in tracks:
        print("Fuck")
    return tracks


def create_spotify_playlist(
        tracks: list[Track],
        spotify_client: Spotify,
        playlist_name="SpotifyByTheYears",
        playlist_id: str | None = None,
        limit=300,
) -> str:
    playlist_id = playlist_id or spotify_client.user_playlist_create(spotify_client.me()["id"], playlist_name)["id"]
    tracks = list({t.uri for t in tracks})[:limit]
    with tqdm(total=math.ceil(len(tracks) / 100), desc=f"Adding the songs to the playlist") as pbar:
        while tracks:
            spotify_client.playlist_add_items(playlist_id, tracks[:100])
            tracks = tracks[100:]
            pbar.update(1)
    return playlist_id
