from dataclasses import dataclass


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
