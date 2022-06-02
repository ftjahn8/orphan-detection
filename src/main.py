import argparse
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


def main():
    # prepare and parse arguments
    parser = argparse.ArgumentParser(description="Find orphanage pages for a domain")
    parser.add_argument("domain", type=str, help="Enter a domain to find orphanage pages for")
    parser.add_argument("-s", type=str, dest="download_date", default=None,
                        help="Enter the date of the previously downloaded archive data to skip the download phase.")
    parser.add_argument("-d", dest="dude", action='store_true', help="Activate DUDe step.")
    parser.add_argument("--current_sitemap_filter", type=str, dest="current_sitemap_filter", default=None,
                        help="Enter the date from which on a page is marked as still part of the current sitemap")
    parser.add_argument("--delay_between_two_probe_requests", type=float, dest="probe_delay",
                        default=constants.PROBE_DELAY, help="Enter the time in seconds the probe alg should wait "
                                                            "between two head requests to not overload the target server infrastructure.")

    parser.add_argument("--probe_timeout", type=float, dest="probe_timeout", default=constants.PROBE_TIMEOUT,
                        help="Enter the time in seconds after which the probe request should timeout")

    parser.add_argument("--pc", type=float, dest="pc", default=constants.DUDE_DEFAULT_PC,
                        help="Dude Param")

    parser.add_argument("--st", type=float, dest="st", default=constants.DUDE_DEFAULT_ST,
                        help="Dude Param")

    parser.add_argument("--lt", type=float, dest="lt", default=constants.DUDE_DEFAULT_LT,
                        help="Dude Param")

    parser.add_argument("--lc", type=float, dest="lc", default=constants.DUDE_DEFAULT_LC,
                        help="Dude Param")
    args = parser.parse_args()

    # get main args
    domain = args.domain

    probe_delay = args.probe_delay
    probe_timeout = args.probe_timeout

    skip_download_phase = args.download_date is not None
    skip_download_date = args.download_date

    dude = args.dude
    popularity_cutoff = args.pc
    short_prefix_cutoff = args.st
    large_link_len_threshold = args.lt
    large_link_count = args.lc

    if args.current_sitemap_filter is None:
        current_sitemap_filter = util.get_default_current_sitemap_filter()
    else:
        validated_filer = util.parse_year_argument(args.current_sitemap_filter)
        if validated_filer is None:
            print(f"[ARGUMENT ERROR] Value of {args.current_sitemap_filter} Argument current_sitemap_filter "
                  f"does not fit one of the supported formats.")
            sys.exit(1)
        current_sitemap_filter = validated_filer

    start_time = time.time()

    # create needed directories
    initialize_data_directory.initialize_data_directory(domain)

    # retrieve data from web archiv for domain
    if not skip_download_phase:
        print(f"Retrieving archive data for {domain}.")
        start_time_step = time.time()
        archive_data_file = download.download_step(domain)
        end_time_step = time.time()
        print(f"Retrieving archive data for {domain} took {end_time_step - start_time_step:.2f} seconds.")
    else:
        print(f"Skipped download archive data for {domain} and use data from {skip_download_date}.")
        archive_data_file = constants.ZIPPED_ARCHIVE_NAME_TEMPLATE.format(DOMAIN=domain, DATE=skip_download_date)

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

    # TODO DUDE
    if dude:
        print(f"Performing Dynamic URL Detection for {domain}.")
        start_time_step = time.time()
        amount_before_dude = amount_orphan_candidates


        amount_orphan_candidates = dynamic_url_detection.dynamic_url_detection(domain, popularity_cutoff,
                                                                               short_prefix_cutoff, large_link_len_threshold, large_link_count)

        reduction = (amount_before_dude * 100 - amount_orphan_candidates * 100) / amount_before_dude if amount_before_dude != 0 else 0
        end_time_step = time.time()
        print(f"Performing Dynamic URL Detection for {domain} took {end_time_step - start_time_step:.2f} seconds, "
              f"and resulted in {amount_orphan_candidates} pages. This is a reduction of {reduction}%.")
    exit(0)
    amount_probe_urls = amount_orphan_candidates
    print(f"Checking status codes for {amount_probe_urls} pages on {domain} and extracting links with status code 200.")
    start_time_step = time.time()
    amount_orphan_candidates = check_status_codes.check_status_codes(domain, probe_delay, probe_timeout)
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
