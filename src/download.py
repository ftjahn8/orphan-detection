from orphan_detection import constants
from orphan_detection import util


def download_step(searched_domain: str) -> str:
    date = util.get_date()
    zipped_archive_file = constants.ZIPPED_ARCHIVE_NAME_TEMPLATE.format(DOMAIN=searched_domain, DATE=date)

    # retrieve data from web archiv
    response_data = util.download_web_archive_data(domain=searched_domain)

    # zip results and save in archive directory
    util.write_lines_to_file(zipped_archive_file, response_data, zipped_file=True)
    return zipped_archive_file
