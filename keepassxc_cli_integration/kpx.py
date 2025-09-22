from typing import Literal

from keepassxc_cli_integration.backend import kpx_protocol
from keepassxc_cli_integration.backend.settings import Settings


def _get_connection() -> kpx_protocol.Connection:
    connection = kpx_protocol.Connection()
    connection.connect()
    associates = Settings.read().associates
    connection.load_associates(associates)
    return connection


def get_items(url: str, name: str | None = None) -> list[kpx_protocol.Login]:
    connection = _get_connection()

    if not connection.test_associate():
        raise Exception("Failed to load associates")

    items = connection.get_logins(url)

    if name is not None:
        items__ = []
        for item in items:
            if item.name == name:
                items__.append(item)
        items = items__

    return items


def get_value(url: str, value: str, name: str | None = None) -> str:
    items = get_items(url, name)

    if len(items) > 1:
        raise Exception("Found more than one item with this url. Try specifying a name.")

    if len(items) == 0:
        raise Exception("No items found.")

    return getattr(items[0], value)


def associate() -> None:
    connection = _get_connection()
    connection.associate()
    associates = connection.dump_associate()
    settings = Settings.read()
    settings.associates = associates
    settings.write()



def delete_association(
    db_hash: str | None = None, id_: str | None = None, all_: bool = False, current: bool = False
) -> None:
    settings = Settings.read()

    if current:
        connection = _get_connection()
        db_hash = connection.get_databasehash().hash
        try:
            settings.associates.delete_by_hash(db_hash)
            settings.write()
        except KeyError:
            print(f"Association for current db not found.")
        return

    if all_:
        settings.associates.delete_all()
        settings.write()
        return

    if db_hash:
        settings.associates.delete_by_hash(db_hash)
        settings.write()
        return


if __name__ == "__main__":
    items_ = get_items("system-example")
    print(items_)
    value_ = get_value("system-example", "password", "")
    print(value_)
    value_ = get_value("test_url", "password", None)
    print(value_)
