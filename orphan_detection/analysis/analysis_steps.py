from typing import Dict

import requests

from orphan_detection import util
from orphan_detection import constants

import time
from tqdm import tqdm
from orphan_detection.analysis.similarity_score_functions import calculate_similarity_score

ANALYSIS_DATA_TYPE = Dict[str, Dict[str, int | str]]


def get_last_seen_date(data: ANALYSIS_DATA_TYPE, domain: str, download_date: str) -> int:
    zipped_archive_file = constants.ZIPPED_ARCHIVE_NAME_TEMPLATE.format(DOMAIN=domain, DATE=download_date)
    url_list_web_archive = util.read_lines_from_file(zipped_archive_file, zipped_file=True)

    oldest_page_year = 9999

    last_seen_lookup = {}
    for line in url_list_web_archive:
        timestamp, url = line.split(" ")[:2]
        if url in last_seen_lookup:
            if int(timestamp) > last_seen_lookup[url]:
                last_seen_lookup[url] = int(timestamp)
        else:
            last_seen_lookup[url] = int(timestamp)

        oldest_page_year = min(int(timestamp[:4]), oldest_page_year)

    last_seen_output = []
    for candidate in data.keys():
        last_seen_date = last_seen_lookup[candidate]
        last_seen_output.append(f"{candidate} {last_seen_date}")
        data[candidate]["last_seen_date"] = last_seen_date

    util.write_lines_to_file("..\\Data\\tmp\\hm.edu\\hm.edu_last_seen_dates", last_seen_output)
    return oldest_page_year


def get_current_page_content(data: ANALYSIS_DATA_TYPE) -> int:
    no_html = []
    to_be_removed = []

    for candidate in tqdm(data.keys()):
        current_page_response = requests.get(candidate, headers={'Accept-Encoding': constants.DEFAULT_ENCODING})

        current_content_type_header = current_page_response.headers.get("Content-Type")
        current_content = current_page_response.content
        if current_content_type_header is None or "text/html" not in current_content_type_header.lower():
            no_html.append(f"[NO HTML        ] {current_content_type_header:15s} {candidate} ")
            to_be_removed.append(candidate)
            continue

        current_page_hashed_name = util.get_md5_hash(candidate)

        if f"charset={constants.DEFAULT_ENCODING}" in current_content_type_header.lower():
            encoding_current = constants.DEFAULT_ENCODING
        elif "charset=" in current_content_type_header.lower():
            encoding_current = current_content_type_header.lower().split("charset=")[1]
        elif current_content_type_header is not None and current_page_response.encoding:
            encoding_current = current_page_response.encoding
        else:
            encoding_current = util.guess_encoding(current_content)

        if encoding_current != constants.DEFAULT_ENCODING:
            try:
                current_content = current_content.decode(encoding_current).encode(constants.DEFAULT_ENCODING)
            except LookupError:
                no_html.append(f"[ENCODING ERROR] {encoding_current:15s} {candidate}")
                to_be_removed.append(candidate)
                continue

        util.save_to_bin_file(f"..\\Data\\tmp\\pages\\{current_page_hashed_name}", current_content)
        data[candidate]["current_page_file"] = current_page_hashed_name
        time.sleep(1)

    util.write_lines_to_file("..\\Data\\tmp\\hm.edu\\hm.edu_download_current_error", no_html)
    for url in to_be_removed:
        del data[url]

    return len(data)


def retrieve_page_sizes(data: ANALYSIS_DATA_TYPE) -> None:
    for candidate_url, candidate_data in data.items():
        candidate_content = util.read_from_bin_file(candidate_data["current_page_file"])
        data[candidate_url]["current_page_file"] = len(candidate_content)


def retrieve_page_size():
    url_list = util.read_lines_from_file("..\\Data\\Results\\hm.edu\\hm.edu_potential_orphans_2.txt")
    page_size = {}
    for url in url_list:
        size = len(requests.get(url).content)
        page_size[url] = size
        time.sleep(0.2)

    lines_output = [f"{url} {size}" for url, size in page_size.items()]
    util.write_lines_to_file("..\\Data\\tmp\\hm.edu\\hm.edu_with_size", lines_output)


def filter_same_size():
    url_list = util.read_lines_from_file("..\\Data\\tmp\\hm.edu\\hm.edu_with_size")
    page_size_lookup = []
    for line in url_list:
        url, size = line.split(" ")[:2]
        page_size_lookup.append((url, int(size)))

    start_len = len(page_size_lookup)
    to_remove = []
    tmp_remove = []
    current_size = 0
    epsilon = 5

    # Loop over entries, ordered by size
    for url, size in sorted(page_size_lookup, key=lambda x: x[1]):
        # If size is within reasonable similarity to previous size, add to discard list
        if size <= current_size + epsilon:
            tmp_remove.append((url, size))
            current_size = size
            continue
        # Write out current discard list and continue procedure
        else:
            if len(tmp_remove) >= 2:
                to_remove += tmp_remove
            tmp_remove = [(url, size)]
            current_size = size

    # Remove all entries that need to be discarded
    filtered = list(set(page_size_lookup) - set(to_remove))
    # Write out results
    output = [f"{url} {size}" for url, size in filtered]
    util.write_lines_to_file("..\\Data\\tmp\\hm.edu\\hm.edu_with_size_filtered", output)

    # Calculate the reduction percentage
    end_len = len(filtered)
    reduction = 100 - ((end_len / start_len) * 100)
    print("Reduction of {:.2f}%".format(reduction))



def get_type():
    header = {'Accept-Encoding': 'utf-8'}
    url_list = util.read_lines_from_file("..\\Data\\tmp\\hm.edu\\hm.edu_with_dates")
    page_size_lookup = []
    no_html = []
    for line in url_list:
        url, size, last_seen = line.split(" ")[:3]
        page_size_lookup.append((url, int(size), last_seen))

    output = []
    for url, size, last_seen in page_size_lookup:
        current_page_head = requests.head(url, headers=header)
        last_seen_page_head = requests.head(f"https://web.archive.org/web/{last_seen}id_/{url}", headers=header)

        content_type_current = current_page_head.headers.get("Content-Type")
        content_type_past = last_seen_page_head.headers.get("Content-Type")
        if content_type_current is None or "text/html" not in content_type_current:
            no_html.append(f"{url} Current Page does not return Content Type text/html: {content_type_current}")
            continue

        if content_type_past is None or "text/html" not in content_type_past:
            no_html.append(f"{url} Last Seen Page does not return Content Type text/html: {content_type_past}")
            continue

        time.sleep(1)
        hash_name_current = util.get_md5_hash(url)
        hash_name_past = util.get_md5_hash(f"{url}_{last_seen}")

        content_current = requests.get(url, headers=header).content
        content_past = requests.get(f"https://web.archive.org/web/{last_seen}id_/{url}", headers=header).content

        if "charset=utf-8" in content_type_current.lower():
            encoding_current = "utf-8"
        elif "charset=" in content_type_current.lower():
            encoding_current = content_type_current.lower().split("charset=")[1]
        elif current_page_head.encoding:
            encoding_current = current_page_head.encoding
        else:
            encoding_current = util.guess_encoding(content_current)

        if encoding_current != "utf-8":
            try:
                content_current = content_current.decode(encoding_current).encode("utf-8")
            except LookupError:
                no_html.append(f"{url} Unknown current encoding: {encoding_current}")
                continue

        if "charset=utf-8" in content_type_past.lower():
            encoding_past = "utf-8"
        elif "charset=" in content_type_past.lower():
            encoding_past = content_type_past.lower().split("charset=")[1]
        elif last_seen_page_head.encoding:
            encoding_past = last_seen_page_head.encoding
        else:
            encoding_past = util.guess_encoding(content_past)

        if encoding_past != "utf-8":
            try:
                content_past = content_past.decode(encoding_past).encode("utf-8")
            except LookupError:
                no_html.append(f"{url} Unknown past encoding: {encoding_current}")
                continue

        with open(f"..\\Data\\tmp\\pages\\{hash_name_current}", "wb") as outfile:
            outfile.write(content_current)

        with open(f"..\\Data\\tmp\\pages\\{hash_name_past}", "wb") as outfile:
            outfile.write(content_past)
        print(url, encoding_current, current_page_head.headers.get("Content-Type"), current_page_head.encoding,
              encoding_past, last_seen_page_head.headers.get("Content-Type"), last_seen_page_head.encoding)
        output.append((url, size, last_seen, calculate_similarity_score(content_current, content_past)))
        time.sleep(1)

    util.write_lines_to_file("..\\Data\\tmp\\hm.edu\\hm.edu_with_dates_after_fingerprint",
                             [f'{line[0]} {line[1]} {line[2]} {line[3]}' for line in output])
    util.write_lines_to_file("..\\Data\\tmp\\hm.edu\\hm.edu_fingerprint_error", no_html)


def orphan_likelihood_score_filter():
    age_weight = 0.1
    sim_weight = 0.9
    cutoff = 0.7

    min_year = get_earliest_year("")
    current_year = util.get_current_year()

    max_scale = current_year - min_year

    orphan_scores = []
    orphan_scores_filtered = []
    data = util.read_lines_from_file("..\\Data\\tmp\\hm.edu\\hm.edu_with_dates_after_fingerprint")
    for line in data:
        url, _, last_seen, sim_score = line.split(" ")
        url_year = int(last_seen[:4])

        orphan_score = (max_scale * float(sim_score) * sim_weight + age_weight * (current_year - url_year)) / max_scale

        orphan_scores.append(f"{url} {orphan_score}")
        if orphan_score > cutoff:
            orphan_scores_filtered.append(f"{url} {orphan_score}")

    util.write_lines_to_file("..\\Data\\tmp\\hm.edu\\hm.edu_orphan_score", orphan_scores)
    util.write_lines_to_file("..\\Data\\tmp\\hm.edu\\hm.edu_after_orphan_score_filter", orphan_scores_filtered)


def get_earliest_year(download_date: str) -> int:
    zipped_archive_file = constants.ZIPPED_ARCHIVE_NAME_TEMPLATE.format(DOMAIN="hm.edu", DATE="2022-05-28")
    url_list_web_archive = util.read_lines_from_file(zipped_archive_file, zipped_file=True)

    set_year = set()
    for line in url_list_web_archive:
        set_year.add(int(line[:4]))
    return min(set_year)

# retrieve_page_size()
# filter_same_size()
# get_last_seen_date()
# get_type()
# orphan_likelihood_score_filter()
