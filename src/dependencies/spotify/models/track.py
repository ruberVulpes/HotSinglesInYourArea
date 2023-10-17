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

    def artists_string(self) -> str:
        return ", ".join(artist.name for artist in self.artists)

    def __hash__(self):
        return hash(self.id)

    @staticmethod
    def coalesce_tracks(tracks: list['Track']) -> list['Track']:
        result = set()
        for track in tracks:
            result.add(max((t for t in tracks if track == t), key=lambda t: t.popularity))
        return sorted(result, key=lambda t: t.popularity, reverse=True)

    def __eq__(self, other: 'Track'):
        if not isinstance(other, Track):
            return NotImplemented
        if self.id == other.id:
            return True
        for key, value in self.external_ids.items():
            if other.external_ids[key] == value:
                return True
        if (self.name, self.artists_string, self.explicit) == (other.name, other.artists_string(), not other.explicit):
            return True
        return False
