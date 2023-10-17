import itertools
from dataclasses import dataclass

import rapidfuzz.process
from bs4 import Tag
import re

from rapidfuzz import fuzz
from rapidfuzz.utils import default_process

from dependencies.rapidfuzz.processor import custom_processor
from dependencies.spotify.models import Track

artist_delimiters = (", ", " and ", " featuring ", " or ")


@dataclass
class Single:
    year: int
    number: int
    title: str
    artists: list[str]

    # def __post_init__(self):
    #     if self.index in ((2000, 97), (2001, 10)):
    #         self.title = self.title.replace("Part I", "Pt. 1")
    #     if self.index == (2001, 28):
    #         self.title = self.title.replace("U", "You")
    #     if self.index == (2001, 54):
    #         self.artists = [" and ".join(self.artists)]
    #     if self.index == (2002, 13):
    #         self.title = "Ain't It Funny (feat. Ja Rule & Cadillac Tah) - Murder Remix"
    #     if self.index == (2002, 15):
    #         self.title = "I Need a Girl (Pt. 1) [feat. Usher & Loon]"
    #     if self.index == (2002, 18):
    #         self.title = "I Need a Girl (Pt. 2) [feat. Loon, Ginuwine, Mario Winans]"
    #     if self.index == (2005, 33):
    #         self.title = "Obsesion (No Es Amor) (feat. Baby Bash)"
    #     if self.index == (2006, 75):
    #         self.title = "Deja Vu (feat. Jay-Z)"
    #     if self.index == (2007, 22):
    #         self.title = "What Goes Around.../...Comes Around (Interlude)"
    #     if self.index == (2008, 38):
    #         self.title = "Bust It Baby, Pt. 2 (feat. Ne-Yo)"
    #     if self.index == (2021, 28):
    #         self.title = "DÁKITI"

    @property
    def index(self):
        return self.year, self.number

    @property
    def track_query(self):
        return f"{self.title}"

    @property
    def artist_query(self):
        return f"{self.artists[0]}"

    def spotify_search_string(self, use_first_artist: bool) -> str:
        return f"{self.track_query} {f'artist:{self.artist_query}' if use_first_artist else ''}"

    def artists_string(self) -> str:
        return ", ".join(self.artists)

    def fuzz_spotify_tracks(self, tracks: list[Track]) -> tuple[float, Track]:
        filtered_tracks = list()
        for track in tracks:
            artist_ratio = fuzz.WRatio(self.artists_string(), track.artists_string(), processor=custom_processor)
            if artist_ratio >= 75:
                title_ratio = fuzz.WRatio(self.title, track.name, processor=custom_processor)
                if title_ratio >= 80:
                    filtered_tracks.append(((artist_ratio + title_ratio), track))
        if filtered_tracks:
            # TODO: Combine line after done debugging
            result = max((track for track in filtered_tracks), key=lambda t: t[0])
            return result[0], result[-1]

    def fuzz_track(self, track: Track) -> float:
        if "feat" in track.name:
            title_ratio = fuzz.partial_ratio(self.title, track.name, processor=custom_processor)
        else:
            title_ratio = fuzz.ratio(self.title, track.name, processor=custom_processor)
        return title_ratio + fuzz.ratio(self.artists_string(), track.artists_string(), processor=custom_processor)

    @staticmethod
    def from_bs4(tag: Tag, year: int):
        try:
            td_number, td_title, td_artists = map(lambda td: td.text.strip(), tag.find_all("td"))
        except ValueError:
            # Sometimes Artist columns are reused for subsequent rows so take from the previous
            td_number, td_title = map(lambda td: td.text.strip(), tag.find_all("td"))
            *_, td_artists = map(lambda td: td.text.strip(), tag.find_previous("tr").find_all("td"))
        number = int(td_number)
        title = td_title[1:-1]

        artists = re.split("|".join(map(re.escape, artist_delimiters)), td_artists)
        return Single(year, number, title, artists)

    def __lt__(self, other):
        if isinstance(other, Single):
            return (self.year, self.number) < (other.year, other.number)
        return NotImplemented
