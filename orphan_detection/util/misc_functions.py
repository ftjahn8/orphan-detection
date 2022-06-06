import hashlib
import re
import random
from typing import List

from orphan_detection import constants

__all__ = ["fnv_1a_64", "get_md5_hash", "is_resource_url", "shuffle_candidates_list"]

FNV_1A_INIT_VALUE = 0xcbf29ce484222325
FNV_1A_PRIME = 0x100000001b3


def fnv_1a_64(data: bytes) -> int:
    hash_value = FNV_1A_INIT_VALUE
    for byte in data:
        hash_value = hash_value ^ byte
        hash_value = (hash_value * FNV_1A_PRIME) % 2**64
    return hash_value


def get_md5_hash(text: str) -> str:
    return hashlib.md5(text.encode(constants.DEFAULT_ENCODING)).hexdigest()


def is_resource_url(url: str) -> bool:
    filter_regex = re.compile(constants.FILTER_REGEX, re.IGNORECASE)
    return filter_regex.match(url) is not None


def shuffle_candidates_list(candidates_list: List[str]) -> List[str]:
    random.shuffle(candidates_list)
    return candidates_list
