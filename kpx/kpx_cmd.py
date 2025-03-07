from kpx.backend.modules import *
from kpx.backend import dep
from kpx.backend.queries import get_item


def main():
    if dep.args.mode == "get":
        url = dep.args.url
        value = dep.args.value
        name = dep.args.name

        value = get_item(url, value, name)

        print(value)


if __name__ == '__main__':
    main()