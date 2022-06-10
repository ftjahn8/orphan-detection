import time
from typing import Dict

from tqdm import tqdm

from orphan_detection import util
from orphan_detection import constants

from orphan_detection.analysis.check_page import check_page
from orphan_detection.analysis.similarity_score_functions import calculate_similarity_score

ANALYSIS_DATA_TYPE = Dict[str, Dict[str, int | str | float]]


def check_needed_input_files(domain: str, download_date: str) -> int:
    orphan_candidate_file = constants.POTENTIAL_ORPHAN_LIST_NAME_TEMPLATE.format(DOMAIN=domain)
    if not util.is_file(orphan_candidate_file):
        print(f"[MISSING INPUT FILE] File {orphan_candidate_file} does not exist, but is needed for the analysis.")
        return 1

    zipped_archive_file = constants.ZIPPED_ARCHIVE_NAME_TEMPLATE.format(DOMAIN=domain, DATE=download_date)
    if not util.is_file(zipped_archive_file):
        print(f"[MISSING INPUT FILE] File {zipped_archive_file} does not exist, but is needed for the analysis.")
        return 1
    return 0


def get_last_seen_date(data: ANALYSIS_DATA_TYPE, domain: str, download_date: str) -> int:
    zipped_archive_file = constants.ZIPPED_ARCHIVE_NAME_TEMPLATE.format(DOMAIN=domain, DATE=download_date)
    url_list_web_archive = util.read_lines_from_file(zipped_archive_file, zipped_file=True)

    oldest_page_year = 9999

    last_seen_lookup = {}
    for line in url_list_web_archive:
        timestamp, url = line.split(" ")[:2]
        if url in last_seen_lookup:
            if int(timestamp) > last_seen_lookup[url]:
                last_seen_lookup[url] = int(timestamp)
        else:
            last_seen_lookup[url] = int(timestamp)

        oldest_page_year = min(int(timestamp[:4]), oldest_page_year)

    last_seen_output = []
    for candidate in data.keys():
        last_seen_date = last_seen_lookup[candidate]
        last_seen_output.append(f"{candidate} {last_seen_date}")
        data[candidate]["last_seen_date"] = last_seen_date

    util.write_lines_to_file(constants.LAST_SEEN_DATES_NAME_TEMPLATE.format(DOMAIN=domain), last_seen_output)
    return oldest_page_year


def download_page(file_name: str, url: str, **kwargs) -> str | None:
    page_response = util.download_page_content(url, bytes_content=True, **kwargs)
    if page_response.error_msg is not None:
        return f"[DOWNLOAD ERROR] {page_response.error_msg} {url}"
    content_type_header = page_response.content_header
    page_content = page_response.content

    if content_type_header is None or "text/html" not in content_type_header.lower():
        if content_type_header is None:
            content_type_header = ""
        return f"[NO HTML       ] {content_type_header:15s} {url}"

    if f"charset={constants.DEFAULT_ENCODING}" in content_type_header.lower():
        encoding_current = constants.DEFAULT_ENCODING
    elif "charset=" in content_type_header.lower():
        encoding_current = content_type_header.lower().split("charset=")[1]
    elif content_type_header is not None and page_response.encoding:
        encoding_current = page_response.encoding
    else:
        encoding_current = util.guess_encoding(page_content)

    if encoding_current != constants.DEFAULT_ENCODING:
        try:
            page_content = page_content.decode(encoding_current).encode(constants.DEFAULT_ENCODING)
        except LookupError:
            return f"[ENCODING ERROR] {encoding_current:15s} {url}"

    util.save_to_bin_file(constants.PAGES_CONTENT_NAME_TEMPLATE.format(FILE_NAME=file_name), page_content)


def get_current_page_content(data: ANALYSIS_DATA_TYPE, domain: str,
                             download_params: util.ContentDownloadParameters) -> int:
    no_html = []
    to_be_removed = []

    for candidate in tqdm(data.keys()):
        page_hashed_name = util.get_md5_hash(candidate)
        error = download_page(page_hashed_name, candidate, timeout=download_params.timeout)
        if error is not None:
            no_html.append(error)
            to_be_removed.append(candidate)
            continue
        data[candidate]["current_page_file"] = page_hashed_name
        time.sleep(download_params.interval)

    error_save_path = constants.DOWNLOAD_ERROR_C_NAME_TEMPLATE.format(DOMAIN=domain)
    util.write_lines_to_file(error_save_path, no_html)
    for url in to_be_removed:
        del data[url]

    return len(data)


def retrieve_page_sizes(data: ANALYSIS_DATA_TYPE, domain: str) -> None:
    output = []
    for candidate_url, candidate_data in data.items():
        file_current = constants.PAGES_CONTENT_NAME_TEMPLATE.format(FILE_NAME=candidate_data['current_page_file'])
        candidate_content = util.read_from_bin_file(file_current)
        page_size = len(candidate_content)
        data[candidate_url]["size"] = page_size
        output.append(f"{candidate_url} {page_size}")
    util.write_lines_to_file(constants.PAGE_SIZE_NAME_TEMPLATE.format(DOMAIN=domain), output)


def filter_same_size(data: ANALYSIS_DATA_TYPE, domain: str, size_filter_params: util.SizeFilterParameters) -> int:
    page_size_lookup = [(candidate_url, candidate_data["size"]) for candidate_url, candidate_data in data.items()]

    start_len = len(page_size_lookup)

    to_remove = []
    tmp_remove = []
    current_size = 0

    # Loop over entries, ordered by size
    for url, size in sorted(page_size_lookup, key=lambda x: x[1]):
        # If size is within reasonable similarity to previous size, add to discard list
        if size <= current_size + size_filter_params.epsilon:
            tmp_remove.append((url, size))
            current_size = size
            continue
        # Write out current discard list and continue procedure
        else:
            if len(tmp_remove) >= size_filter_params.min_amount_same_size:
                to_remove += tmp_remove
            tmp_remove = [(url, size)]
            current_size = size

    # Remove all entries that need to be discarded
    filtered = list(set(page_size_lookup) - set(to_remove))
    for url, _ in to_remove:
        del data[url]

    # Write out results
    output = [f"{url} {size}" for url, size in filtered]
    util.write_lines_to_file(constants.PAGE_SIZE_FILTERED_NAME_TEMPLATE.format(DOMAIN=domain), output)

    output_removed = [f"{url} {size}" for url, size in to_remove]
    util.write_lines_to_file(constants.PAGE_SIZE_REMOVED_NAME_TEMPLATE.format(DOMAIN=domain), output_removed)

    # Calculate the reduction percentage
    end_len = len(filtered)
    reduction = 100 - ((end_len / start_len) * 100)
    print("Reduction of {:.2f}%".format(reduction))
    return end_len


def get_last_seen_page_content(data: ANALYSIS_DATA_TYPE, domain: str,
                               download_params: util.ContentDownloadParameters) -> int:
    no_html = []
    to_be_removed = []

    for candidate in tqdm(data.keys()):
        last_seen_date = data[candidate]["last_seen_date"]
        page_hashed_name = util.get_md5_hash(f"{candidate}_{last_seen_date}")
        url_web_archive = constants.WEB_ARCHIV_LAST_SEEN_VERSION.format(LAST_SEEN_DATE=last_seen_date, URL=candidate)
        error = download_page(page_hashed_name, url_web_archive, timeout=download_params.timeout)
        if error is not None:
            no_html.append(error)
            to_be_removed.append(candidate)
            continue
        data[candidate]["last_seen_page_file"] = page_hashed_name
        time.sleep(download_params.interval)

    error_save_path = constants.DOWNLOAD_ERROR_LS_NAME_TEMPLATE.format(DOMAIN=domain)
    util.write_lines_to_file(error_save_path, no_html)
    for url in to_be_removed:
        del data[url]

    return len(data)


def get_similarity_scores(data: ANALYSIS_DATA_TYPE, domain: str) -> None:
    output = []
    for candidate_url, candidate_data in data.items():
        file_current = constants.PAGES_CONTENT_NAME_TEMPLATE.format(FILE_NAME=candidate_data['current_page_file'])
        file_last_seen = constants.PAGES_CONTENT_NAME_TEMPLATE.format(FILE_NAME=candidate_data['last_seen_page_file'])

        current_page_content = util.read_from_bin_file(file_current)
        last_seen_page_content = util.read_from_bin_file(file_last_seen)

        sim_score = calculate_similarity_score(current_page_content, last_seen_page_content)
        data[candidate_url]["similarity_score"] = sim_score
        output.append(f"{candidate_url} {sim_score}")
    util.write_lines_to_file(constants.SIMILARITY_SCORES_NAME_TEMPLATE.format(DOMAIN=domain), output)


def filter_orphan_likelihood_score(data: ANALYSIS_DATA_TYPE, domain: str, oldest_page_year: int,
                                   orphan_score_params: util.OrphanScoreParameters) -> int:
    current_year = util.get_current_year()
    max_scale = current_year - oldest_page_year

    orphan_scores = []
    orphan_scores_filtered = []
    to_be_removed = []

    for url, candidate_data in data.items():
        url_year = int(str(candidate_data["last_seen_date"])[:4])
        sim_score = candidate_data["similarity_score"]

        orphan_score = (max_scale * float(sim_score) * orphan_score_params.similarity_weight
                        + orphan_score_params.age_weight * (current_year - url_year)) / max_scale

        data[url]["orphan_score"] = orphan_score
        orphan_scores.append(f"{url} {orphan_score}")
        if orphan_score >= orphan_score_params.cutoff_value:
            orphan_scores_filtered.append(f"{url} {orphan_score}")
        else:
            to_be_removed.append(url)

    util.write_lines_to_file(constants.ORPHAN_SCORES_NAME_TEMPLATE.format(DOMAIN=domain), orphan_scores)
    util.write_lines_to_file(constants.ORPHAN_SCORES_FILTERED_NAME_TEMPLATE.format(DOMAIN=domain),
                             orphan_scores_filtered)

    for url in to_be_removed:
        del data[url]
    return len(data)


def check_orphan_status(data: ANALYSIS_DATA_TYPE, domain) -> None:
    result_translation = {0: "[UNDECIDED      ]", 1: "[LIKELY ORPHAN  ]", -1: "[UNLIKELY ORPHAN]"}
    results = []
    for candidate_url, candidate_data in data.items():
        content_file = constants.PAGES_CONTENT_NAME_TEMPLATE.format(FILE_NAME=candidate_data['current_page_file'])
        current_page_content = util.read_from_bin_file(content_file)
        result, msg = check_page(current_page_content, candidate_url)
        for single_message in msg:
            results.append(f"{result_translation[result]} {candidate_url} {single_message}")
    util.write_lines_to_file(constants.ANALYSIS_RESULT_FILE.format(DOMAIN=domain), results)
