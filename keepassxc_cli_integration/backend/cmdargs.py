from .modules import *


class CmdArgs:
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description="KeepassXC-CLI-Integration. "
                        "Getting data from a running KeepassXC-GUI instance."
        )
        self.subparsers = self.parser.add_subparsers(
            help="Choise action.",
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
        help_ = "Get value from kpx. To search for values in ALL open databases, you need to associate with each database."

        parser: argparse.ArgumentParser = subparsers.add_parser(name_, help=help_)

        parser.add_argument(
            "value",
            choices=["login", "password",
                     "l", "p"],
            help="Select value: login(l), password(p), both(b)"
        )

        parser.add_argument(
            "url",
            type=str,
            help="URL for item in keepassxc. Can be specified without http(s)://"
        )

        parser.add_argument(
            "-N", "--name",
            type=str,
            required=False,
            help="Name of item (requred if one url has several items)"
        )

        parser.add_argument(
            "-B", "--bat", "--cmd",
            action="store_true",
            required=False,
            help="Escape answer for .bat scripts"
        )


class CmdArgsAssociate:
    def __init__(self, subparsers):
        name_ = "associate"
        help_ = "Associate with current active BD. Association management."

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


