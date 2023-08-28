from enum import StrEnum, auto


class Type(StrEnum):
    album = auto()
    artist = auto()
    playlist = auto()
    track = auto()
    show = auto()
    episode = auto()
    audiobook = auto()


class AlbumType(StrEnum):
    album = "album"
    single = "single"
    compilation = "compilation"


class ReleaseDatePrecision(StrEnum):
    year = "year"
    month = "month"
    day = "day"
