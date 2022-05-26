# misc
PROBE_DELAY = 0.5
PROBE_TIMEOUT = 5

DUDE_DEFAULT_PC = 0.05
DUDE_DEFAULT_ST = 15
DUDE_DEFAULT_LT = 20
DUDE_DEFAULT_LC = 0

CHMOD_USER_ONLY_FILE = 0o600

# directory names
DATA_DIRECTORY = "../Data/"
ARCHIVE_DATA_DIRECTORY = DATA_DIRECTORY + "Archive_Data/"   # Location of downloaded web archive data
RESULT_DIRECTORY = DATA_DIRECTORY + "Result/"               # Location for results of the process
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

ERROR_RESPONSES_LIST_NAME_TEMPLATE = DOMAIN_TMP_DIRECTORY + "{DOMAIN}_error_responses.txt"

CANDIDATES_TO_PROBE_LIST_NAME_TEMPLATE = DOMAIN_DIRECTORY + "{DOMAIN}_list_to_probe.txt"
POTENTIAL_ORPHAN_LIST_NAME_TEMPLATE = DOMAIN_DIRECTORY + "{DOMAIN}_potential_orphans.txt"

# base url wor web archiv request
WEB_ARCHIV_BASE_URL = 'https://web.archive.org/cdx/search/cdx?url={DOMAIN}&matchType=domain' \
                      '&fl=timestamp,original,length&filter=statuscode:200'

# file filter
LIST_OF_FILTER_FILE_ENDINGS = ["jpg", "gif", "css", "svg", "png", "pdf", "jpeg", "mov", "avi", "mpg", "wmv", "mp4",
                               "ttf", "woff", "eot", "js", "ico", "mp3", "ogg", "webm", "webp", "tiff", "psd", "bmp",
                               "heif", "indd", "ai", "eps", "jpe", "jif", "jfif", "jfi", "tif", "dib", "heic", "ind",
                               "indt", "jp2", "j2k", "jpf", "jpx", "jpm", "mj2", "svgz", "m4a", "m4v", "f4v", "f4a",
                               "m4b", "m4r", "f4b", "3gp", "3gp2", "3g2", "3gpp", "3gpp2", "oga", "ogv", "ogx", "wma",
                               "flv", "mp2", "mpeg", "mpe", "mpv", "m4p", "qt", "swf"]
FILTER_REGEX = f".+\.({'|'.join(LIST_OF_FILTER_FILE_ENDINGS)}).*$"
