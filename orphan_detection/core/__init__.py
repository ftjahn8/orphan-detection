import datetime
import time

from orphan_detection import constants
from orphan_detection import util

from orphan_detection.core.orphan_detection_steps import initialize_data_directory, \
    download_web_archive_data, get_orphan_candidates, filter_file_extensions, check_status_codes

from orphan_detection.core.dynamic_url_detection import dynamic_url_detection

__all__ = ["orphaned_pages_detection"]


def orphaned_pages_detection(domain: str, pre_download_date: str | None, current_sitemap_filter: datetime.date,
                             enable_dude: True, dude_params: util.DUDEParameters,
                             probe_params: util.ProbeParameters) -> int:
    start_time = time.time()

    # create needed directories
    print(f"Creating data directory structure for {domain}.")
    initialize_data_directory(domain)
    print("Finished creating data directory structure.")

    # retrieve data from web archiv for domain
    if pre_download_date is None:
        print(f"Retrieving archive data for {domain}.")
        start_time_step = time.time()
        archive_data_file = download_web_archive_data(domain)
        end_time_step = time.time()
        print(f"Retrieving archive data for {domain} took {end_time_step - start_time_step:.2f} seconds.")
    else:
        print(f"Skipped download archive data for {domain} and use data from date {pre_download_date}.")
        archive_data_file = constants.ZIPPED_ARCHIVE_NAME_TEMPLATE.format(DOMAIN=domain, DATE=pre_download_date)

    if not util.is_file(archive_data_file):
        print(f"[Error] No archive data file found at path {archive_data_file}. Stopped procedure.")
        return 1

    print(f"Extracting candidate orphan pages for {domain}.")
    start_time_step = time.time()
    amount_orphan_candidates = get_orphan_candidates(archive_data_file, current_sitemap_filter, domain)
    end_time_step = time.time()
    print(f"Extracting candidate orphan pages for {domain} took {end_time_step - start_time_step:.2f} seconds, "
          f"and resulted in {amount_orphan_candidates} pages.")

    print(f"Filtering out list of file extensions for {domain}.")
    start_time_step = time.time()
    amount_orphan_candidates = filter_file_extensions(domain)
    end_time_step = time.time()
    print(f"Filtering out list of file extensions for {domain} took {end_time_step - start_time_step:.2f} seconds, "
          f"and resulted in {amount_orphan_candidates} pages.")

    if enable_dude:
        print(f"Performing Dynamic URL Detection for {domain}.")
        start_time_step = time.time()
        amount_before_dude = amount_orphan_candidates

        amount_orphan_candidates = dynamic_url_detection(domain, dude_params)

        if amount_before_dude != 0:
            reduction = (amount_before_dude * 100 - amount_orphan_candidates * 100) / amount_before_dude
        else:
            reduction = 0

        end_time_step = time.time()
        print(f"Performing Dynamic URL Detection for {domain} took {end_time_step - start_time_step:.2f} seconds, "
              f"and resulted in {amount_orphan_candidates} pages. This is a reduction of {reduction:.2f}%.")
    return 1
    amount_probe_urls = amount_orphan_candidates
    print(f"Checking status codes for {amount_probe_urls} pages on {domain} and extracting links with status code 200.")
    start_time_step = time.time()
    amount_orphan_candidates = check_status_codes(domain, probe_params)
    end_time_step = time.time()
    print(f"Checking status codes for {amount_probe_urls} pages on {domain} and extracting links with status code 200 "
          f"took {end_time_step - start_time_step:.2f} seconds, and resulted in {amount_orphan_candidates} pages.")

    # Finish timing for domain
    end_time = time.time()
    print()
    print("Done!")
    print(f"Total procedure for {domain} took  {end_time - start_time:.2f} seconds.")
    return 0
