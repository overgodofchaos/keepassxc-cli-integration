import os

from kpx.backend.modules import *
from kpx.backend import dep
from kpx.backend.queries import get_item


def main():
    if dep.args.mode == "get":
        url = dep.args.url
        item = dep.args.item
        name = dep.args.name

        item = get_item(url, item, name)

        print(item)


if __name__ == '__main__':
    main()