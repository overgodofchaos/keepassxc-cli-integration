from keepassxc_cli_integration import kpx
from keepassxc_cli_integration.backend import utils, autorization
import typer
from typing import Literal
from enum import Enum

app = typer.Typer(
    name="KeepassXC-CLI-Integration",
    help="Getting data from a running KeepassXC-GUI instance.",
    add_completion=False,
    no_args_is_help=True,
)


class Value(str, Enum):
    password = "password"
    login = "login"


@app.command(
    help="Get value from kpx. To search for values in ALL open databases, you need to associate with each database."
)
def get(
        value: Value = typer.Argument(
            ...,
            help="Select value: login, password"),

        url: str = typer.Argument(
            ...,
            help="URL for item in keepassxc. Can be specified without http(s)://"),

        name: str = typer.Option(
            None,
            help="Name of item (requred if one url has several items)"),

        bat: bool = typer.Option(
            False,
            help="Escape answer for .bat scripts")
):
    try:
        result = kpx.get_value(url, value.name, name)
    except Exception as e:
        print(e)
        return

    if bat:
        print(utils.escape_for_bat(result))
        return

    print(result)


associate_app = typer.Typer(
    help="Associate with current active BD. Association management. (Default: add)",
    no_args_is_help=False
)
app.add_typer(associate_app, name="associate")


@associate_app.command(
    help="Add current active DB to associaties"
)
def add():
    kpx.associate()


@associate_app.callback(invoke_without_command=True)
def associate_default():
    add()


@associate_app.command(
    help="Delete DB from associaties. (Default: current)"
)
def delete(
        select: str = typer.Argument(
            "current",
            help="Accosiate name or 'current' or 'all'")
):
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
def show():
    print(autorization.read_settings_text())


def main():
    app()
