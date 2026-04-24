from typing import Literal

import keepassxc_protocol as kpxp
from pydantic import validate_call

from .backend.constants import ASSOCIATE_FILE
from .backend.utils import get_connection


@validate_call
def get_items(url: str, name: str | None = None) -> list[kpxp.Login]:
    connection = get_connection()

    if not connection.test_associate():
        raise Exception("Failed to load associates")

    items = connection.get_logins(url)

    if name:
        filtered_items: list[kpxp.Login] = []
        for item in items.entries:
            if item.name == name:
                filtered_items.append(item)
        return filtered_items

    return items.entries


@validate_call
def get_value(
        url: str,
        value: Literal["password", "login", "totp", "name"],
        name: str | None = None,
) -> str:
    items = get_items(url, name)

    if len(items) > 1:
        raise Exception("Found more than one item with this url. Try specifying a name.")

    if len(items) == 0:
        raise Exception("No items found.")

    return getattr(items[0], value)


def associate() -> None:
    connection = get_connection()
    connection.associate()
    associates_json = connection.dump_associate_json()
    ASSOCIATE_FILE.write_text(associates_json, encoding="utf-8")


@validate_call
def delete_association(
    db_hash: str | None = None,
    all_: bool = False,
    id_: str | None = None,
    current: bool = False,
) -> None:

    if current:
        connection = get_connection()
        db_hash = connection.get_databasehash().hash
        try:
            connection.session.associates.delete_by_hash(db_hash)
            associates_json = connection.dump_associate_json()
            ASSOCIATE_FILE.write_text(associates_json, encoding="utf-8")
        except KeyError:
            print(f"Association for current db not found.")
        return

    if all_:
        connection = get_connection()
        connection.session.associates.delete_all()
        associates_json = connection.dump_associate_json()
        ASSOCIATE_FILE.write_text(associates_json, encoding="utf-8")
        return

    if db_hash:
        connection = get_connection()
        connection.session.associates.delete_by_hash(db_hash)
        associates_json = connection.dump_associate_json()
        ASSOCIATE_FILE.write_text(associates_json, encoding="utf-8")
        return

    if id_:
        connection = get_connection()
        associates = connection.session.associates
        target: str | None = None
        for key, value in associates.entries.items():
            if value.id == id_:
                target = key
                break

        if target:
            associates.delete_by_hash(target)
        return
