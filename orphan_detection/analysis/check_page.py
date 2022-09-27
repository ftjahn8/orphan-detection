"""This file contains all functions for the check page step in the analysis chain."""
from typing import Tuple, List

from bs4 import BeautifulSoup

from orphan_detection import util
from orphan_detection import constants


def check_redirect(page_content: str | bytes) -> Tuple[bool, str | None]:
    """
    Identify potential redirects in page content.
    :param page_content: content of the page in its current form
    :return: (True, target of redirect) if a redirect is found, otherwise (False, None)
    """
    meta_tags = BeautifulSoup(page_content, constants.HTML_PARSER_CONFIG).find_all("meta", content=True)
    for tag in meta_tags:
        if "http-equiv=\"refresh\"" in str(tag).lower() and "url=" in str(tag).lower():
            return True, tag["content"].lower().split("url=")[1].split("\"")[0]
    return False, None


def check_frames(page_content: str | bytes) -> Tuple[bool, List[str] | None]:
    """
    Identify links in frames in page content.
    :param page_content: content of the page in its current form
    :return: (True, list of frame links) if frames with links are found, otherwise (False, None)
    """
    links = []
    for keyword in constants.FRAME_TAGS:
        frames = BeautifulSoup(page_content, constants.HTML_PARSER_CONFIG).find_all(keyword, src=True)
        for frame in frames:
            links.append(frame["src"])
    if not links:
        return False, None
    return True, links


def solve_link(url: str, redirects: int) -> Tuple[int, str]:
    """
    Recursively solve an identified frame or redirect link.
    :param url: url to solve
    :param redirects: redirects left to follow
    :return: Tuple of classification value and identified markers in the link
    """
    # download linked page
    response = util.download_page_content(url, bytes_content=False, allow_redirects=True)
    if response.error_msg:
        return 0, f"[ERROR   RESPONSE] [LINKED URL] [{response.error_msg}] {url}"
    if response.content_header is not None or "text/html" not in response.content_header:
        return 0, f"[INVALID RESPONSE] [LINKED URL] [{response.error_msg}] {url}"

    # analyse page
    code, result = check_page(response.content, url, redirects=redirects)
    return code, f"{result} {url}"


def check_copyright(page_content: str) -> Tuple[bool, int | None]:
    """
    Identify the copyright year in the page if it exists.
    :param page_content: content of the page in its current form
    :return: (True, copyright year) if a valid copyright year is found, otherwise (False, None)
    """
    keyword_indices = []
    for keyword in constants.COPYRIGHT_KEYWORDS:
        try:
            index_keyword = page_content.index(keyword)
            keyword_indices.append((index_keyword, index_keyword + len(keyword)))
        except ValueError:
            pass

    if not keyword_indices:
        return False, None

    # identify potential copyright phrases
    potential_copyright = ""
    for keyword_index in keyword_indices:
        potential_copyright += page_content[-50 + keyword_index[0]: keyword_index[1] + 50]

    # identify valid copyright years
    potential_years = list(map(int, util.identify_numbers(potential_copyright)))
    current_year = util.get_current_year()
    potential_years_cleaned = {year for year in potential_years if 1970 <= year <= current_year}
    if not potential_years_cleaned:
        return False, None

    latest_year_found = max(potential_years_cleaned)
    return current_year != latest_year_found, latest_year_found


def check_potential_redirect(content: str) -> Tuple[bool, str | None]:
    """
    Check for redirect marker.
    :param content: content of the page in its current form
    :return: (True, redirect keyword) if a redirect keyword is identified, otherwise (False, None)
    """
    keyword_founds = [keyword.lower() in content for keyword in constants.REDIRECT_KEYWORDS]
    if not any(keyword_founds):
        return False, None
    return True, constants.REDIRECT_KEYWORDS[keyword_founds.index(True)]


def check_error_page(content: str) -> Tuple[bool, str | None]:
    """
    Check for error page marker.
    :param content: content of the page in its current form
    :return: (True, error page keyword) if an error page keyword is identified, otherwise (False, None)
    """
    keyword_founds = [keyword.lower() in content for keyword in constants.NOT_FOUND_KEYWORDS]
    if not any(keyword_founds):
        return False, None
    return True, constants.NOT_FOUND_KEYWORDS[keyword_founds.index(True)]


def check_expired_page(content: str) -> Tuple[bool, str | None]:
    """
    Check for expired marker.
    :param content: content of the page in its current form
    :return: (True, expired keyword) if an expired keyword is identified, otherwise (False, None)
    """
    keyword_founds = [keyword.lower() in content for keyword in constants.EXPIRED_KEYWORDS]
    if not any(keyword_founds):
        return False, None
    return True, constants.EXPIRED_KEYWORDS[keyword_founds.index(True)]


def check_boiler_plate(content: str) -> Tuple[bool, int | None]:
    """
    Check for boilerplate code on page.
    :param content: content of the page in its current form
    :return: (True, amount of words) if less than five words are found in the page, otherwise (False, amount of words)
    """
    word_list = util.identify_words(content)
    return len(word_list) < 5, len(word_list)


def check_page(content: str | bytes, url: str, redirects: int = 20) -> Tuple[int, List[str]]:
    """
    Check page for hints of its orphan status. Returns a classification and list of reasons for it.
    :param content: content of page in its current form
    :param url: url of page
    :param redirects: amount of redirects left to be followed
    :return: Tuple with classification value and list of identified markers
    """
    if redirects == 0:
        return 0, [f"[TOO MANY REDIRECTS] for {url}"]
    response_code = 0
    response = []
    cleaned_content = util.remove_html_tags(content).lower()

    # find redirects
    found_marker, link_redirect = check_redirect(content)
    if found_marker:
        if link_redirect.startswith('/'):
            code, msg = solve_link(url + link_redirect, redirects - 1)
        else:
            code, msg = solve_link(link_redirect, redirects - 1)
        return code, [msg]

    # find frame with links
    found_marker, links = check_frames(content)
    if found_marker:
        for link in links:
            if link.startswith('/'):
                _, msg = solve_link(url + link, redirects - 1)
            else:
                _, msg = solve_link(link, redirects - 1)
            response.append(msg)

    # check for copyright marker
    found_marker, year = check_copyright(cleaned_content)
    if found_marker:
        response_code = 1
        response.append(f"[OLD COPYRIGHT DATE] Latest Copyright from year {year}.")
    if not found_marker and year:
        return -1,  response + [f"[NEW COPYRIGHT DATE] Latest Copyright from year {year}."]

    # check for redirect marker
    found_marker, keyword = check_potential_redirect(str(content))
    if found_marker:
        response.append(f"[POTENTIAL REDIRECT] found keyword {keyword} on page.")

    # check for error page markers
    found_marker, keyword = check_error_page(cleaned_content)
    if found_marker:
        response_code = 1
        response.append(f"[CUSTOM ERROR PAGE] found keyword {keyword} on page.")

    # check for expired page marker
    found_marker, keyword = check_expired_page(cleaned_content)
    if found_marker:
        response_code = 1
        response.append(f"[EXPIRED PAGE] found keyword {keyword} on page.")

    # check for boilerplate code
    content_without_scripts = util.get_content_without_tags(content, ["scripts"])
    found_marker, amount_words = check_boiler_plate(content_without_scripts)
    if found_marker:
        response_code = 1
        response.append(f"[BOILERPLATE PAGE] Identified page as boilerplate with only {amount_words} words.")

    if response_code == 0:
        return 0,  response + ["[UNDECIDED] Unknown status, no indicators found"]
    return response_code, response
