import requests

import util
import constants


def download_step(searched_domain: str) -> str:
    date = util.get_date()
    zipped_archive_file = constants.ZIPPED_ARCHIVE_NAME_TEMPLATE.format(DOMAIN=searched_domain, DATE=date)

    # retrieve data from web archiv
    response = requests.get(constants.WEB_ARCHIV_BASE_URL.format(DOMAIN=searched_domain))
    response.raise_for_status()

    # zip results and save in archive directory
    util.save_to_gzip_file(zipped_archive_file, response.text)
    return zipped_archive_file
