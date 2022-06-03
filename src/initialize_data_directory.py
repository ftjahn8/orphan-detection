from orphan_detection import constants
from orphan_detection import util


def initialize_data_directory(domain: str) -> None:
    # create static directories
    print(f"Creating data directory structure for {domain}.")
    util.create_directory(constants.DATA_DIRECTORY)
    util.create_directory(constants.ARCHIVE_DATA_DIRECTORY)
    util.create_directory(constants.RESULT_DIRECTORY)
    util.create_directory(constants.TMP_DIRECTORY)

    # create domain specific directories
    util.create_directory(constants.DOMAIN_DIRECTORY.format(DOMAIN=domain))
    util.create_directory(constants.DOMAIN_TMP_DIRECTORY.format(DOMAIN=domain))
    print(f"Finished creating data directory structure.")
