from .modules import *


class CmdArgs:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.subparsers = self.parser.add_subparsers(
            help="get: Get value from kpx.\n"
                 "accosiate: Associate with current active BD or delete association.",
            dest="mode"
        )

        self.get = CmdArgsGet(self.subparsers)
        self.associate = CmdArgsAssociate(self.subparsers)

    @classmethod
    def get_args(cls) -> argparse.Namespace:
        cmdargs = cls()
        return cmdargs.parser.parse_args()


class CmdArgsGet:
    def __init__(self, subparsers):
        name_ = "get"
        help_ = "get value from kpx"

        parser: argparse.ArgumentParser = subparsers.add_parser(name_, help=help_)

        parser.add_argument(
            "value",
            choices=["login", "password",
                     "l", "p"],
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


class CmdArgsAssociate:
    def __init__(self, subparsers):
        name_ = "associate"
        help_ = "Associate with current active BD"

        parser: argparse.ArgumentParser = subparsers.add_parser(name_, help=help_)

        parser.add_argument(
            "command",
            type=str,
            choices=["add", "delete", "show"],
            nargs="?",
            default="add",
        )

        parser.add_argument(
            "select",
            type=str,
            help='For delete command. "current" or "all" or associate name. Default is "current".',
            nargs="?",
            default="current"
        )

        # group = parser.add_mutually_exclusive_group()
        #
        # group.add_argument(
        #     "-D", "--delete",
        #     help='delete association by id. Current active if specified "current" or ""',
        #     required=False,
        #     type=str,
        #     default=None
        # )
        #
        # group.add_argument(
        #     "-C", "--clear",
        #     help="clear all saved associations",
        #     action="store_true"
        # )
        #
        # group.add_argument(
        #     "-S", "--show",
        #     help="show all saved associations",
        #     action="store_true"
        # )

