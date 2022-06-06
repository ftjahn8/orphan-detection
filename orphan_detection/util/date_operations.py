
import datetime


__all__ = ["get_current_year", "get_date", "parse_year_argument", "get_default_current_sitemap_filter"]


def get_current_year() -> int:
    return datetime.date.today().year


def get_date() -> str:
    return datetime.datetime.today().strftime("%Y-%m-%d")


def parse_year_argument(arg_value: str) -> datetime.date | None:
    split_value = arg_value.split("-")
    match len(split_value):
        case 3:
            try:
                return datetime.date(int(split_value[0]), int(split_value[1]), int(split_value[2]))
            except ValueError:
                return None
        case 2:
            try:
                return datetime.date(int(split_value[0]), int(split_value[1]), 1)
            except ValueError:
                return None
        case 1:
            try:
                return datetime.date(int(split_value[0]), 1, 1)
            except ValueError:
                return None
    return None


def get_default_current_sitemap_filter() -> datetime.date:
    return datetime.date(get_current_year(), 1, 1)