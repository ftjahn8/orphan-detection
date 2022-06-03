from typing import Tuple, List

import requests
from orphan_detection import constants

__all__ = ["download_web_archive_data", "probe_url"]


def download_web_archive_data(domain: str) -> List[str]:
    response = requests.get(constants.WEB_ARCHIV_BASE_URL.format(DOMAIN=domain))
    response.raise_for_status()
    response_lines = response.text.splitlines()
    return response_lines


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
