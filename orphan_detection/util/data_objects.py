from dataclasses import dataclass

__all__ = ["DUDEParameters", "ProbeParameters", "OrphanScoreParameters", "PageResponse", "SizeFilterParameters",
           "ContentDownloadParameters"]


@dataclass(frozen=True, slots=True)
class DUDEParameters:
    popularity_cutoff: float
    short_prefix_cutoff: float
    large_link_len_threshold: int
    large_link_count: int
    pc_value_threshold: float | int


@dataclass(frozen=True, slots=True)
class ProbeParameters:
    timeout: float | int
    interval: float | int


@dataclass(frozen=True, slots=True)
class OrphanScoreParameters:
    age_weight: float
    similarity_weight: float
    cutoff_value: float


@dataclass(frozen=True, slots=True)
class SizeFilterParameters:
    epsilon: float | int
    min_amount_same_size: int


@dataclass(frozen=True, slots=True)
class ContentDownloadParameters:
    timeout: None | float
    interval: float


@dataclass(frozen=True, slots=True)
class PageResponse:
    error_msg: None | str
    content: bytes | str
    content_header: None | str
    encoding: None | str
