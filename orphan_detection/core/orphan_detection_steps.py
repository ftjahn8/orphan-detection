"""This file contains all function steps to detect orphan pages for a single domain
except the ones for the dynamic url detection step"""
import datetime
import time

from tqdm import tqdm

from orphan_detection import constants
from orphan_detection import util


def initialize_data_directory(domain: str) -> None:
    """Create all output directories"""
    # create static directories
    util.create_directory(constants.DATA_DIRECTORY)
    util.create_directory(constants.ARCHIVE_DATA_DIRECTORY)
    util.create_directory(constants.RESULT_DIRECTORY)
    util.create_directory(constants.TMP_DIRECTORY)
    util.create_directory(constants.PAGES_TMP_DIRECTORY)

    # create domain specific directories
    util.create_directory(constants.DOMAIN_DIRECTORY.format(DOMAIN=domain))
    util.create_directory(constants.DOMAIN_TMP_DIRECTORY.format(DOMAIN=domain))


def download_web_archive_data(searched_domain: str) -> str:
    """Download the web archive data for given domain"""
    # retrieve data from web archiv
    response = util.download_page_content(constants.WEB_ARCHIV_BASE_URL.format(DOMAIN=searched_domain),
                                          bytes_content=False)
    if response.error_msg is not None:
        print(f"Failed to download Data from Webarchive for domain {searched_domain}.")
        return ""

    # zip results and save in archive directory
    date = util.get_date()
    zipped_archive_file = constants.ZIPPED_ARCHIVE_NAME_TEMPLATE.format(DOMAIN=searched_domain, DATE=date)

    response_data = response.content.splitlines()
    util.write_lines_to_file(zipped_archive_file, response_data, zipped_file=True)
    return zipped_archive_file


def get_orphan_candidates(zipped_archive_file: str, current_sitemap_filter: datetime.date, domain: str) -> int:
    """
    Identify potential orphans not being part of the sitemap after the current_sitemap_filter date.
    :param zipped_archive_file: path to the file with the web archive data
    :param current_sitemap_filter: date to separate orphan candidates from pages being part of the current sitemap
    :param domain: domain to identify orphan pages for
    :return: amount of orphan candidates
    """
    url_list_web_archive = util.read_lines_from_file(zipped_archive_file, zipped_file=True)

    current_unique_url_set = set()
    total_unique_url_set = set()

    for web_archive_line in url_list_web_archive:
        # separate line into timestamp and url
        timestamp, url = web_archive_line.split(" ")[:2]
        timestamp_date = datetime.datetime.strptime(timestamp, '%Y%m%d%H%M%S').date()

        # add urls with an index date after the current sitemap filter date to the current urls set
        if timestamp_date >= current_sitemap_filter:
            current_unique_url_set.add(url)

        total_unique_url_set.add(url)

    # identify missing urls
    orphan_candidates_url_set = total_unique_url_set - current_unique_url_set

    # sort entries
    current_unique_url_sorted = list(current_unique_url_set)
    total_unique_url_sorted = list(total_unique_url_set)
    orphan_candidates_url_sorted = list(orphan_candidates_url_set)

    current_unique_url_sorted.sort()
    total_unique_url_sorted.sort()
    orphan_candidates_url_sorted.sort()

    # save as tmp results
    current_file_path = constants.CURRENT_UNIQUE_URL_NAME_TEMPLATE.format(DOMAIN=domain, FILTER=current_sitemap_filter)
    total_file_path = constants.TOTAL_UNIQUE_URL_NAME_TEMPLATE.format(DOMAIN=domain)
    orphan_candidates_file_path = constants.CANDIDATES_LIST_NAME_TEMPLATE.format(DOMAIN=domain)

    util.write_lines_to_file(current_file_path, current_unique_url_sorted)
    util.write_lines_to_file(total_file_path, total_unique_url_sorted)
    util.write_lines_to_file(orphan_candidates_file_path, orphan_candidates_url_sorted)
    return len(orphan_candidates_url_set)


def filter_file_extensions(domain: str) -> int:
    """
    Filter out all candidate urls identified as leading to a ressource file.
    :param domain: domain to identify orphan pages for
    :return: amount of remaining candidates
    """
    orphan_candidates_file_path = constants.CANDIDATES_LIST_NAME_TEMPLATE.format(DOMAIN=domain)
    candidates_unfiltered = util.read_lines_from_file(orphan_candidates_file_path)

    candidates_filtered = []
    for url in candidates_unfiltered:
        if not util.is_resource_url(url):
            candidates_filtered.append(url)

    candidates_filtered_file_path = constants.CANDIDATES_FILTERED_LIST_NAME_TEMPLATE.format(DOMAIN=domain)
    util.write_lines_to_file(candidates_filtered_file_path, candidates_filtered)

    candidates_to_probe_path = constants.CANDIDATES_TO_PROBE_LIST_NAME_TEMPLATE.format(DOMAIN=domain)
    util.write_lines_to_file(candidates_to_probe_path, candidates_filtered)
    return len(candidates_filtered)


def check_status_codes(domain: str, probe_args: util.ProbeParameters) -> int:
    """
    Probe all candidates and filter out all urls with a response != 200.
    :param domain: domain to identify orphan pages for
    :param probe_args: parameters for probe
    :return: amount of candidates left
    """
    probe_candidates_path = constants.CANDIDATES_TO_PROBE_LIST_NAME_TEMPLATE.format(DOMAIN=domain)
    probe_candidates = util.read_lines_from_file(probe_candidates_path)

    potential_orphans = []
    all_status_codes = {}
    error_responses = {}

    # shuffle candidates before probe
    probe_candidates_shuffled = probe_candidates.copy()
    probe_candidates_shuffled = util.shuffle_candidates_list(probe_candidates_shuffled)

    for url in tqdm(probe_candidates_shuffled):
        # probe url
        status_code, error_msg = util.probe_url(url, timeout_after=probe_args.timeout)

        # analyse response code
        if status_code == 200:
            potential_orphans.append(url)

        if error_msg is not None:
            error_responses[url] = f"{error_msg:25s} {url}"

        all_status_codes[url] = f"{status_code:03} {url}"
        time.sleep(probe_args.interval)

    # sort results
    potential_orphans.sort()
    all_status_codes_sorted = [all_status_codes[url] for url in probe_candidates]
    error_responses_sorted = [error_responses[url] for url in probe_candidates if url in error_responses]

    # save results
    potential_orphans_path = constants.POTENTIAL_ORPHAN_LIST_NAME_TEMPLATE.format(DOMAIN=domain)
    util.write_lines_to_file(potential_orphans_path, potential_orphans)

    status_code_list_path = constants.STATUS_CODES_LIST_NAME_TEMPLATE.format(DOMAIN=domain)
    util.write_lines_to_file(status_code_list_path, all_status_codes_sorted)

    error_responses_path = constants.ERROR_RESPONSES_LIST_NAME_TEMPLATE.format(DOMAIN=domain)
    util.write_lines_to_file(error_responses_path, error_responses_sorted)

    return len(potential_orphans)
