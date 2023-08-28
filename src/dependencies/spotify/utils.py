
import math

from spotipy import Spotify
from tqdm import tqdm

from dependencies.spotify.models import Track
from dependencies.wikipedia import Single


def get_spotify_track_from_single(single: Single, spotify_client: Spotify) -> Track:
    for use_artist in (False, True):
        if items := spotify_client.search(q=single.spotify_search_string(use_artist))["tracks"]["items"]:
            tracks = [Track(**_) for _ in items]
            for track in tracks:
                if single.is_spotify_track(track):
                    return track


def get_spotify_track_from_single_replace_artist(single: Single, spotify_client: Spotify) -> Track:
    for artist in spotify_client.search(q=single.artist_query, type="artist")["artists"]["items"]:
        single.artists.append(artist["name"])
        return get_spotify_track_from_single(single, spotify_client)


def get_spotify_songs(singles: list[Single], spotify_client: Spotify) -> list[Track]:
    tracks = list()
    # with ThreadPoolExecutor() as executor:
    #     future_to_row = {executor.submit(get_spotify_track_from_single, single, spotify_client): single for single in
    #                      singles}
    #     with tqdm(total=len(singles), desc="Finding Spotify Tracks") as pbar:
    #         for future in concurrent.futures.as_completed(future_to_row):
    #             tracks.append(future.result())
    #             pbar.update(1)
    for single in tqdm(singles):
        if track := get_spotify_track_from_single(single, spotify_client):
            tracks.append(track)
        elif track := get_spotify_track_from_single_replace_artist(single, spotify_client):
            tracks.append(track)
        else:
            print('Fuck')
    return tracks


def create_spotify_playlist(tracks: list[Track], spotify_client: Spotify, playlist_name="SpotifyByTheYears",
                            playlist_id: str | None = None, limit=300) -> str:
    playlist_id = playlist_id or spotify_client.user_playlist_create(spotify_client.me()['id'], playlist_name)["id"]
    tracks = list({t.uri for t in tracks})[:limit]
    with tqdm(total=math.ceil(len(tracks) / 100), desc=f"Adding the songs to the playlist") as pbar:
        while tracks:
            spotify_client.playlist_add_items(playlist_id, tracks[:100])
            tracks = tracks[100:]
            pbar.update(1)
    return playlist_id
