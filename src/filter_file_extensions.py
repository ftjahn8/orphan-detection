from orphan_detection import constants
from orphan_detection import util


def filter_file_extensions(domain: str) -> int:
    orphan_candidates_file_path = constants.CANDIDATES_LIST_NAME_TEMPLATE.format(DOMAIN=domain)
    candidates_unfiltered = util.read_lines_from_file(orphan_candidates_file_path)

    candidates_filtered = []
    for url in candidates_unfiltered:
        if not util.is_ressource_url(url):
            candidates_filtered.append(url)

    candidates_filtered_file_path = constants.CANDIDATES_FILTERED_LIST_NAME_TEMPLATE.format(DOMAIN=domain)
    util.write_lines_to_file(candidates_filtered_file_path, candidates_filtered)

    candidates_to_probe_path = constants.CANDIDATES_TO_PROBE_LIST_NAME_TEMPLATE.format(DOMAIN=domain)
    util.write_lines_to_file(candidates_to_probe_path, candidates_filtered)
    return len(candidates_filtered)
