import argparse
import sys

from orphan_detection import constants
from orphan_detection import util
from orphan_detection import core
from orphan_detection import analysis

ARG_FILTER_DATE_ERROR = "[ARG ERROR] Value ARG_VALUE for arg current_sitemap_filter does not fit any supported format."


def main():
    # prepare and parse arguments
    parser = argparse.ArgumentParser(description="Process to identify potential orphan pages for a single domain.")
    parser.add_argument("domain", type=str, help="Enter a domain to find orphanage pages for")

    parser.add_argument("-s", type=str, dest="download_date", default=None,
                        help="Enter the date of the previously downloaded archive data to skip the download phase.")

    parser.add_argument("-a", dest="analysis_flag", action='store_true', help="Activate Analysis step.")

    # orphan detection
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

    # analysis params
    # Download current page content
    parser.add_argument("--a_cpd_timeout", type=float, dest="cpd_timeout",
                        default=constants.CURRENT_PAGE_DOWNLOAD_DEFAULT_TIMEOUT,
                        help="Download content of page for current state.")
    parser.add_argument("--a_cpd_interval", type=float, dest="cpd_interval",
                        default=constants.CURRENT_PAGE_DOWNLOAD_DEFAULT_INTERVAL, help="Dude Param")

    parser.add_argument("--a_sf_epsilon", type=float, dest="sf_epsilon",
                        default=constants.SIZE_FILTER_DEFAULT_EPSILON, help="Dude Param")
    parser.add_argument("--a_sf_min_amount", type=int, dest="sf_min_amount",
                        default=constants.SIZE_FILTER_DEFAULT_AMOUNT, help="Dude Param")
    # Download last seen page content
    parser.add_argument("--a_lspd_timeout", type=float, dest="lspd_timeout",
                        default=constants.LAST_SEEN_PAGE_DOWNLOAD_DEFAULT_TIMEOUT, help="Dude Param")
    parser.add_argument("--a_lspd_interval", type=float, dest="lspd_interval",
                        default=constants.LAST_SEEN_PAGE_DOWNLOAD_DEFAULT_INTERVAL, help="Dude Param")
    # orphan score calculation params
    parser.add_argument("--a_os_age_weight", type=float, dest="os_age_weight",
                        default=constants.ORPHAN_SCORE_DEFAULT_AGE_WEIGHT, help="Dude Param")
    parser.add_argument("--a_os_similarity_weight", type=float, dest="os_similarity_weight",
                        default=constants.ORPHAN_SCORE_DEFAULT_SIMILARITY_WEIGHT, help="Dude Param")
    parser.add_argument("--a_os_cutoff", type=float, dest="os_cutoff",
                        default=constants.ORPHAN_SCORE_DEFAULT_CUTOFF, help="Dude Param")
    args = parser.parse_args()

    # organise main args
    domain = args.domain
    pre_download_date = args.download_date

    if not args.analysis_flag:  # main orphan detection procedure
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
        exit_code = core.orphaned_pages_detection(domain=domain,
                                      pre_download_date=pre_download_date,
                                      current_sitemap_filter=current_sitemap_filter,
                                      enable_dude=enable_dude, dude_params=dude_params,
                                      probe_params=probe_params)
    else:

        if pre_download_date is None:
            print("[MISSING PARAMETER] The param -s [DATE] is required for the analysis process.")
            return
        # Analysis
        cpd_params = util.ContentDownloadParameters(timeout=args.cpd_timeout, interval=args.cpd_interval)
        sf_params = util.SizeFilterParameters(epsilon=args.sf_epsilon, min_amount_same_size=args.sf_min_amount)
        lspd_params = util.ContentDownloadParameters(timeout=args.lspd_timeout, interval=args.lspd_interval)
        os_params = util.OrphanScoreParameters(age_weight=args.os_age_weight,
                                               similarity_weight=args.os_similarity_weight,
                                               cutoff_value=args.os_cutoff)
        exit_code = analysis.analysis(domain=domain,
                          download_date=pre_download_date,
                          current_download_params=cpd_params,
                          size_filter_params=sf_params,
                          last_seen_download_params=lspd_params,
                          orphan_score_params=os_params)
    exit(exit_code)


if __name__ == "__main__":
    main()
