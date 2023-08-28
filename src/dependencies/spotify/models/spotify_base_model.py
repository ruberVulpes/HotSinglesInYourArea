from pydantic import BaseModel

from dependencies.spotify.models import Type


class SpotifyBaseModel(BaseModel):
    id: str
    uri: str
    type: Type
    name: str
    href: str
    external_urls: dict

    def __repr__(self):
        return self.__str__()
