import time

from orphan_detection import util
from orphan_detection import constants
from orphan_detection.analysis.analysis_steps import retrieve_page_sizes, get_last_seen_date, get_current_page_content


def analysis(domain: str, download_date: str) -> int:
    orphan_candidates = util.read_lines_from_file("..\\Data\\Results\\hm.edu\\hm.edu_potential_orphans_2.txt")

    analysis_data = {}
    for candidate in orphan_candidates:
        analysis_data[candidate] = {"size": -1, "last_seen_date": None,
                                    "current_page_file": None, "last_seen_page_file": None}

    print(f"Checking last seen dates for {domain}.")
    start_time_step = time.time()
    oldest_page_year = get_last_seen_date(analysis_data, domain, download_date)
    end_time_step = time.time()
    print(f"Checking last seen dates for {domain} took {end_time_step - start_time_step:.2f} seconds.")

    print(f"Retrieving page content in current version for {domain}")
    start_time_step = time.time()
    candidates_left = get_current_page_content(analysis_data)
    end_time_step = time.time()
    print(f"Retrieving page content in current version for {domain} took {end_time_step - start_time_step:.2f} seconds"
          f" and left {candidates_left} candidates.")

    print(f"Filtering on page size for {domain}")
    start_time_step = time.time()
    retrieve_page_sizes(analysis_data)
    # removed_pages = a(analysis_data)
    end_time_step = time.time()
    #print(f"Filtering on page size for {domain} took {end_time_step - start_time_step:.2f} seconds"
    #      f" and removed {removed_pages} candidates.")
    print(analysis_data)



    return 0
