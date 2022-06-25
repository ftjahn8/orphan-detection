"""This file contains helper functions for text processing."""
import json
import re
from typing import List

import bs4

from orphan_detection import constants

__all__ = ["identify_words", "identify_numbers", "remove_html_tags", "get_content_without_tags", "guess_encoding"]


def identify_words(text: str) -> List[str]:
    """Identifies all words in a given text and returns a list with all of them."""
    return re.findall(r"[\w']+", text.lower())


def identify_numbers(text: str) -> List[str]:
    """Identifies all numbers in a given text and returns a list with all of them."""
    return re.findall(r'\d+', text.lower())


def remove_html_tags(page_content: bytes | str) -> str:
    """Removes all html tags from a given page and returns only its content."""
    return bs4.BeautifulSoup(page_content, constants.HTML_PARSER_CONFIG).get_text()


def get_content_without_tags(page_content: bytes | str, tags: List[str]) -> str:
    """Removes all sections from a given page for a list of unwanted tags and returns the content with any html tags."""
    soup = bs4.BeautifulSoup(page_content, constants.HTML_PARSER_CONFIG)
    for tag in tags:
        for tag_part in soup.select(tag):
            tag_part.extract()
    return soup.get_text()


def guess_encoding(text: bytes) -> str:
    """Guesses the file encoding based on its text-bytes form and returns it."""
    return json.detect_encoding(text)
