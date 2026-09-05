import pytest
from typer.testing import CliRunner

from src.keepassxc_cli_integration.kpx_cmd import app

runner = CliRunner()


def test_get_password() -> None:
    result = runner.invoke(app, ["get", "password", "https://example.com"])
    assert result.exit_code == 0
    assert result.output.strip() == "asdfsdafasdf"


def test_get_login() -> None:
    result = runner.invoke(app, ["get", "login", "https://example.com"])
    assert result.exit_code == 0
    assert result.output.strip() == "sadf"


def test_get_name() -> None:
    result = runner.invoke(app, ["get", "name", "https://example.com"])
    assert result.exit_code == 0
    assert result.output.strip() == "testentry1"


def test_get_totp() -> None:
    result = runner.invoke(app, ["get", "totp", "https://example.com"])
    assert result.exit_code == 0
    assert result.output.strip().isdecimal()


def test_get_password_multiple_entries_error(capsys: pytest.CaptureFixture[str]) -> None:
    result = runner.invoke(app, ["get", "password", "https://example9.com"])
    assert result.exit_code == 1
    assert "Found more than one item with this url." in result.exception.__str__()


def test_get_password_multiple_entries() -> None:
    result = runner.invoke(app, ["get", "password", "https://example9.com", "--name", "testmuent1"])
    assert result.exit_code == 0
    assert result.output.strip() == "asdfsdafasdf"
