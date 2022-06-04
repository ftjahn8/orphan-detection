import datetime
import json
import re
from typing import List

import requests
from bs4 import BeautifulSoup

from orphan_detection import util, constants
import time
import hashlib

from orphan_detection.analysis.hash import fnv_1a


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


def get_last_seen_date():
    zipped_archive_file = constants.ZIPPED_ARCHIVE_NAME_TEMPLATE.format(DOMAIN="hm.edu", DATE="2022-05-28")
    url_list_web_archive = util.read_lines_from_file(zipped_archive_file, zipped_file=True)

    url_list = util.read_lines_from_file("..\\Data\\tmp\\hm.edu\\hm.edu_with_size_filtered")
    page_size_lookup = []
    for line in url_list:
        url, size = line.split(" ")[:2]
        page_size_lookup.append((url, int(size)))

    last_seen_lookup = {}
    for line in url_list_web_archive:
        timestamp, url = line.split(" ")[:2]
        if url in last_seen_lookup:
            if int(timestamp) > last_seen_lookup[url]:
                last_seen_lookup[url] = int(timestamp)
        else:
            last_seen_lookup[url] = int(timestamp)

    output = [(url, size, last_seen_lookup[url]) for url, size in page_size_lookup]
    output.sort(key=lambda x: x[0])
    output = [f"{url} {size} {date}" for url, size, date in output]
    util.write_lines_to_file("..\\Data\\tmp\\hm.edu\\hm.edu_with_dates", output)


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
        hash_name_current = hashlib.md5(url.encode("utf-8")).hexdigest()
        hash_name_past = hashlib.md5(f"{url}_{last_seen}".encode("utf-8")).hexdigest()

        content_current = requests.get(url, headers=header).content
        content_past = requests.get(f"https://web.archive.org/web/{last_seen}id_/{url}", headers=header).content

        if "charset=utf-8" in content_type_current.lower():
            encoding_current = "utf-8"
        elif "charset=" in content_type_current.lower():
            encoding_current = content_type_current.lower().split("charset=")[1]
        elif current_page_head.encoding:
            encoding_current = current_page_head.encoding
        else:
            encoding_current = guess_encoding(content_current)

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
            encoding_past = guess_encoding(content_past)

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
        output.append((url, size, last_seen, get_similarity(content_current, content_past)))
        time.sleep(1)

    util.write_lines_to_file("..\\Data\\tmp\\hm.edu\\hm.edu_with_dates_after_fingerprint",
                             [f'{line[0]} {line[1]} {line[2]} {line[3]}' for line in output])
    util.write_lines_to_file("..\\Data\\tmp\\hm.edu\\hm.edu_fingerprint_error", no_html)


def guess_encoding(text: bytes) -> str:
    return json.detect_encoding(text)


def get_similarity(content_current: bytes, content_past: bytes) -> float:
    current_words = prepare_text(content_current)
    past_words = prepare_text(content_past)

    current_fingerprint = calculate_finger_print(current_words)
    past_fingerprint = calculate_finger_print(past_words)
    return calculate_similarity_value(current_fingerprint, past_fingerprint)


def prepare_text(text: bytes) -> List[str]:
    bs_soup = BeautifulSoup(text, 'html.parser')
    text_extracted = bs_soup.get_text()
    return re.findall(r"[\w']+", text_extracted.lower())


def get_ngrams(wordlist: List[str], n: int) -> List[List[str]]:
    ngrams = []
    for i in range(len(wordlist) - n + 1):
        ngrams.append(wordlist[i:i + n])
    return ngrams


def calculate_finger_print(word_list: List[str]) -> list[int]:
    fingerprint = [0 for _ in range(64)]
    ngram_list = get_ngrams(word_list, 8)
    hashed_ngrams = [fnv_1a(''.join(ngram).encode("utf-8")) for ngram in ngram_list]

    for hash_gram in hashed_ngrams:
        binary = bin(hash_gram)  # Convert text to binary
        bin_len = len(binary) - 2
        bin_str = "0" * (64 - bin_len) + binary[2:]   # Add the missing leading 0's to make all hashes 64 bit

        for i in range(64):
            if bin_str[i] == '1':
                fingerprint[i] += 1
            else:
                fingerprint[i] -= 1

    for i in range(64):
        if fingerprint[i] > 0:
            fingerprint[i] = 1
        else:
            fingerprint[i] = 0
    return fingerprint


def calculate_similarity_value(fingerprint_a: List[int], fingerprint_b: List[int]) -> float:
    differences = [1 for k in range(len(fingerprint_a)) if fingerprint_a[k] != fingerprint_b[k]]
    return 1 - (sum(differences) / len(fingerprint_a))


def orphan_likelihood_score_filter():
    age_weight = 0.1
    sim_weight = 0.9
    cutoff = 0.7

    min_year = get_earliest_year("")
    current_year = datetime.date.today().year

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
orphan_likelihood_score_filter()
