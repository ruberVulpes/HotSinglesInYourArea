from dependencies.spotify.models import SpotifyBaseModel


class Artist(SpotifyBaseModel):
    pass

    def __str__(self):
        name = self.name
        return f"{self.__class__.__name__}({name=})"
