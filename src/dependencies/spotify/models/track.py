from typing import Optional

from dependencies.spotify.models import Album
from dependencies.spotify.models import Artist
from dependencies.spotify.models import SpotifyBaseModel


class Track(SpotifyBaseModel):
    album: Album
    artists: list[Artist]
    available_markets: Optional[list[str]] = []
    disc_number: int
    duration_ms: int
    explicit: bool
    external_ids: dict
    is_local: bool
    popularity: int
    preview_url: str | None
    track_number: int

    def __str__(self):
        name = self.name
        album = self.album.name
        artists = self.artists
        return f"{self.__class__.__name__}({name=}, {album=}, {artists=})"
