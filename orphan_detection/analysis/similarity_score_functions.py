"""This file contains all functions to calculate the similarity score for the fingerprint step in the analysis chain."""
from typing import List

from orphan_detection import constants
from orphan_detection import util

__all__ = ["calculate_similarity_score"]


def calculate_similarity_score(current_page_content: bytes, past_page_content: bytes) -> float:
    """
    Calculates the similarity score from the content of a page in its current and last seen state.
    :param current_page_content: content of the page in its current form
    :param past_page_content: content of the page in its last seen form
    :return: similarity score value
    """
    cleaned_current_page = util.remove_html_tags(current_page_content)
    cleaned_past_page = util.remove_html_tags(past_page_content)

    # identify words
    current_words = util.identify_words(cleaned_current_page)
    past_words = util.identify_words(cleaned_past_page)

    # calculate fingerprints for both page forms
    current_fingerprint = calculate_finger_print(current_words)
    past_fingerprint = calculate_finger_print(past_words)

    # calculate hammer distance and similarity scores from fingerprints
    differences = [1 for k in range(len(current_fingerprint)) if current_fingerprint[k] != past_fingerprint[k]]
    return 1 - (sum(differences) / len(current_fingerprint))


def get_ngrams(word_list: List[str], n: int = constants.DEFAULT_NGRAM_SIZE) -> List[List[str]]:
    """
    Create all possible ngrams for the word list of a single page.
    :param word_list: list of words of a single page
    :param n: size of ngrams
    :return: List of ngrams
    """
    # pylint: disable=invalid-name
    ngrams = []
    for i in range(len(word_list) - n + 1):
        ngrams.append(word_list[i:i + n])
    return ngrams


def calculate_finger_print(word_list: List[str]) -> list[int]:
    """
    Calculates the fingerprint from the word list of a page.
    :param word_list: list of words of the page
    :return: fingerprint for page
    """
    # prepare fingerprint
    fingerprint = [0 for _ in range(constants.DEFAULT_FINGERPRINT_SIZE)]

    # calculate ngrams from word list
    ngram_list = get_ngrams(word_list, constants.DEFAULT_NGRAM_SIZE)

    # calculate all fnv 1a hashes for ngrams
    hashed_ngrams = []
    for ngram in ngram_list:
        combined_ngram = ''.join(ngram)
        hashed_ngram = util.fnv_1a_64(combined_ngram.encode(constants.DEFAULT_ENCODING))
        hashed_ngrams.append(hashed_ngram)

    # calculate fingerprint from hashed ngram
    for hash_gram in hashed_ngrams:
        binary = bin(hash_gram)  # Convert int to binary
        bin_len = len(binary) - 2
        # Add the missing leading 0's to make all hashes 64 bit
        bin_str = "0" * (constants.DEFAULT_FINGERPRINT_SIZE - bin_len) + binary[2:]

        for i in range(constants.DEFAULT_FINGERPRINT_SIZE):
            if bin_str[i] == '1':
                fingerprint[i] += 1
            else:
                fingerprint[i] -= 1

    for i in range(constants.DEFAULT_FINGERPRINT_SIZE):
        fingerprint[i] = 1 if fingerprint[i] > 0 else 0
    return fingerprint
