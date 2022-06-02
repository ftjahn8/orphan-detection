from typing import List, Tuple, Dict, Set

import util
import constants


def dynamic_url_detection(domain: str, popularity_cutoff: float, short_prefix_cutoff: int, large_link_len_threshold: int, large_link_count: int) -> int:
    candidates_path = constants.CANDIDATES_TO_PROBE_LIST_NAME_TEMPLATE.format(DOMAIN=domain)
    candidates = util.read_lines_from_file(candidates_path)
    orphan_candidates, excluded_candidates = dude(candidates, domain)
    print(len(orphan_candidates), len(excluded_candidates))
    # orphan_candidates, excluded_candidates = execute_dude_process(candidates, len(domain), popularity_cutoff, short_prefix_cutoff, large_link_len_threshold, large_link_count)

    orphan_candidates = list(orphan_candidates)
    excluded_candidates = list(excluded_candidates)
    orphan_candidates.sort()
    excluded_candidates.sort()
    excluded_path = constants.DUDE_EXCLUDED_LIST_NAME_TEMPLATE.format(DOMAIN=domain)
    util.write_lines_to_file(candidates_path, orphan_candidates)
    util.write_lines_to_file(excluded_path, excluded_candidates)
    return len(orphan_candidates)


def remove_https_schema(url_list: List[str]) -> Tuple[List[str], Dict[str, str]]:
    back_lookup = {}
    cleaned_url_list = []
    for url in url_list:
        if url.startswith("https://"):
            short_url = url[len("https://"):]
            back_lookup[short_url] = "https://"
            cleaned_url_list.append(short_url)
        elif url.startswith("http://"):
            short_url = url[len("http://"):]
            back_lookup[short_url] = "http://"
            cleaned_url_list.append(short_url)
    return cleaned_url_list, back_lookup


def identify_subdomains(url_list: List[str], domain: str) -> Dict[str, List[str]]:
    domain_lookup = {}
    for url in url_list:
        index_domain_begin = url.find(domain)
        sub_domain = url[:index_domain_begin + len(domain)]
        if sub_domain in domain_lookup:
            domain_lookup[sub_domain].append(url)
        else:
            domain_lookup[sub_domain] = []

    return domain_lookup


def dude(url_list: List[str], domain: str) -> Tuple[List[str], List[str]]:
    url_list, back_lookup = remove_https_schema(url_list)
    subdomain_lookup = identify_subdomains(url_list, domain)
    orphans, excluded = [], []

    for subdomain, subdomain_urls in subdomain_lookup.items():
        print("===================", subdomain)
        orphans_a, excluded_a = dude_exp(subdomain_urls, subdomain, len(subdomain_urls) * 0.05)
        orphans += orphans_a
        excluded += excluded_a
    return orphans, excluded


def dude_exp(url_list: List[str], domain: str, cutoff: float, prev_prefix="", ) -> Tuple[List[str], List[str]]:
    orphans = []
    excluded = []
    candidates = set(url_list)

    while True:
        if len(candidates) < cutoff:
            orphans += list(candidates)
            break
        prefix, c_with_prefix, c_without_prefix = execute_dude_step(candidates, len(domain), cutoff, 20, 0)

        if prefix is None or prefix == prev_prefix:
            print("===", prev_prefix)
            orphans += list(candidates)
            break

        if len(prefix) < len(domain) + 15:
            orp, exc = dude_exp(list(c_with_prefix), domain, cutoff, prefix)
            orphans += orp
            exc += exc
            candidates = c_without_prefix

        else:
            print("===", prefix)
            excluded += list(c_with_prefix)
            candidates = c_without_prefix

    return orphans, excluded



def execute_dude_process(url_list: List[str], domain_len: int, popularity_cutoff: float, short_prefix_cutoff: int, large_link_len_threshold: int, large_link_count: int):
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
    large_urls = [url for url in url_list if len(url) > large_link_len_threshold + domain_len]
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
    # cutoff_value = len(url_list) * popularity_cutoff

    while True:
        candidates_with_prefix = {url for url in url_list if prefix in url}
        candidates_without_prefix = url_list - candidates_with_prefix

        if len(candidates_with_prefix) >= popularity_cutoff or len(candidates_with_prefix) == len(url_list):
            return prefix, candidates_with_prefix, candidates_without_prefix

        prefix = prefix[:-1]
