import subprocess

from .string_query import find_query, resolve_query


def run(command: list[str]) -> None:
    program = command[0]
    args = command[1:]

    args = [
        arg.replace(find_query(arg), resolve_query(find_query(arg))) if find_query(arg) else arg
        for arg in args
    ]

    subprocess.run(
        [program, *args]
    )
