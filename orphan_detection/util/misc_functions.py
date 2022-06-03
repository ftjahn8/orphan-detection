import datetime
import re
import random
from typing import List

from orphan_detection import constants

__all__ = ["get_date", "parse_year_argument", "get_default_current_sitemap_filter",
           "is_ressource_url", "shuffle_candidates_list"]


# date related functions
def get_date() -> str:
    return datetime.datetime.today().strftime("%Y-%m-%d")


def parse_year_argument(arg_value: str) -> datetime.date | None:
    split_value = arg_value.split("-")
    match len(split_value):
        case 3:
            try:
                return datetime.date(int(split_value[0]), int(split_value[1]), int(split_value[2]))
            except ValueError:
                return None
        case 2:
            try:
                return datetime.date(int(split_value[0]), int(split_value[1]), 1)
            except ValueError:
                return None
        case 1:
            try:
                return datetime.date(int(split_value[0]), 1, 1)
            except ValueError:
                return None
    return None


def get_default_current_sitemap_filter() -> datetime.date:
    return datetime.date(datetime.date.today().year, 1, 1)


# misc functions
def is_ressource_url(url: str) -> bool:
    filter_regex = re.compile(constants.FILTER_REGEX, re.IGNORECASE)
    return filter_regex.match(url) is not None


def shuffle_candidates_list(candidates_list: List[str]) -> List[str]:
    random.shuffle(candidates_list)
    return candidates_list
