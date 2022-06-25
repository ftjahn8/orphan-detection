import json
import re
from typing import List

import bs4

from orphan_detection import constants

__all__ = ["identify_words", "identify_numbers", "remove_html_tags", "get_content_without_tags", "guess_encoding"]


def identify_words(text: str) -> List[str]:
    return re.findall(r"[\w']+", text.lower())


def identify_numbers(text: str) -> List[str]:
    return re.findall(r'\d+', text.lower())


def remove_html_tags(page_content: bytes | str) -> str:
    return bs4.BeautifulSoup(page_content, constants.HTML_PARSER_CONFIG).get_text()


def get_content_without_tags(page_content: bytes | str, tags: List[str]) -> str:
    soup = bs4.BeautifulSoup(page_content, constants.HTML_PARSER_CONFIG)
    for tag in tags:
        for tag_part in soup.select(tag):
            tag_part.extract()
    return soup.get_text()


def guess_encoding(text: bytes) -> str:
    return json.detect_encoding(text)
