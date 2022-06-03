import argparse
import datetime
import sys
import time

import initialize_data_directory
import get_orphan_candidates
import download
import constants
import util
import filter_file_extensions
import check_status_codes
import dynamic_url_detection
from util_data_objects import DUDEParameters, ProbeParameters


ARG_FILTER_DATE_ERROR = "[ARG ERROR] Value ARG_VALUE for arg current_sitemap_filter does not fit any supported format."


def main():
    # prepare and parse arguments
    parser = argparse.ArgumentParser(description="Find orphanage pages for a domain")
    parser.add_argument("domain", type=str, help="Enter a domain to find orphanage pages for")

    parser.add_argument("-s", type=str, dest="download_date", default=None,
                        help="Enter the date of the previously downloaded archive data to skip the download phase.")

    parser.add_argument("--current_sitemap_filter", type=str, dest="current_sitemap_filter", default=None,
                        help="Enter the date from which on a page is marked as still part of the current sitemap")

    # dude args
    parser.add_argument("-d", dest="dude_flag", action='store_true', help="Activate DUDe step.")
    parser.add_argument("--pc", type=float, dest="pc", default=constants.DUDE_DEFAULT_PC, help="Dude Param")
    parser.add_argument("--st", type=float, dest="st", default=constants.DUDE_DEFAULT_ST, help="Dude Param")
    parser.add_argument("--lt", type=float, dest="lt", default=constants.DUDE_DEFAULT_LT, help="Dude Param")
    parser.add_argument("--lc", type=float, dest="lc", default=constants.DUDE_DEFAULT_LC, help="Dude Param")

    # probe args
    parser.add_argument("--delay_between_two_probe_requests", type=float, dest="probe_interval",
                        default=constants.PROBE_INTERVAL,
                        help="Enter the time in seconds the probe alg should wait between two head "
                             "requests to not overload the target server infrastructure.")
    parser.add_argument("--probe_timeout", type=float, dest="probe_timeout", default=constants.PROBE_TIMEOUT,
                        help="Enter the time in seconds after which the probe request should timeout")

    args = parser.parse_args()

    # organise main args
    domain = args.domain
    pre_download_date = args.download_date

    # current pages filter
    if args.current_sitemap_filter is None:
        current_sitemap_filter = util.get_default_current_sitemap_filter()
    else:
        validated_filter = util.parse_year_argument(args.current_sitemap_filter)
        if validated_filter is None:
            print(ARG_FILTER_DATE_ERROR.format(ARG_VALUE=args.current_sitemap_filter))
            sys.exit(1)
        current_sitemap_filter = validated_filter

    # dude flag & params
    enable_dude = args.dude_flag
    dude_params = DUDEParameters(popularity_cutoff=args.pc,
                                 short_prefix_cutoff=args.st,
                                 large_link_count=args.lc,
                                 large_link_len_threshold=args.lt,
                                 pc_value_threshold=2)

    # probe params
    probe_params = ProbeParameters(timeout=args.probe_timeout, interval=args.probe_interval)

    # call main procedure
    orphan_page_detection(domain=domain,
                          pre_download_date=pre_download_date,
                          current_sitemap_filter=current_sitemap_filter,
                          enable_dude=enable_dude, dude_params=dude_params,
                          probe_params=probe_params)


def orphan_page_detection(domain: str, pre_download_date: str | None, current_sitemap_filter: datetime.date,
                          enable_dude: True, dude_params: DUDEParameters, probe_params: ProbeParameters):
    start_time = time.time()

    # create needed directories
    initialize_data_directory.initialize_data_directory(domain)

    # retrieve data from web archiv for domain
    if pre_download_date is None:
        print(f"Retrieving archive data for {domain}.")
        start_time_step = time.time()
        archive_data_file = download.download_step(domain)
        end_time_step = time.time()
        print(f"Retrieving archive data for {domain} took {end_time_step - start_time_step:.2f} seconds.")
    else:
        print(f"Skipped download archive data for {domain} and use data from {pre_download_date}.")
        archive_data_file = constants.ZIPPED_ARCHIVE_NAME_TEMPLATE.format(DOMAIN=domain, DATE=pre_download_date)

    print(f"Extracting candidate orphan pages for {domain}.")
    start_time_step = time.time()
    amount_orphan_candidates = get_orphan_candidates.get_orphan_candidates(archive_data_file, current_sitemap_filter, domain)
    end_time_step = time.time()
    print(f"Extracting candidate orphan pages for {domain} took {end_time_step - start_time_step:.2f} seconds, "
          f"and resulted in {amount_orphan_candidates} pages.")

    print(f"Filtering out list of file extensions for {domain}.")
    start_time_step = time.time()
    amount_orphan_candidates = filter_file_extensions.filter_file_extensions(domain)
    end_time_step = time.time()
    print(f"Filtering out list of file extensions for {domain} took {end_time_step - start_time_step:.2f} seconds, "
          f"and resulted in {amount_orphan_candidates} pages.")

    if enable_dude:
        print(f"Performing Dynamic URL Detection for {domain}.")
        start_time_step = time.time()
        amount_before_dude = amount_orphan_candidates

        amount_orphan_candidates = dynamic_url_detection.dynamic_url_detection(domain, dude_params)

        if amount_before_dude != 0:
            reduction = (amount_before_dude * 100 - amount_orphan_candidates * 100) / amount_before_dude
        else:
            reduction = 0

        end_time_step = time.time()
        print(f"Performing Dynamic URL Detection for {domain} took {end_time_step - start_time_step:.2f} seconds, "
              f"and resulted in {amount_orphan_candidates} pages. This is a reduction of {reduction}%.")
    exit(0)
    amount_probe_urls = amount_orphan_candidates
    print(f"Checking status codes for {amount_probe_urls} pages on {domain} and extracting links with status code 200.")
    start_time_step = time.time()
    amount_orphan_candidates = check_status_codes.check_status_codes(domain, probe_params)
    end_time_step = time.time()
    print(f"Checking status codes for {amount_probe_urls} pages on {domain} and extracting links with status code 200 "
          f"took {end_time_step - start_time_step:.2f} seconds, and resulted in {amount_orphan_candidates} pages.")

    # Finish timing for domain
    end_time = time.time()
    print()
    print("Done!")
    print(f"Total procedure for {domain} took  {end_time - start_time:.2f} seconds.")


if __name__ == "__main__":
    main()
