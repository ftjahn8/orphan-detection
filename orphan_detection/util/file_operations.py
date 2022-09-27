"""This file contains all file related helper functions for the module."""
import gzip
import os
import shutil

from typing import List

from orphan_detection import constants

__all__ = ["create_directory", "is_file", "delete_directory",
           "save_to_bin_file", "read_from_bin_file", "read_lines_from_file", "write_lines_to_file"]


def create_directory(path: str) -> None:
    """Creates a directory at given path if it does not exist yet."""
    if not os.path.exists(path):
        os.mkdir(path)


def is_file(path: str) -> bool:
    """Returns True if given path leads to an existing file, otherwise returns False."""
    return os.path.exists(path) and os.path.isfile(path)


def save_to_bin_file(path: str, content: bytes, user_restricted: bool = True) -> None:
    """Saves given content in bytes form to given file path."""
    with open(path, 'wb') as outfile:
        outfile.write(content)
    if user_restricted:
        os.chmod(path, constants.CHMOD_USER_ONLY_FILE)


def save_to_file(path: str, content: str, user_restricted: bool = True) -> None:
    """Saves given content in text form to given file path."""
    with open(path, 'w', encoding=constants.DEFAULT_ENCODING) as outfile:
        outfile.write(content)
    if user_restricted:
        os.chmod(path, constants.CHMOD_USER_ONLY_FILE)


def save_to_gzip_file(path: str, content: str, user_restricted: bool = True) -> None:
    """Saves given content in compressed form to given file path."""
    with gzip.open(path, 'wb') as outfile:
        outfile.write(content.encode(constants.DEFAULT_ENCODING))

    if user_restricted:
        os.chmod(path, constants.CHMOD_USER_ONLY_FILE)


def read_from_bin_file(path: str) -> bytes:
    """Reads in the content from a binary file at given file path."""
    with open(path, 'rb') as infile:
        content = infile.read()
    return content


def read_from_file(path: str) -> str:
    """Reads in the content from a regular file at given file path."""
    with open(path, 'r', encoding=constants.DEFAULT_ENCODING) as infile:
        content = infile.read()
    return content


def read_from_gzip_file(path: str) -> str:
    """Reads in the content from a compressed file at given file path."""
    with gzip.open(path, 'rb') as infile:
        content = infile.read()
    return content.decode(constants.DEFAULT_ENCODING)


def read_lines_from_file(path: str, zipped_file: bool = False) -> List[str]:
    """Reads in the content from given path and return a list of single lines."""
    if zipped_file:
        content = read_from_gzip_file(path)
    else:
        content = read_from_file(path)
    return content.splitlines()


def write_lines_to_file(path: str, content: List[str], zipped_file: bool = False, user_restricted: bool = True) -> None:
    """Saves single lines to given path."""
    content_combined = "\n".join(content)
    if zipped_file:
        save_to_gzip_file(path, content_combined, user_restricted)
    else:
        save_to_file(path, content_combined, user_restricted)


def delete_directory(path: str):
    """Delete the directory from given path recursively."""
    shutil.rmtree(path, ignore_errors=True)
