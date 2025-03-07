from keepassxc_cli_integration.backend.modules import *
from keepassxc_cli_integration.backend import dep, autorization


def get_item(url: str,
             mode: str = "password",
             name: str = None):

    modes = {
        "password": "p",
        "login": "l",
        "both": "b"
    }

    if mode in modes:
        mode = modes[mode]

    if url.startswith("https://") is False \
            and url.startswith("http://") is False:
        url = f"https://{url}"

    connection = kpx_protocol.Connection()
    connection.connect()
    associates = autorization.get_autorization_data()
    connection.load_associate(associates)
    connection.test_associate()

    items = connection.get_logins(url)

    item = None

    if len(items) == 1:
        item = items[0]

    if len(items) > 1:
        if name is None:
            print(items)
            names = [item["name"] if item["name"] != '' else "NONAME"
                     for item in items]
            names = [f"{i+1}. {names[i]}" for i in range(len(names))]
            print(names)
            names = "\n".join(names)
            raise IOError(f"Item {url} has multiple entries. Name required.\n"
                          f"Found names:\n"
                          f"{names}")

        for item_ in items:
            if item_["name"] == name:
                item = item_
                break

    if len(items) == 0 or item is None:
        raise IOError(f"Item {url} not found")

    if mode == "l":
        return item["login"]
    elif mode == "p":
        return item["password"]
    elif mode == "b":
        return f"{item['login']};;;{item['password']}"