import re

from ..kpx import get_value


def find_query(arg: str) -> str | None:
    pattern = r"(@kpx::[^:]*::(password|login)(::[^!]+)?@kpx)"

    match = re.search(pattern, arg)

    if match:
        query = match.group(0)
        return query
    else:
        return None


def resolve_query(query: str) -> str:
    query = (query
             .removeprefix("@kpx").removesuffix("@kpx")
             .removeprefix("::").removesuffix("::")
             .replace("kpx::", "").split("::"))
    url = query[0]
    item = query[1]
    name = None if len(query) == 2 else query[2]

    return get_value(url, item, name)