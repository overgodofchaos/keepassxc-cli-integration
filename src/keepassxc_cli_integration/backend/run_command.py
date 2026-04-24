import subprocess

from .string_query import find_query, resolve_query


def run(command: list[str]) -> None:
    program = command[0]
    args = command[1:]

    args = [
        arg.replace(x, resolve_query(x)) if (x := find_query(arg)) else arg
        for arg in args
    ]

    subprocess.run(  # noqa: PLW1510
        [program, *args],
    )
