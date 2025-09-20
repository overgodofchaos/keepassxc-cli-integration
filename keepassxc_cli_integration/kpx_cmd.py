import os
import sys
from enum import StrEnum
from typing import Annotated

import typer

from keepassxc_cli_integration import kpx
from keepassxc_cli_integration.backend import autorization, run_command, utils

app = typer.Typer(
    name="KeepassXC-CLI-Integration",
    help="Getting data from a running KeepassXC-GUI instance.",
    add_completion=False,
    no_args_is_help=True
)


class Value(StrEnum):
    password = "password"
    login = "login"


@app.command(
    help="Get value from kpx. "
         "To search for values in ALL open databases, "
         "you need to associate with each database."
)
def get(
        value: Annotated[Value, typer.Argument(help="Select value: login, password")],
        url: Annotated[str, typer.Argument(help="URL for item in keepassxc. "
                                                "Can be specified without http(s)://")],
        name: Annotated[str | None, typer.Option(help="Name of item (requred if one url has several items)")] = None,
        bat: Annotated[bool, typer.Option(help="Escape answer for .bat scripts")] = False,
) -> None:
    try:
        result = kpx.get_value(url, value.name, name)
    except Exception as e:
        print(e)
        return

    if bat:
        print(utils.escape_for_bat(result))
        return

    print(result)


@app.command(help="", context_settings={"ignore_unknown_options": True})
def run(command: Annotated[list[str], typer.Argument(..., help="List of commands to run.")]) -> None:
    run_command.run(command)


associate_app = typer.Typer(
    help="Associate with current active BD. Association management. (Default: add)",
    no_args_is_help=False
)
app.add_typer(associate_app, name="associate")


@associate_app.command(
    help="Add current active DB to associaties"
)
def add() -> None:
    kpx.associate()


@associate_app.callback(invoke_without_command=True)
def associate_default() -> None:
    add()


@associate_app.command(
    help="Delete DB from associaties. (Default: current)"
)
def delete(
        select: Annotated[str, typer.Argument(help="Accosiate name or 'current' or 'all'")] = "current"
) -> None:
    match select:
        case "current":
            kpx.delete_association(current=True)
        case "all":
            kpx.delete_association(all_=True)
        case _:
            kpx.delete_association(id_=select)


@associate_app.command(
    help="Show all associaties"
)
def show() -> None:
    print(autorization.read_settings_text())




def main() -> None:
    try:
        app()
    except Exception as e:
        if os.environ.get("KPX_DEBUG") == "true":
            raise e
        else:
            print(f"{type(e).__name__}: {e}")
            sys.exit(1)