import gzip
import os

from typing import List

from orphan_detection import constants

__all__ = ["create_directory", "is_file", "read_lines_from_file", "write_lines_to_file"]


def create_directory(path: str) -> None:
    if not os.path.exists(path):
        os.mkdir(path)


def is_file(path) -> bool:
    return os.path.exists(path) and os.path.isfile(path)


def save_to_file(path: str, content: str, user_restricted: bool = True) -> None:
    with open(path, 'w', encoding=constants.DEFAULT_ENCODING) as outfile:
        outfile.write(content)
    if user_restricted:
        os.chmod(path, constants.CHMOD_USER_ONLY_FILE)


def save_to_gzip_file(path: str, content: str, user_restricted: bool = True) -> None:
    with gzip.open(path, 'wb') as outfile:
        outfile.write(content.encode(constants.DEFAULT_ENCODING))

    if user_restricted:
        os.chmod(path, constants.CHMOD_USER_ONLY_FILE)


def read_from_file(path: str) -> str:
    with open(path, 'r', encoding=constants.DEFAULT_ENCODING) as infile:
        content = infile.read()
    return content


def read_from_gzip_file(path: str) -> str:
    with gzip.open(path, 'rb') as infile:
        content = infile.read()
    return content.decode(constants.DEFAULT_ENCODING)


def read_lines_from_file(path: str, zipped_file: bool = False) -> List[str]:
    if zipped_file:
        content = read_from_gzip_file(path)
    else:
        content = read_from_file(path)

    return content.splitlines()


def write_lines_to_file(path: str, content: List[str], zipped_file: bool = False, user_restricted: bool = True) -> None:
    content_combined = "\n".join(content)
    if zipped_file:
        save_to_gzip_file(path, content_combined, user_restricted)
    else:
        save_to_file(path, content_combined, user_restricted)
