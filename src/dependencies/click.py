import click
from click import IntRange

valid_year_range: IntRange = click.IntRange(min=1946, max=2022)
