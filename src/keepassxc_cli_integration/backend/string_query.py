import re

from ..kpx import get_value


def find_query(arg: str) -> str | None:
    pattern = r"(@kpx::[^:]*::(password|login)(::[^!]+)?@kpx)"

    match = re.search(pattern, arg)

    if match:
        return match.group(0)
    return None


def resolve_query(query: str) -> str:
    query_ = (query
              .removeprefix("@kpx").removesuffix("@kpx")
              .removeprefix("::").removesuffix("::")
              .replace("kpx::", "").split("::"))
    url = query_[0]
    item = query_[1]
    name = None if len(query_) == 2 else query_[2]  # noqa: PLR2004

    return get_value(url, item, name)
