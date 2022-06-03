import argparse
import sys

from orphan_detection import constants
from orphan_detection import util
from orphan_detection import core

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
    dude_params = util.DUDEParameters(popularity_cutoff=args.pc,
                                      short_prefix_cutoff=args.st,
                                      large_link_count=args.lc,
                                      large_link_len_threshold=args.lt,
                                      pc_value_threshold=2)

    # probe params
    probe_params = util.ProbeParameters(timeout=args.probe_timeout, interval=args.probe_interval)

    # call main procedure
    core.orphaned_pages_detection(domain=domain,
                                  pre_download_date=pre_download_date,
                                  current_sitemap_filter=current_sitemap_filter,
                                  enable_dude=enable_dude, dude_params=dude_params,
                                  probe_params=probe_params)


if __name__ == "__main__":
    main()
