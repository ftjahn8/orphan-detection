"""This file contains all default values for the package."""


# Orphan Detection Process constant

# If you want to change the default sitemap filter for the get_orphan_candidates-step,
# you have to adjust it in the util.date_operations.py file.

# dude default values
DUDE_DEFAULT_PC = 0.05
DUDE_DEFAULT_ST = 15
DUDE_DEFAULT_LT = 20
DUDE_DEFAULT_LC = 0
DUDE_DEFAULT_MSS = 40

# probe params
PROBE_INTERVAL = 0.5
PROBE_TIMEOUT = 5

# File related default values
CHMOD_USER_ONLY_FILE = 0o600
DEFAULT_ENCODING = "utf-8"

# base url for web archiv request
WEB_ARCHIV_BASE_URL = 'https://web.archive.org/cdx/search/cdx?url={DOMAIN}&matchType=domain' \
                      '&fl=timestamp,original,length&filter=statuscode:200'

# base url for downloading a page in its last seen form from the web archiv
WEB_ARCHIV_LAST_SEEN_VERSION = "https://web.archive.org/web/{LAST_SEEN_DATE}id_/{URL}"

# ressource file filter
LIST_OF_FILTER_FILE_ENDINGS = ["jpg", "gif", "css", "svg", "png", "pdf", "jpeg", "mov", "avi", "mpg", "wmv", "mp4",
                               "ttf", "woff", "eot", "js", "ico", "mp3", "ogg", "webm", "webp", "tiff", "psd", "bmp",
                               "heif", "indd", "ai", "eps", "jpe", "jif", "jfif", "jfi", "tif", "dib", "heic", "ind",
                               "indt", "jp2", "j2k", "jpf", "jpx", "jpm", "mj2", "svgz", "m4a", "m4v", "f4v", "f4a",
                               "m4b", "m4r", "f4b", "3gp", "3gp2", "3g2", "3gpp", "3gpp2", "oga", "ogv", "ogx", "wma",
                               "flv", "mp2", "mpeg", "mpe", "mpv", "m4p", "qt", "swf", "otf"]

# pylint: disable-msg=anomalous-backslash-in-string
FILTER_REGEX = f".+\.({'|'.join(LIST_OF_FILTER_FILE_ENDINGS)}).*$"  # noqa: W605

# Analysis constants
# default param values
CURRENT_PAGE_DOWNLOAD_DEFAULT_TIMEOUT = 5
CURRENT_PAGE_DOWNLOAD_DEFAULT_INTERVAL = 1

SIZE_FILTER_DEFAULT_EPSILON = 5
SIZE_FILTER_DEFAULT_AMOUNT = 2

LAST_SEEN_PAGE_DOWNLOAD_DEFAULT_TIMEOUT = 5
LAST_SEEN_PAGE_DOWNLOAD_DEFAULT_INTERVAL = 1.5

ORPHAN_SCORE_DEFAULT_AGE_WEIGHT = 0.1
ORPHAN_SCORE_DEFAULT_SIMILARITY_WEIGHT = 0.9
ORPHAN_SCORE_DEFAULT_CUTOFF = 0.7

# download defaults
DOWNLOAD_HEADER = {'Accept-Encoding': DEFAULT_ENCODING}
HTML_PARSER_CONFIG = "html.parser"

# fingerprint defaults
DEFAULT_NGRAM_SIZE = 8
DEFAULT_FINGERPRINT_SIZE = 64

# Keywords for page analysis
COPYRIGHT_KEYWORDS = ["copyright", "&copy", "&#169", chr(169)]
NOT_FOUND_KEYWORDS = ["404 Not Found", "404 Error", "Page Not Found"]
EXPIRED_KEYWORDS = ["If you are the owner of this", "Domain expired", "website has been suspended"]
REDIRECT_KEYWORDS = ["top.location", "http-equiv=\"refresh\"", "header(\'Location:", "redirect_to", "writeHead(3",
                     "Redirect(", "AddHeader(\"Location\"", "RedirectPermanent", "Object moved to", "window.location",
                     "301 Moved Permanently", "302 Found"]
FRAME_TAGS = ["iframe", "frame", "frameset"]
