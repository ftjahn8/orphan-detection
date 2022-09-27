"""This file contains some helper functions."""
import hashlib
import re
import random
from typing import List

from orphan_detection import constants

__all__ = ["fnv_1a_64", "get_md5_hash", "is_resource_url", "shuffle_candidates_list"]

# FNV-1A Initialization Values
FNV_1A_INIT_VALUE = 0xcbf29ce484222325
FNV_1A_PRIME = 0x100000001b3


def fnv_1a_64(data: bytes) -> int:
    """Calculates and returns the FNV-1A 64-bit hash for given data."""
    hash_value = FNV_1A_INIT_VALUE
    for byte in data:
        hash_value = hash_value ^ byte
        hash_value = (hash_value * FNV_1A_PRIME) % 2**64
    return hash_value


def get_md5_hash(text: str) -> str:
    """Returns the MD-5 Hash of given text."""
    return hashlib.md5(text.encode(constants.DEFAULT_ENCODING)).hexdigest()


def is_resource_url(url: str) -> bool:
    """Returns True if given url is identified as leading to a ressource like an image etc. Otherwise, returns False."""
    filter_regex = re.compile(constants.FILTER_REGEX, re.IGNORECASE)
    return filter_regex.match(url) is not None


def shuffle_candidates_list(candidates_list: List[str]) -> List[str]:
    """Shuffles the list of candidate urls and returns it."""
    random.shuffle(candidates_list)
    return candidates_list
