import datetime
import itertools
from concurrent.futures import ThreadPoolExecutor

import cachetools
import requests
from bs4 import BeautifulSoup
from cachetools import LRUCache
from shelved_cache import PersistentCache

from dependencies.wikipedia.models import Single


def get_billboard_hot_singles_for_year(year: int) -> list[Single]:
    assert 1946 <= year < datetime.datetime.today().year, f"Year {year} out of range"
    page = requests.get(f"https://en.wikipedia.org/wiki/Billboard_Year-End_Hot_100_singles_of_{year}")
    soup = BeautifulSoup(page.content, "html.parser")
    # Throw away header row
    table_data = soup.find("table", {"class": "wikitable sortable"}).find("tbody").find_all("tr")[1:]
    assert len(table_data) == 100
    return [Single.from_bs4(row, year) for row in table_data]


def get_billboard_hot_singles(start_year: int, end_year: int) -> list[Single]:
    assert 1946 <= start_year, f"Start Year {start_year} out of range"
    assert end_year < datetime.datetime.today().year, f"End Year {end_year} out of range"
    with ThreadPoolExecutor() as executor:
        futures = executor.map(get_billboard_hot_singles_for_year, range(start_year, end_year + 1))
        return list(itertools.chain.from_iterable(futures))
