from .modules import *
from dataclasses import dataclass


class CmdArgs:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.subparsers = self.parser.add_subparsers(
            help="get: get item from kpx",
            dest="mode"
        )

        self.get = CmdArgsGet(
            self.subparsers.add_parser("get", help="get item from kpx"),
        )

    @classmethod
    def get_args(cls) -> Namespace:
        cmdargs = cls()
        return cmdargs.parser.parse_args()


class CmdArgsGet:
    def __init__(self, subparser):
        parser = subparser

        parser.add_argument(
            "item",
            choices=["login", "password", "both",
                     "l", "p", "b"],
            help="select item: login(l), password(p), both(b)"
        )

        parser.add_argument(
            "url",
            type=str,
            help="url for item in keepassxc"
        )

        parser.add_argument(
            "-N", "--name",
            type=str,
            required=False,
            help="name of item (requred if one url has several items)"
        )

        parser.add_argument(
            "-B", "--bat", "--cmd",
            action="store_true",
            required=False,
            help="escape answer for .bat scripts"
        )
