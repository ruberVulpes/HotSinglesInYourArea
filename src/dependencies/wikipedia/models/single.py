import itertools
from dataclasses import dataclass

from bs4 import Tag
import re

from dependencies.spotify.models import Track

artist_delimiters = (", ", " and ", " featuring ", " or ")


@dataclass
class Single:
    year: int
    number: int
    title: str
    artists: list[str]

    def __post_init__(self):
        if self.index in ((2000, 97), (2001, 10)):
            self.title = self.title.replace("Part I", "Pt. 1")
        if self.index == (2001, 28):
            self.title = self.title.replace("U", "You")
        if self.index == (2001, 54):
            self.artists = [" and ".join(self.artists)]
        if self.index == (2002, 13):
            self.title = "Ain't It Funny (feat. Ja Rule & Cadillac Tah) - Murder Remix"
        if self.index == (2002, 15):
            self.title = "I Need a Girl (Pt. 1) [feat. Usher & Loon]"
        if self.index == (2002, 18):
            self.title = 'I Need a Girl (Pt. 2) [feat. Loon, Ginuwine, Mario Winans]'
        if self.index == (2005, 33):
            self.title = 'Obsesion (No Es Amor) (feat. Baby Bash)'
        if self.index == (2006, 75):
            self.title = 'Deja Vu (feat. Jay-Z)'
        if self.index == (2007, 22):
            self.title = 'What Goes Around.../...Comes Around (Interlude)'
        if self.index == (2008, 38):
            self.title = 'Bust It Baby, Pt. 2 (feat. Ne-Yo)'
        if self.index == (2021, 28):
            self.title = 'DÁKITI'

    @property
    def index(self):
        return self.year, self.number

    @property
    def artist_query(self):
        return f"{self.artists[0]}"

    @property
    def track_query(self):
        return f"{self.title}"

    def spotify_search_string(self, use_first_artist: bool) -> str:
        return f"{self.track_query} {f'artist:{self.artist_query}' if use_first_artist else ''}"

    def is_spotify_track(self, track: Track) -> bool:
        if any(artist.lower() in {a.name.lower() for a in track.artists} for artist in self.artists):
            for left, right in itertools.permutations((self.title.lower(), track.name.lower())):
                if left in right:
                    return True
                # Remove quotes, brackets, hyphen,
                for character in ('“', '”', '"', "‘", "’", "'", "(", "[", "{", ")", "]", "}", "-", ".", ",", "!", "?"):
                    left, right = left.replace(character, ""), right.replace(character, "")
                # Remove any double spaces created by removing characters
                left, right = left.replace("  ", " "), right.replace("  ", " ")
                if left in right:
                    return True
                if left.replace(" ", "") == right.replace(" ", ""):
                    return True
                for word, censor in (
                ("fuck", "f**k"), ("niggas", "ni**as"), ("pussy", 'p*$$y'), ("&", "and"), ("Shit", "S**t")):
                    if left.replace(word, censor) in right:
                        return True
        return False

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
