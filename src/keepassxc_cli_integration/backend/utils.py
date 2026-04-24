import keepassxc_protocol as kpxp

from .constants import ASSOCIATE_FILE


def get_connection() -> kpxp.Connection:
    conn = kpxp.Connection()

    if ASSOCIATE_FILE.exists():
        associate_file_data: str = ASSOCIATE_FILE.read_text(encoding="utf-8")
        conn.load_associates_json(associate_file_data)

    return conn