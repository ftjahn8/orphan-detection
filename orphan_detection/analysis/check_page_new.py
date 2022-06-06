from typing import Tuple

from orphan_detection import util

copyright_keywords = ["copyright", "&copy", "&#169", chr(169)]
not_found_keywords = ["404 Not Found", "404 Error", "Page Not Found"]
expired_keywords = ["If you are the owner of this", "Domain expired", "website has been suspended"]


def check_copyright(page_content: str) -> Tuple[bool, int | None]:
    keyword_indices = []
    for keyword in copyright_keywords:
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

    potential_years = list(map(int, util.identify_words(potential_copyright)))
    if not potential_years:
        return False, None
    current_year = util.get_current_year()
    latest_year_found = max({year for year in potential_years if year <= current_year})

    return current_year != latest_year_found, latest_year_found


def check_error_page(content: str) -> Tuple[bool, str | None]:
    keyword_founds = [keyword.lower() in content for keyword in not_found_keywords]
    if not any(keyword_founds):
        return False, None
    return True, not_found_keywords[keyword_founds.index(True)]


def check_expired_page(content: str) -> Tuple[bool, str | None]:
    keyword_founds = [keyword.lower() in content for keyword in expired_keywords]
    if not any(keyword_founds):
        return False, None
    return True, expired_keywords[keyword_founds.index(True)]


def check_boiler_plate(content: str) -> Tuple[bool, int | None]:
    word_list = util.identify_words(content)
    return len(word_list) < 5, len(word_list)


def check_page(content: bytes, url: str) -> Tuple[int, str]:
    cleaned_content = util.remove_html_tags(content).lower()

    # check for copyright marker
    found_marker, year = check_copyright(cleaned_content)
    if found_marker:
        return 1, f"[OLD COPYRIGHT DATE] Latest Copyright from year {year}."
    if year:
        return -1, f"[NEW COPYRIGHT DATE] Latest Copyright from year {year}."

    # check for error page markers
    found_marker, keyword = check_error_page(cleaned_content)
    if found_marker:
        return 1, f"[CUSTOM ERROR PAGE] found keyword {keyword} on page."

    # check for expired page marker
    found_marker, keyword = check_expired_page(cleaned_content)
    if found_marker:
        return 1, f"[EXPIRED PAGE] found keyword {keyword} on page."

    content_without_scripts = util.remove_html_sections(content, "scripts")
    found_marker, amount_words = check_boiler_plate(util.remove_html_tags(content_without_scripts))
    if found_marker:
        return 1, f"[BOILERPLATE PAGE] Identified page as boilerplate page with only {amount_words} words on it."


def main():
    candidates = util.read_lines_from_file("..\\Data\\tmp\\hm.edu\\hm.edu_after_orphan_score_filter")
    for line in candidates:
        url = line.split(" ")[0]
        hash_name_current = util.get_md5_hash(url)
        with open(f"..\\Data\\tmp\\pages\\{hash_name_current}", "rb") as outfile:
            content = outfile.read()
        print(check_page(content, url), url, hash_name_current)

main()
