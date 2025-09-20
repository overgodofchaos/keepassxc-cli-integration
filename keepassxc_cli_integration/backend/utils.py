import os
import re
from pathlib import Path

import toml


def write_toml(path: Path, data: dict) -> None:
    if path.exists():
        with open(path, "rb") as f:
            backup = f.read()
    else:
        backup = None

    try:
        with open(path, 'w', encoding="utf-8") as f:
            f.write(toml.dumps(data))
    except Exception as e:
        if backup:
            with open(path, "wb") as f:
                f.write(backup)
        else:
            os.remove(path)
        raise e


def read_toml(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return toml.load(f)


def read_text(path: Path) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def escape_for_bat(s: str) -> str:
    s = re.sub(r'([&|<>^%!"(){}])', r'^\1', s)

    return s
