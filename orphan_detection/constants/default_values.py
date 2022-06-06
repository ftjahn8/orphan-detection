
PROBE_INTERVAL = 0.5
PROBE_TIMEOUT = 5

DUDE_DEFAULT_PC = 0.05
DUDE_DEFAULT_ST = 15
DUDE_DEFAULT_LT = 20
DUDE_DEFAULT_LC = 0

CHMOD_USER_ONLY_FILE = 0o600
DEFAULT_ENCODING = "utf-8"

# base url wor web archiv request
WEB_ARCHIV_BASE_URL = 'https://web.archive.org/cdx/search/cdx?url={DOMAIN}&matchType=domain' \
                      '&fl=timestamp,original,length&filter=statuscode:200'


# file filter
LIST_OF_FILTER_FILE_ENDINGS = ["jpg", "gif", "css", "svg", "png", "pdf", "jpeg", "mov", "avi", "mpg", "wmv", "mp4",
                               "ttf", "woff", "eot", "js", "ico", "mp3", "ogg", "webm", "webp", "tiff", "psd", "bmp",
                               "heif", "indd", "ai", "eps", "jpe", "jif", "jfif", "jfi", "tif", "dib", "heic", "ind",
                               "indt", "jp2", "j2k", "jpf", "jpx", "jpm", "mj2", "svgz", "m4a", "m4v", "f4v", "f4a",
                               "m4b", "m4r", "f4b", "3gp", "3gp2", "3g2", "3gpp", "3gpp2", "oga", "ogv", "ogx", "wma",
                               "flv", "mp2", "mpeg", "mpe", "mpv", "m4p", "qt", "swf", "otf"]
FILTER_REGEX = f".+\.({'|'.join(LIST_OF_FILTER_FILE_ENDINGS)}).*$"

# Analysis constants
HTML_PARSER_CONFIG = "html.parser"
DEFAULT_NGRAM_SIZE = 8
DEFAULT_FINGERPRINT_SIZE = 64
