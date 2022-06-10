from typing import Tuple, List

from bs4 import BeautifulSoup

from orphan_detection import util
from orphan_detection import constants


def check_redirect(page_content: str | bytes) -> Tuple[bool, str | None]:
    meta_tags = BeautifulSoup(page_content, constants.HTML_PARSER_CONFIG).find_all("meta", content=True)
    for tag in meta_tags:
        if "http-equiv=\"refresh\"" in str(tag).lower() and "url=" in str(tag).lower():
            return True, tag["content"].lower().split("url=")[1].split("\"")[0]
    return False, None


def check_frames(page_content: str | bytes) -> Tuple[bool, List[str] | None]:
    links = []
    for keyword in constants.FRAME_TAGS:
        frames = BeautifulSoup(page_content, constants.HTML_PARSER_CONFIG).find_all(keyword, src=True)
        for frame in frames:
            links.append(frame["src"])
    if not links:
        return False, None
    return True, links


def solve_link(url: str) -> Tuple[int, str]:
    response = util.download_page_content(url, bytes_content=False, allow_redirects=True)
    if response.error_msg:
        return 0, f"[ERROR   RESPONSE] [LINKED URL] [{response.error_msg}] {url}"
    if response.content_header is not None or "text/html" not in response.content_header:
        return 0, f"[INVALID RESPONSE] [LINKED URL] [{response.error_msg}] {url}"
    code, result = check_page(response.content, url)
    return code, f"{result} {url}"


def check_copyright(page_content: str) -> Tuple[bool, int | None]:
    keyword_indices = []
    for keyword in constants.COPYRIGHT_KEYWORDS:
        try:
            index_keyword = page_content.index(keyword)
            keyword_indices.append((index_keyword, index_keyword + len(keyword)))
        except ValueError:
            pass

    if not keyword_indices:
        return False, None

    potential_copyright = ""
    for keyword_index in keyword_indices:
        potential_copyright += page_content[-50 + keyword_index[0]: keyword_index[1] + 50]

    potential_years = list(map(int, util.identify_numbers(potential_copyright)))
    if not potential_years:
        return False, None
    current_year = util.get_current_year()
    latest_year_found = max({year for year in potential_years if year <= current_year})

    return current_year != latest_year_found, latest_year_found


def check_potential_redirect(content: str) -> Tuple[bool, str | None]:
    keyword_founds = [keyword.lower() in content for keyword in constants.REDIRECT_KEYWORDS]
    if not any(keyword_founds):
        return False, None
    return True, constants.REDIRECT_KEYWORDS[keyword_founds.index(True)]


def check_error_page(content: str) -> Tuple[bool, str | None]:
    keyword_founds = [keyword.lower() in content for keyword in constants.NOT_FOUND_KEYWORDS]
    if not any(keyword_founds):
        return False, None
    return True, constants.NOT_FOUND_KEYWORDS[keyword_founds.index(True)]


def check_expired_page(content: str) -> Tuple[bool, str | None]:
    keyword_founds = [keyword.lower() in content for keyword in constants.EXPIRED_KEYWORDS]
    if not any(keyword_founds):
        return False, None
    return True, constants.EXPIRED_KEYWORDS[keyword_founds.index(True)]


def check_boiler_plate(content: str) -> Tuple[bool, int | None]:
    word_list = util.identify_words(content)
    return len(word_list) < 5, len(word_list)


def check_page(content: str | bytes, url: str) -> Tuple[int, List[str]]:
    response = []
    cleaned_content = util.remove_html_tags(content).lower()

    found_marker, link_redirect = check_redirect(content)
    if found_marker:
        if link_redirect.startswith('/'):
            code, msg = solve_link(url + link_redirect)
        else:
            code, msg = solve_link(link_redirect)
        return code, [msg]

    found_marker, links = check_frames(content)
    if found_marker:
        for link in links:
            if link.startswith('/'):
                _, msg = solve_link(url + link)
            else:
                _, msg = solve_link(link)
            response.append(msg)

    # check for copyright marker
    found_marker, year = check_copyright(cleaned_content)
    if found_marker:
        return 1, response + [f"[OLD COPYRIGHT DATE] Latest Copyright from year {year}."]
    if year:
        return -1,  response + [f"[NEW COPYRIGHT DATE] Latest Copyright from year {year}."]

    found_marker, keyword = check_potential_redirect(str(content))
    if found_marker:
        return 0,  response + [f"[POTENTIAL REDIRECT] found keyword {keyword} on page."]

    # check for error page markers
    found_marker, keyword = check_error_page(cleaned_content)
    if found_marker:
        return 1,  response + [f"[CUSTOM ERROR PAGE] found keyword {keyword} on page."]

    # check for expired page marker
    found_marker, keyword = check_expired_page(cleaned_content)
    if found_marker:
        return 1,  response + [f"[EXPIRED PAGE] found keyword {keyword} on page."]

    content_without_scripts = util.remove_html_sections(content, "scripts")
    found_marker, amount_words = check_boiler_plate(util.remove_html_tags(content_without_scripts))
    if found_marker:
        return 1,  response + [f"[BOILERPLATE PAGE] Identified page as boilerplate with only {amount_words} words."]

    return 0,  response + ["[UNDECIDED] Unknown status, no indicators found"]
