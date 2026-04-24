import os
import re
import sys
from typing import Annotated, Literal

import typer

from keepassxc_cli_integration import kpx
from keepassxc_cli_integration.backend import run_command
from keepassxc_cli_integration.backend.constants import ASSOCIATE_FILE

from .backend.string_query import find_query, resolve_query


def debug() -> bool:
    return bool(os.environ.get("KPX_CLI_DEBUG"))


app = typer.Typer(
    name="KeepassXC-CLI-Integration",
    help="Getting data from a running KeepassXC-GUI instance.",
    add_completion=False,
    no_args_is_help=True,
)


@app.callback()
def base_options(
        debug_: Annotated[
            bool,
            typer.Option("--debug/--no-debug", help="Debug mode.")] = False,
        envs: Annotated[
            list[str] | None,
            typer.Option("--env", help="Env in format ENV_NAME=env_value. Can multiple entries")] = None,
) -> None:
    if debug_:
        os.environ["KPX_CLI_DEBUG"] = "true"
        os.environ["KPX_PROTOCOL_DEBUG"] = "true"

    if envs:
        for env in envs:
            match = re.fullmatch(r".+=.+", env)
            if not match:
                raise SystemError(f"Incorrect env format: {env}")

            key, value = env.split("=", 1)
            value = resolve_query(x) if (x := find_query(value)) else value

            os.environ[key] = value


@app.command(
    help="Get value from kpx. "
         "To search for values in ALL open databases, "
         "you need to associate with each database.",
)
def get(
        value: Annotated[
            Literal["password", "login", "totp", "name"],
            typer.Argument(help="Select value: login, password")],
        url: Annotated[
            str,
            typer.Argument(help="URL for item in keepassxc. Can be specified without http(s)://")],
        name: Annotated[
            str | None,
            typer.Option(help="Name of item (requred if one url has several items)")] = None,
) -> None:
    try:
        result = kpx.get_value(url, value, name)
    except Exception as e:  # noqa: BLE001
        print(e)
        return

    print(result)


@app.command(help="", context_settings={"ignore_unknown_options": True})
def run(command: Annotated[list[str], typer.Argument(help="List of commands to run.")]) -> None:
    run_command.run(command)


associate_app = typer.Typer(
    help="Associate with current active BD. Association management. (Default: add)",
    no_args_is_help=False,
)
app.add_typer(associate_app, name="associate")


@associate_app.command(
    help="Add current active DB to associaties",
)
def add() -> None:
    kpx.associate()


@associate_app.callback(invoke_without_command=True)
def associate_default(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is None:
        add()


@associate_app.command(
    help="Delete DB from associaties. (Default: current)",
)
def delete(
        select: Annotated[str, typer.Argument(help="Accosiate name or 'current' or 'all'")] = "current",
) -> None:
    match select:
        case "current":
            kpx.delete_association(current=True)
        case "all":
            kpx.delete_association(all_=True)
        case _:
            kpx.delete_association(id_=select)


@associate_app.command(
    help="Show all associaties",
)
def show() -> None:
    associates_json = ASSOCIATE_FILE.read_text(encoding="utf-8")
    print(associates_json)


def main() -> None:
    try:
        app()
    except Exception as e:
        if os.environ.get("KPX_CLI_DEBUG") == "true":
            raise
        print(f"{type(e).__name__}: {e}")
        sys.exit(1)