from keepassxc_cli_integration.backend.modules import *
from keepassxc_cli_integration.backend import dep
from keepassxc_cli_integration.backend.queries import get_item


def main():
    if dep.args.mode == "get":
        url = dep.args.url
        value = dep.args.value
        name = dep.args.name

        value = get_item(url, value, name)

        print(value)


if __name__ == '__main__':
    main()