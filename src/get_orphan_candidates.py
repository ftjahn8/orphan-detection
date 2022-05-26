import datetime

import util
import constants


def get_orphan_candidates(zipped_archive_file: str, current_sitemap_filter: datetime.date, domain: str) -> int:
    url_list_web_archive = util.read_lines_from_file(zipped_archive_file, zipped_file=True)

    current_unique_url_set = set()
    total_unique_url_set = set()

    for web_archive_line in url_list_web_archive:
        timestamp, url = web_archive_line.split(" ")[:2]
        timestamp_date = datetime.datetime.strptime(timestamp, '%Y%m%d%H%M%S').date()
        if timestamp_date >= current_sitemap_filter:
            current_unique_url_set.add(url)
        total_unique_url_set.add(url)

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
