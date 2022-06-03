# directory names
DATA_DIRECTORY = "../Data/"
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