"""This file contains both helper functions related with internet/ http requests."""
from typing import Tuple

import requests
from orphan_detection.util.data_objects import PageResponse

__all__ = ["probe_url", "download_page_content"]


def probe_url(url: str, timeout_after: float) -> Tuple[int, str | None]:
    """Makes an HTTP-Head-Request for given url and returns its status code and None if successful.
    In case of an error occurred it returns 0 and the error reason."""
    try:
        response_for_url = requests.head(url, timeout=timeout_after)
        return response_for_url.status_code, None
    except requests.exceptions.Timeout:
        return 000, "Timeout"
    except requests.exceptions.SSLError as exc:
        return 000, f"[ERROR] SSLError: {exc}"
    except requests.exceptions.ConnectionError as exc:
        return 000, f"[ERROR] ConnectionError: {exc}"
    except Exception as exc:  # pylint: disable-msg=broad-except
        return 000, str(exc)


def download_page_content(url: str, bytes_content: bool = True, **kwargs) -> PageResponse:
    """
    Downloads the content for given url in requested form and returns an
    util.PageResponse object with the collected data.
    :param url: url to download the content for
    :param bytes_content: flag to return the content in bytes form
    :param kwargs:
    :return: util.PageResponse with data about content, content-header, encoding and errors if occurred.
    """
    try:
        response = requests.get(url, **kwargs)
        page_content = response.text if not bytes_content else response.content
        return PageResponse(error_msg=None, content=page_content,
                            content_header=response.headers.get("Content-Type"), encoding=response.encoding)
    except requests.exceptions.Timeout:
        error_reason = "Timeout"
    except requests.exceptions.SSLError:
        error_reason = "SSLError"
    except requests.exceptions.ConnectionError:
        error_reason = "ConnectionError"
    except Exception as exc:  # pylint: disable-msg=broad-except
        error_reason = str(exc)
    return PageResponse(error_msg=error_reason, content="", content_header=None, encoding=None)
