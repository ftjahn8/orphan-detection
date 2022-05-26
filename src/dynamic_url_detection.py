from typing import List, Tuple, Dict, Set

import util
import constants


def dynamic_url_detection(domain: str, popularity_cutoff: float, short_prefix_cutoff: int,
                          large_link_len_threshold: int, large_link_count: int) -> int:

    candidates_path = constants.CANDIDATES_TO_PROBE_LIST_NAME_TEMPLATE.format(DOMAIN=domain)
    candidates = util.read_lines_from_file(candidates_path)

    orphan_candidates, excluded_candidates = execute_dude_process(candidates, len(domain), popularity_cutoff,
                                                                  short_prefix_cutoff, large_link_len_threshold, large_link_count)

    orphan_candidates = list(excluded_candidates)
    excluded_candidates = list(excluded_candidates)
    orphan_candidates.sort()
    excluded_candidates.sort()
    excluded_path = constants.DUDE_EXCLUDED_LIST_NAME_TEMPLATE.format(DOMAIN=domain)
    util.write_lines_to_file(candidates_path, orphan_candidates)
    util.write_lines_to_file(excluded_path, excluded_candidates)
    return len(orphan_candidates)


def execute_dude_process(url_list: List[str], domain_len: int,
                         popularity_cutoff: float, short_prefix_cutoff: int,
                         large_link_len_threshold: int, large_link_count: int):

    blocklist = set()
    candidates = set(url_list)
    while True:
        prefix, c_with_prefix, c_without_prefix = execute_dude_step(candidates, domain_len, popularity_cutoff,
                                                                    large_link_len_threshold, large_link_count)

        print(prefix, len(c_with_prefix), len(c_without_prefix))
        if prefix is None:
            break

        if len(prefix) < domain_len + 8 + short_prefix_cutoff:
            candidates = c_without_prefix
        else:
            blocklist.union(c_with_prefix)
            candidates = c_without_prefix

    return candidates, blocklist

    
def execute_dude_step(url_list: Set[str], domain_len: int, popularity_cutoff: float,
                      large_link_len_threshold: int, large_link_count: int) -> Tuple[str | None, Set[str], Set[str]]:

    # filter large links
    large_urls = [url for url in url_list if len(url) > large_link_len_threshold + domain_len + 8]
    if len(large_urls) <= large_link_count:
        return None, url_list, set()

    avg_len, max_len = get_average_and_max_len(url_list)
    counters = count_characters_per_position(large_urls, max_len)
    prefix = generate_prefix(counters, avg_len)
    print(prefix)
    return shorten_prefix(prefix, url_list, popularity_cutoff)


def get_average_and_max_len(url_list: Set[str]) -> Tuple[int, int]:
    url_lengths = [len(url) for url in url_list]
    avg_len = sum(url_lengths) // len(url_list)
    max_len = max(url_lengths)
    return avg_len, max_len


def count_characters_per_position(url_list: List[str], max_len: int) -> List[Dict[str, int]]:
    counters = [{} for _ in range(max_len)]
    for url in url_list:
        for position, character in enumerate(url):
            if character in counters[position]:
                counters[position][character] += 1
            else:
                counters[position][character] = 1
    return counters


def generate_prefix(counters: List[Dict[str, int]], avg_len: int) -> str:
    generated_prefix = ""
    for i in range(0, avg_len):
        generated_prefix += max(counters[i], key=counters[i].get)
    return generated_prefix


def shorten_prefix(prefix: str, url_list: Set[str], popularity_cutoff: float) -> Tuple[str, Set[str], Set[str]]:
    cutoff_value = len(url_list) * popularity_cutoff

    while True:
        candidates_with_prefix = {url for url in url_list if prefix in url}
        candidates_without_prefix = url_list - candidates_with_prefix

        if len(candidates_with_prefix) >= cutoff_value or len(candidates_with_prefix) == len(url_list):
            return prefix, candidates_with_prefix, candidates_without_prefix

        prefix = prefix[:-1]
