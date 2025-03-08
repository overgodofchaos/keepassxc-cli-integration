from keepassxc_cli_integration.backend import kpx_protocol, autorization


def get_items(url: str, name: str = None) -> list[dict]:
    connection = kpx_protocol.Connection()
    connection.connect()
    associates = autorization.get_autorization_data()
    connection.load_associates(associates)

    if not connection.test_associate():
        raise Exception("Failed to load associates")

    items = connection.get_logins(url)

    if name is not None:
        items_ = []
        for item in items:
            if item["name"] == name:
                items_.append(item)
        items = items_

    return items


def get_value(url: str, value: str, name: str = None) -> str:
    items = get_items(url, name)

    if len(items) > 1:
        raise Exception("Found more than one item with this url. Try specifying a name.")

    if len(items) == 0:
        raise Exception("No items found.")

    return items[0][value]


def associate() -> None:
    autorization.get_autorization_data()


def delete_association(db_hash: str = None,
                       id_: str = None,
                       all_: bool = False,
                       current: bool = False) -> None:
    if current:
        autorization.delete_autorization_data(current=True)
        return

    if all_:
        autorization.delete_autorization_data(all_=True)
        return

    if id_:
        autorization.delete_autorization_data(id_=id_)
        return

    if db_hash:
        autorization.delete_autorization_data(db_hash=db_hash)
        return


if __name__ == "__main__":
    items_ = get_items("system-example")
    print(items_)
    value_ = get_value("system-example", "password", "")
    print(value_)
