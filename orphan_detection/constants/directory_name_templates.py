"""This file contains all template names for all output directories, result and interim result files."""
# directory names
DATA_DIRECTORY = "./Data/"
ARCHIVE_DATA_DIRECTORY = DATA_DIRECTORY + "Archive_Data/"   # Location of downloaded web archive data
RESULT_DIRECTORY = DATA_DIRECTORY + "Results/"               # Location for results of the process
TMP_DIRECTORY = DATA_DIRECTORY + "tmp/"                     # Location for temporary files of the process

DOMAIN_DIRECTORY = RESULT_DIRECTORY + "{DOMAIN}/"  # Folder to store the results for the domain being processed
DOMAIN_TMP_DIRECTORY = TMP_DIRECTORY + "{DOMAIN}/"  # Folder to store temporary data for the domain being processed


# file name templates
ZIPPED_ARCHIVE_NAME_TEMPLATE = ARCHIVE_DATA_DIRECTORY + "{DOMAIN}_{DATE}.txt.gz"

CURRENT_UNIQUE_URL_NAME_TEMPLATE = DOMAIN_TMP_DIRECTORY + "{DOMAIN}_unique_links_{FILTER}.txt"
TOTAL_UNIQUE_URL_NAME_TEMPLATE = DOMAIN_TMP_DIRECTORY + "{DOMAIN}_unique_links_total.txt"

CANDIDATES_LIST_NAME_TEMPLATE = DOMAIN_TMP_DIRECTORY + "{DOMAIN}_orphan_candidates.txt"
CANDIDATES_FILTERED_LIST_NAME_TEMPLATE = DOMAIN_TMP_DIRECTORY + "{DOMAIN}_orphan_candidates_filtered.txt"

STATUS_CODES_LIST_NAME_TEMPLATE = DOMAIN_TMP_DIRECTORY + "{DOMAIN}_status_codes.txt"
DUDE_EXCLUDED_LIST_NAME_TEMPLATE = DOMAIN_TMP_DIRECTORY + "{DOMAIN}_dude_excluded.txt"
DUDE_EXCLUDED_PREFIXES_NAME_TEMPLATE = DOMAIN_TMP_DIRECTORY + "{DOMAIN}_dude_prefix_excluded.txt"

ERROR_RESPONSES_LIST_NAME_TEMPLATE = DOMAIN_TMP_DIRECTORY + "{DOMAIN}_error_responses.txt"

CANDIDATES_TO_PROBE_LIST_NAME_TEMPLATE = DOMAIN_DIRECTORY + "{DOMAIN}_list_to_probe.txt"
POTENTIAL_ORPHAN_LIST_NAME_TEMPLATE = DOMAIN_DIRECTORY + "{DOMAIN}_potential_orphans.txt"


# Analysis templates
PAGES_TMP_DIRECTORY = TMP_DIRECTORY + "pages/"

LAST_SEEN_DATES_NAME_TEMPLATE = DOMAIN_TMP_DIRECTORY + "{DOMAIN}_last_seen_dates.txt"
PAGES_CONTENT_NAME_TEMPLATE = PAGES_TMP_DIRECTORY + "{FILE_NAME}.txt"

DOWNLOAD_ERROR_C_NAME_TEMPLATE = DOMAIN_TMP_DIRECTORY + "{DOMAIN}_download_current_error.txt"
DOWNLOAD_ERROR_LS_NAME_TEMPLATE = DOMAIN_TMP_DIRECTORY + "{DOMAIN}_download_last_seen_error.txt"

PAGE_SIZE_NAME_TEMPLATE = DOMAIN_TMP_DIRECTORY + "{DOMAIN}_with_size.txt"
PAGE_SIZE_FILTERED_NAME_TEMPLATE = DOMAIN_TMP_DIRECTORY + "{DOMAIN}_with_size_filtered.txt"
PAGE_SIZE_REMOVED_NAME_TEMPLATE = DOMAIN_TMP_DIRECTORY + "{DOMAIN}_with_size_removed.txt"

SIMILARITY_SCORES_NAME_TEMPLATE = DOMAIN_TMP_DIRECTORY + "{DOMAIN}_similarity_scores.txt"
ORPHAN_SCORES_NAME_TEMPLATE = DOMAIN_TMP_DIRECTORY + "{DOMAIN}_orphan_score.txt"
ORPHAN_SCORES_FILTERED_NAME_TEMPLATE = DOMAIN_TMP_DIRECTORY + "{DOMAIN}_after_orphan_score_filter.txt"

ANALYSIS_RESULT_FILE = DOMAIN_DIRECTORY + "{DOMAIN}_analysis_results.txt"
ALL_ANALYSIS_RESULT_FILE = DOMAIN_TMP_DIRECTORY + "{DOMAIN}_all_analysis_results.txt"
