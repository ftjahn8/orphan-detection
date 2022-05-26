import datetime
import gzip
import os
import random
import re
from typing import List, Tuple

import requests

import constants


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


def create_directory(path: str) -> None:
    if not os.path.exists(path):
        os.mkdir(path)


def save_to_file(path: str, content: str, user_restricted: bool = True) -> None:
    with open(path, 'w', encoding="utf-8") as outfile:
        outfile.write(content)
    if user_restricted:
        os.chmod(path, constants.CHMOD_USER_ONLY_FILE)


def save_to_gzip_file(path: str, content: str, user_restricted: bool = True) -> None:
    with gzip.open(path, 'wb') as outfile:
        outfile.write(content.encode("utf-8"))

    if user_restricted:
        os.chmod(path, constants.CHMOD_USER_ONLY_FILE)


def read_from_file(path: str) -> str:
    with open(path, 'r', encoding="utf-8") as infile:
        content = infile.read()
    return content


def read_from_gzip_file(path: str) -> str:
    with gzip.open(path, 'rb') as infile:
        content = infile.read()
    return content.decode("utf-8")


def read_lines_from_file(path: str, zipped_file: bool = False) -> List[str]:
    if zipped_file:
        content = read_from_gzip_file(path)
    else:
        content = read_from_file(path)

    return content.splitlines()


def write_lines_to_file(path: str, content: List[str], zipped_file: bool = False, user_restricted: bool = True) -> None:
    content_combined = "\n".join(content)
    if zipped_file:
        save_to_gzip_file(path, content_combined, user_restricted)
    else:
        save_to_file(path, content_combined, user_restricted)


def is_ressource_url(url: str) -> bool:
    filter_regex = re.compile(constants.FILTER_REGEX, re.IGNORECASE)
    return filter_regex.match(url) is not None


def shuffle_candidates_list(candidates_list: List[str]) -> List[str]:
    random.shuffle(candidates_list)
    return candidates_list


def probe_url(url: str, timeout_after: float) -> Tuple[int, str | None]:
    try:
        response_for_url = requests.head(url, timeout=timeout_after)
        return response_for_url.status_code, None
    except requests.exceptions.Timeout:
        return 000, "Timeout"
    except requests.exceptions.SSLError as exc:
        return 000, f"[ERROR] SSLError: {exc}"
    except requests.exceptions.ConnectionError as exc:
        return 000, f"[ERROR] ConnectionError: {exc}"
    except Exception as exc:
        return 000, str(exc)
