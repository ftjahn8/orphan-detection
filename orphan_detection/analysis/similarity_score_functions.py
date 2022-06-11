from typing import List

from orphan_detection import constants
from orphan_detection import util

__all__ = ["calculate_similarity_score"]


def calculate_similarity_score(current_page_content: bytes, past_page_content: bytes) -> float:
    cleaned_current_page = util.remove_html_tags(current_page_content)
    cleaned_past_page = util.remove_html_tags(past_page_content)

    current_words = util.identify_words(cleaned_current_page)
    past_words = util.identify_words(cleaned_past_page)

    current_fingerprint = calculate_finger_print(current_words)
    past_fingerprint = calculate_finger_print(past_words)

    differences = [1 for k in range(len(current_fingerprint)) if current_fingerprint[k] != past_fingerprint[k]]
    return 1 - (sum(differences) / len(current_fingerprint))


def get_ngrams(word_list: List[str], n: int = constants.DEFAULT_NGRAM_SIZE) -> List[List[str]]:
    # pylint: disable=invalid-name
    ngrams = []
    for i in range(len(word_list) - n + 1):
        ngrams.append(word_list[i:i + n])
    return ngrams


def calculate_finger_print(word_list: List[str]) -> list[int]:
    fingerprint = [0 for _ in range(constants.DEFAULT_FINGERPRINT_SIZE)]
    ngram_list = get_ngrams(word_list, constants.DEFAULT_NGRAM_SIZE)

    hashed_ngrams = []
    for ngram in ngram_list:
        combined_ngram = ''.join(ngram)
        hashed_ngram = util.fnv_1a_64(combined_ngram.encode(constants.DEFAULT_ENCODING))
        hashed_ngrams.append(hashed_ngram)

    for hash_gram in hashed_ngrams:
        binary = bin(hash_gram)  # Convert text to binary
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
