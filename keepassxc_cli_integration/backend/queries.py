from . import kpx_protocol, settings


def get_item(url: str,  # noqa: C901
             mode: str = "password",
             name: str | None = None) -> str:

    if url.startswith("https://") is False \
            and url.startswith("http://") is False:
        url = f"https://{url}"

    connection = kpx_protocol.Connection()
    connection.connect()
    associates = settings.read_settings().associates
    connection.load_associates(associates)
    connection.test_associate()

    items = connection.get_logins(url)

    item = None

    if len(items) == 1:
        item = items[0]

    if len(items) > 1:
        if name is None:
            print(items)
            names = [item.name if item.name != '' else "NONAME"
                     for item in items]
            names = [f"{i+1}. {names[i]}" for i in range(len(names))]
            print(names)
            names = "\n".join(names)
            raise SystemError(f"Item {url} has multiple entries. Name required.\n"
                              f"Found names:\n"
                              f"{names}")

        for item_ in items:
            if item_.name == name:
                item = item_
                break

    if len(items) == 0 or item is None:
        raise SystemError(f"Item {url} not found")

    match mode:
        case "login":
            return item.login
        case "password":
            return item.password
        case _:
            raise SystemError(f"Unknown mode {mode}")