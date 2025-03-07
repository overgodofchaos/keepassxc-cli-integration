from kpx.backend.modules import *


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


def read_toml(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return toml.load(f)


def escape_for_bat(s: str) -> str:
    s = re.sub(r'([&|<>^%!"(){}])', r'^\1', s)

    return s