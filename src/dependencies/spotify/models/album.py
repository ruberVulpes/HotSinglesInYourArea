from typing import Optional

from dependencies.spotify.models import Artist
from dependencies.spotify.models import SpotifyBaseModel
from dependencies.spotify.models import AlbumType, ReleaseDatePrecision


class Album(SpotifyBaseModel):
    album_type: AlbumType
    artists: list[Artist]
    available_markets: Optional[list[str]] = []
    images: list[dict]
    release_date: str
    release_date_precision: ReleaseDatePrecision
    total_tracks: int

    def __str__(self):
        name = self.name
        release_date = self.release_date
        artists = self.artists
        return f"{self.__class__.__name__}({name=}, {release_date=}, {artists=})"
