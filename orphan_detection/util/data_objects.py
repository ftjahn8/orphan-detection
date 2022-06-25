"""This file contains the definition of all helper data classes."""
from dataclasses import dataclass

__all__ = ["DUDEParameters", "ProbeParameters", "OrphanScoreParameters", "PageResponse", "SizeFilterParameters",
           "ContentDownloadParameters"]


@dataclass(frozen=True, slots=True)
class DUDEParameters:
    """Data Carrier class for dude filter parameters."""
    popularity_cutoff: float
    short_prefix_cutoff: float
    large_link_len_threshold: int
    large_link_count: int
    pc_value_threshold: float | int


@dataclass(frozen=True, slots=True)
class ProbeParameters:
    """Data Carrier class for probe parameters."""
    timeout: float | int
    interval: float | int


@dataclass(frozen=True, slots=True)
class OrphanScoreParameters:
    """Data Carrier class for orphan score parameters."""
    age_weight: float
    similarity_weight: float
    cutoff_value: float


@dataclass(frozen=True, slots=True)
class SizeFilterParameters:
    """Data Carrier class for size filter parameters."""
    epsilon: float | int
    min_amount_same_size: int


@dataclass(frozen=True, slots=True)
class ContentDownloadParameters:
    """Data Carrier class for download parameters."""
    timeout: None | float
    interval: float


@dataclass(frozen=True, slots=True)
class PageResponse:
    """Data Carrier class for the result of a single download request."""
    error_msg: None | str
    content: bytes | str
    content_header: None | str
    encoding: None | str
