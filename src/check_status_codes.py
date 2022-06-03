import time

from tqdm import tqdm

from orphan_detection import constants
from orphan_detection import util


def check_status_codes(domain: str, probe_args: util.ProbeParameters) -> int:
    probe_candidates_path = constants.CANDIDATES_TO_PROBE_LIST_NAME_TEMPLATE.format(DOMAIN=domain)
    probe_candidates = util.read_lines_from_file(probe_candidates_path)

    potential_orphans = {}
    all_status_codes = {}
    error_responses = {}

    probe_candidates_shuffled = probe_candidates.copy()
    probe_candidates_shuffled = util.shuffle_candidates_list(probe_candidates_shuffled)
    for url in tqdm(probe_candidates_shuffled):
        status_code, error_msg = util.probe_url(url, timeout_after=probe_args.timeout)

        if status_code == 200:
            potential_orphans[url] = url

        if error_msg is not None:
            error_responses[url] = f"{error_msg:25s} {url}"

        all_status_codes[url] = f"{status_code:03} {url}"
        time.sleep(probe_args.interval)

    potential_orphans_sorted = [potential_orphans[url] for url in probe_candidates if url in potential_orphans]
    all_status_codes_sorted = [all_status_codes[url] for url in probe_candidates]
    error_responses_sorted = [error_responses[url] for url in probe_candidates if url in error_responses]

    potential_orphan_path = constants.POTENTIAL_ORPHAN_LIST_NAME_TEMPLATE.format(DOMAIN=domain)
    util.write_lines_to_file(potential_orphan_path, potential_orphans_sorted)

    status_code_list_path = constants.STATUS_CODES_LIST_NAME_TEMPLATE.format(DOMAIN=domain)
    util.write_lines_to_file(status_code_list_path, all_status_codes_sorted)

    error_responses_path = constants.ERROR_RESPONSES_LIST_NAME_TEMPLATE.format(DOMAIN=domain)
    util.write_lines_to_file(error_responses_path, error_responses_sorted)

    return len(potential_orphans_sorted)
