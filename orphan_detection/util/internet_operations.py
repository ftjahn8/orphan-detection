from typing import Tuple

import requests
from orphan_detection.util.data_objects import PageResponse

__all__ = ["probe_url", "download_page_content"]


def probe_url(url: str, timeout_after: float) -> Tuple[int, str | None]:
    try:
        response_for_url = requests.head(url, timeout=timeout_after)
        return response_for_url.status_code, None
    except requests.exceptions.Timeout:
        return 000, "Timeout"
    except requests.exceptions.SSLError as exc:
        return 000, f"[ERROR] SSLError: {exc}"
    except requests.exceptions.ConnectionError as exc:
        return 000, f"[ERROR] ConnectionError: {exc}"
    except Exception as exc:
        return 000, str(exc)


def download_page_content(url: str, bytes_content: bool = True, **kwargs) -> PageResponse:
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
    except Exception as exc:
        error_reason = str(exc)
    return PageResponse(error_msg=error_reason, content="", content_header=None, encoding=None)
