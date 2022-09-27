"""This file contains all functions for the Dynamic url detection (DUDe) step."""
from typing import List, Tuple, Dict, Set

from orphan_detection import constants
from orphan_detection import util


HTTP_SCHEMA = "http://"
HTTPS_SCHEMA = "https://"

DudeReturnType = Tuple[List[str], List[str], List[str]]


def dynamic_url_detection(domain: str, dude_params: util.DUDEParameters) -> int:
    """
    Filter out urls with generated prefixes in their urls.
    :param domain: domain to identify orphan pages for
    :param dude_params: parameters for the dude step
    :return: amount of remaining candidates
    """
    candidates_path = constants.CANDIDATES_TO_PROBE_LIST_NAME_TEMPLATE.format(DOMAIN=domain)
    candidates = util.read_lines_from_file(candidates_path)

    # start dude process
    orphan_candidates, excluded_candidates, identified_prefixes = dude_main(candidates, domain, dude_params)

    orphan_candidates.sort()
    excluded_candidates.sort()
    identified_prefixes.sort()

    # output results
    excluded_path = constants.DUDE_EXCLUDED_LIST_NAME_TEMPLATE.format(DOMAIN=domain)
    prefixes_path = constants.DUDE_EXCLUDED_PREFIXES_NAME_TEMPLATE.format(DOMAIN=domain)

    util.write_lines_to_file(candidates_path, orphan_candidates)
    util.write_lines_to_file(excluded_path, excluded_candidates)
    util.write_lines_to_file(prefixes_path, identified_prefixes)

    return len(orphan_candidates)


def remove_schema(url_list: List[str]) -> Tuple[set[str], dict[str, list[str]]]:
    """
    Cutoff HTTP & HTTPS schemas and provide back transformation lookup
    :param url_list: list of all urls with schemes
    :return: tuple of set of urls without schemes and back transformation lookup
    """
    back_transformation_lookup = {}
    cleaned_urls = set()
    for url in url_list:
        # identify sschema
        if url.startswith(HTTPS_SCHEMA):
            schema = HTTPS_SCHEMA
            short_url = url[len(HTTPS_SCHEMA):]
        elif url.startswith(HTTP_SCHEMA):
            schema = HTTP_SCHEMA
            short_url = url[len(HTTP_SCHEMA):]
        else:
            schema = ""
            short_url = url
        # store url without schema
        cleaned_urls.add(short_url)

        # store schema for back transformation
        if short_url in back_transformation_lookup:
            back_transformation_lookup[short_url].append(schema)
        else:
            back_transformation_lookup[short_url] = [schema]
    return cleaned_urls, back_transformation_lookup


def transform_short_urls_back(url_list: List[str], transformation_lookup: Dict[str, List[str]]) -> List[str]:
    """
    Transform cleaned urls back through adding their schemes again.
    :param url_list: list of cleaned urls
    :param transformation_lookup: back transformation lookup with mapping of cleaned urls to schemes
    :return: list of back transformed urls
    """
    transformed_list = []
    for short_url in url_list:
        for schema in transformation_lookup[short_url]:
            transformed_list.append(f"{schema}{short_url}")
    return transformed_list


def identify_subdomains(url_list: List[str], domain: str) -> Dict[str, List[str]]:
    """
    Identify all subdomains in the candidate urls and group the urls together by their subdomain.
    :param url_list: list with all urls
    :param domain: domain to identify orphan pages for
    :return: mapping of subdomains to their urls
    """
    domain_lookup = {}
    for url in url_list:
        index_domain_begin = url.find(domain)
        sub_domain = url[:index_domain_begin + len(domain)]
        if sub_domain in domain_lookup:
            domain_lookup[sub_domain].append(url)
        else:
            domain_lookup[sub_domain] = [url]
    return domain_lookup


def dude_main(url_list: List[str], domain: str, dude_params: util.DUDEParameters) -> DudeReturnType:
    """
    Transform urls, execute DUDe per subdomain and back transform results.
    :param url_list: list with candidate urls
    :param domain: domain to identify orphan pages for
    :param dude_params: parameters for dude process
    :return: tuple of candidate list, excluded urls list and list of identified prefixes
    """
    # clen urls and identify subdomains
    url_list, back_transformation_lookup = remove_schema(url_list)
    subdomain_lookup = identify_subdomains(list(url_list), domain)
    orphans, excluded, prefixes = [], [], []

    for subdomain, subdomain_urls in subdomain_lookup.items():
        if len(subdomain_urls) < dude_params.subdomain_threshold:  # skip subdomains with very small amount of urls
            orphans += subdomain_urls
            continue

        pc_cutoff_value = len(subdomain_urls) * dude_params.popularity_cutoff
        orphans_subdomain, excluded_subdomain, prefixes_subdomain =\
            dude_subdomain(set(subdomain_urls), subdomain, dude_params, pc_cutoff_value)

        orphans += orphans_subdomain
        excluded += excluded_subdomain
        prefixes += prefixes_subdomain

    # transform cleaned urls back
    orphans_with_schema = transform_short_urls_back(orphans, back_transformation_lookup)
    excluded_with_schema = transform_short_urls_back(excluded, back_transformation_lookup)
    return orphans_with_schema, excluded_with_schema, prefixes


def dude_subdomain(url_list: Set[str], domain: str, dude_params: util.DUDEParameters,
                   cutoff_value: float, prev_prefix: str = "") -> DudeReturnType:
    """
    Execute DUDe.
    :param url_list: list with urls for subdomain
    :param domain: domain to identify orphan pages for
    :param dude_params: parameters for dude step
    :param cutoff_value: popularity cutoff value for subdomain
    :param prev_prefix: prefix of previous iteration
    :return: tuple of candidate list, excluded urls list and list of identified prefixes
    """
    orphans = []
    excluded = []
    identified_prefixes = []
    candidates = url_list

    while True:
        if len(candidates) < cutoff_value:  # too less candidates to fulfill pc condition
            orphans += list(candidates)
            break

        # find prefix
        prefix, c_with_prefix, c_without_prefix = execute_dude_step(candidates, len(domain), cutoff_value,
                                                                    dude_params.large_link_len_threshold,
                                                                    dude_params.large_link_count)

        if prefix is None or prefix == prev_prefix:  # stop if new prefix equals prev prefix or no prefix can be found
            orphans += list(candidates)
            break

        if len(prefix) < len(domain) + dude_params.short_prefix_cutoff:
            # in case of to short prefix repeat dude on urls matching the short prefix
            orp_part, exc_part, prefixes_part = dude_subdomain(c_with_prefix, domain, dude_params, cutoff_value, prefix)

            orphans += orp_part
            excluded += exc_part
            identified_prefixes += prefixes_part
            # continue with dude on urls not matching the short prefix
            candidates = c_without_prefix

        else:
            # remove urls matching the prefix
            identified_prefixes.append(prefix)
            excluded += list(c_with_prefix)

            # continue with dude on urls not matching the short prefix
            candidates = c_without_prefix

    return orphans, excluded, identified_prefixes


def execute_dude_step(url_list: Set[str], domain_len: int, popularity_cutoff: float,
                      large_link_len_threshold: int, large_link_count: int) -> Tuple[str | None, Set[str], Set[str]]:
    """
    Execute one dude step to identify one prefix and the urls matching it.
    :param url_list: list of candidate urls
    :param domain_len: len of base domain
    :param popularity_cutoff: popularity cutoff value
    :param large_link_len_threshold: large_link_len_threshold
    :param large_link_count: large_link_count
    :return: Tuple of prefix, list with candidates matching the prefix and list with candidates not matching the prefix
    """
    # filter large links
    large_urls = [url for url in url_list if len(url) > large_link_len_threshold + domain_len]
    if len(large_urls) <= large_link_count:
        return None, url_list, set()

    avg_len, max_len = get_average_and_max_len(url_list)
    counters = count_characters_per_position(large_urls, max_len)
    prefix = generate_prefix(counters, avg_len)
    return shorten_prefix(prefix, url_list, popularity_cutoff)


def get_average_and_max_len(url_list: Set[str]) -> Tuple[int, int]:
    """
    Calculate average and max length of all urls.
    :param url_list: list with all urls
    :return:  average len, max len
    """
    url_lengths = [len(url) for url in url_list]
    avg_len = sum(url_lengths) // len(url_list)
    max_len = max(url_lengths)
    return avg_len, max_len


def count_characters_per_position(url_list: List[str], max_len: int) -> List[Dict[str, int]]:
    """
    Count characters at each position for all urls.
    :param url_list: list with all urls
    :param max_len: len of the longest url
    :return: all character counters for each position in the urls
    """
    counters = [{} for _ in range(max_len)]
    for url in url_list:
        for position, character in enumerate(url):
            if character in counters[position]:
                counters[position][character] += 1
            else:
                counters[position][character] = 1
    return counters


def generate_prefix(counters: List[Dict[str, int]], avg_len: int) -> str:
    """
    Generate the prefix from most occurring characters for each position.
    :param counters: all character counters for each position in the urls
    :param avg_len: average len of all urls
    :return: generated prefix
    """
    generated_prefix = ""
    for i in range(0, avg_len):
        generated_prefix += max(counters[i], key=counters[i].get)
    return generated_prefix


def shorten_prefix(prefix: str, url_list: Set[str], pc_cutoff_value: float) -> Tuple[str, Set[str], Set[str]]:
    """
    Shorten generated prefix until enough urls are matching the prefix
    :param prefix: generated prefix
    :param url_list: list with all urls
    :param pc_cutoff_value: popularity cutoff value
    :return: Tuple of prefix, list with candidates matching the prefix and list with candidates not matching the prefix
    """
    while True:
        candidates_with_prefix = {url for url in url_list if prefix in url}
        candidates_without_prefix = url_list - candidates_with_prefix

        if len(candidates_with_prefix) >= pc_cutoff_value or len(candidates_with_prefix) == len(url_list):
            return prefix, candidates_with_prefix, candidates_without_prefix
        prefix = prefix[:-1]
