import time

from orphan_detection import util
from orphan_detection import constants
from orphan_detection.analysis.analysis_steps import check_needed_input_files, retrieve_page_sizes, \
    get_last_seen_date, get_current_page_content, filter_same_size, get_last_seen_page_content, \
    get_similarity_scores, filter_orphan_likelihood_score, check_orphan_status
from orphan_detection.core.orphan_detection_steps import initialize_data_directory


__all__ = ["analysis"]


def analysis(domain: str, download_date: str, current_download_params: util.ContentDownloadParameters,
             size_filter_params: util.SizeFilterParameters, last_seen_download_params: util.ContentDownloadParameters,
             orphan_score_params: util.OrphanScoreParameters) -> int:
    # create needed directories
    print(f"Creating data directory structure for {domain}.")
    initialize_data_directory(domain)
    print("Finished creating data directory structure.")

    check = check_needed_input_files(domain, download_date)
    if check != 0:
        return check

    orphan_candidates = util.read_lines_from_file(constants.POTENTIAL_ORPHAN_LIST_NAME_TEMPLATE.format(DOMAIN=domain))

    print(f"Starting with {len(orphan_candidates)} candidates.")
    analysis_data = {}
    for candidate in orphan_candidates:
        analysis_data[candidate] = {"size": -1, "last_seen_date": None, "similarity_score": -1, "orphan_score": -1,
                                    "current_page_file": None, "last_seen_page_file": None}

    print(f"Checking last seen dates for {domain}.")
    start_time_step = time.time()
    oldest_page_year = get_last_seen_date(analysis_data, domain, download_date)
    end_time_step = time.time()
    print(f"Checking last seen dates for {domain} took {end_time_step - start_time_step:.2f} seconds.")

    print(f"Retrieving page content in current version for {domain}")
    time.sleep(0.1)
    start_time_step = time.time()
    candidates_left = get_current_page_content(analysis_data, domain, current_download_params)
    end_time_step = time.time()
    time.sleep(0.1)
    print(f"Retrieving page content in current version for {domain} took {end_time_step - start_time_step:.2f} seconds"
          f" and left {candidates_left} candidates.")

    print(f"Filtering on page size for {domain}")
    start_time_step = time.time()
    retrieve_page_sizes(analysis_data, domain)
    candidates_left = filter_same_size(analysis_data, domain, size_filter_params)
    end_time_step = time.time()
    print(f"Filtering on page size for {domain} took {end_time_step - start_time_step:.2f} seconds"
          f" and left {candidates_left} candidates.")

    print(f"Retrieving page content in last seen version for {domain}")
    time.sleep(0.1)
    start_time_step = time.time()
    candidates_left = get_last_seen_page_content(analysis_data, domain, last_seen_download_params)
    end_time_step = time.time()
    time.sleep(0.1)
    print(f"Retrieving page content in last seen version for {domain} "
          f"took {end_time_step - start_time_step:.2f} seconds and left {candidates_left} candidates.")

    print(f"Retrieving similarity scores for {domain}")
    start_time_step = time.time()
    get_similarity_scores(analysis_data, domain)
    end_time_step = time.time()
    print(f"Retrieving similarity scores for {domain} took {end_time_step - start_time_step:.2f} seconds.")

    print(f"Retrieving orphan likelihood scores for {domain}")
    start_time_step = time.time()
    candidates_left = filter_orphan_likelihood_score(analysis_data, domain, oldest_page_year, orphan_score_params)
    end_time_step = time.time()
    print(f"Retrieving orphan likelihood scores for {domain} took {end_time_step - start_time_step:.2f} seconds "
          f"and left {candidates_left} candidates.")

    print(f"Checking orphan status for {domain}")
    start_time_step = time.time()
    candidates_left = check_orphan_status(analysis_data, domain)
    end_time_step = time.time()
    print(f"Checking orphan status for {domain} took {end_time_step - start_time_step:.2f} seconds "
          f"and identified {candidates_left} likely orphan pages.")

    util.delete_directory(constants.PAGES_TMP_DIRECTORY)
    return 0
