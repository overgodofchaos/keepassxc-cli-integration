from keepassxc_cli_integration import kpx
from keepassxc_cli_integration.backend import dep


def main():
    if dep.args.mode == "get":
        url = dep.args.url
        value = dep.args.value
        name = dep.args.name

        value = kpx.get_value(url, value, name)

        print(value)


if __name__ == '__main__':
    main()