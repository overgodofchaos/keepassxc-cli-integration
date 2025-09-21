# Refer to https://github.com/keepassxreboot/keepassxc-browser/blob/develop/keepassxc-protocol.md
import base64
import json
import os
import platform
import socket
from collections.abc import Buffer
from typing import Any

import nacl.utils
from nacl.public import Box, PrivateKey, PublicKey
from pydantic import ValidationError

from . import classes as k
from . import classes_requests as req
from . import classes_responses as resp
from . import errors
from .connection_config import ConnectionConfig
from .errors import ResponseUnsuccesfulException
from .winpipe import WinNamedPipe

if platform.system() == "Windows":
    import getpass

    import win32file


class Connection:
    def __init__(self) -> None:
        if platform.system() == "Windows":
            _socket = WinNamedPipe(win32file.GENERIC_READ | win32file.GENERIC_WRITE, win32file.OPEN_EXISTING)
        else:
            _socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

        self.config = ConnectionConfig(
            private_key=PrivateKey.generate(),
            nonce=nacl.utils.random(24),
            client_id=base64.b64encode(nacl.utils.random(24)).decode("utf-8"),
            socket=_socket,
            box=None,
            associates=None
        )

    @property
    def socket(self) -> WinNamedPipe | socket.socket:
        return self.config.socket

    def send(self,
             message: k.KPXProtocolRequest,
             path: tuple[Any, ...] | str | Buffer | None = None
             ) -> dict:

        if path is None:
            path = Connection.get_socket_path()

        message = message.to_bytes()
        self.socket.sendall(message)
        response = self.get_unencrypted_response()
        return response

    def connect(self, path: tuple[Any, ...] | str | Buffer | None = None) -> None:
        if path is None:
            path = Connection.get_socket_path()

        response = self.change_public_keys()

        self.config.box = Box(self.config.private_key, PublicKey(base64.b64decode(response.publicKey)))
        self.config.increase_nonce()

    @staticmethod
    def get_socket_path() -> str:
        server_name = "org.keepassxc.KeePassXC.BrowserServer"
        system = platform.system()
        if system == "Linux" and "XDG_RUNTIME_DIR" in os.environ:
            flatpak_socket_path = os.path.join(os.environ["XDG_RUNTIME_DIR"], "app/org.keepassxc.KeePassXC",
                                               server_name)
            if os.path.exists(flatpak_socket_path):
                return flatpak_socket_path
            return os.path.join(os.environ["XDG_RUNTIME_DIR"], server_name)
        elif system == "Darwin" and "TMPDIR" in os.environ:
            return os.path.join(os.getenv("TMPDIR"), server_name)
        elif system == "Windows":
            path_win = "org.keepassxc.KeePassXC.BrowserServer_" + getpass.getuser()
            return path_win
        else:
            return os.path.join("/tmp", server_name)

    def change_public_keys(self) -> resp.ChangePublicKeysResponse:
        message = req.ChangePublicKeysRequest(config=self.config)
        response = message.send(self.send)
        return response


    def get_databasehash(self) -> str:
        msg = {
            "action": "get-databasehash"
        }
        self.send_encrypted_message(msg)
        response = self.get_encrypted_response()
        return response["hash"]

    def associate(self) -> bool:
        id_public_key = PrivateKey.generate().public_key
        # noinspection PyProtectedMember
        msg = {
            "action": "associate",
            "key": base64.b64encode(self.public_key._public_key).decode("utf-8"),
            "idKey": base64.b64encode(id_public_key._public_key).decode("utf-8")
        }

        self.send_encrypted_message(msg)
        response = self.get_encrypted_response()
        associate_id = response["id"]
        self.associates = [{
            "id": associate_id,
            "key": id_public_key
        }]
        return True

    def load_associates(self, associates: list[dict[str, bytes]]) -> None:
        associates_: list[dict[str, bytes | PublicKey]] = associates.copy()
        for i in range(len(associates)):
            associates_[i]["key"] = PublicKey(associates[i]["key"])
        self.associates = associates_

    def dump_associate(self) -> list[dict[str, bytes]]:
        associates_ = self.associates.copy()
        for i in range(len(associates_)):
            # noinspection PyProtectedMember
            associates_[i]["key"] = associates_[i]["key"]._public_key

        # noinspection PyTypeChecker
        return associates_

    def test_associate(self, trigger_unlock: bool = False) -> bool:
        msg = {
            "action": "test-associate",
            "id": self.associates[0]["id"],
            "key": base64.b64encode(self.associates[0]["key"]._public_key).decode("utf-8")
        }

        self.send_encrypted_message(msg, trigger_unlock)
        self.get_encrypted_response()
        return True

    def get_logins(self, url: str) -> list:
        # noinspection HttpUrlsUsage
        if url.startswith("https://") is False \
                and url.startswith("http://") is False:
            url = f"https://{url}"

        associates_ = self.associates
        for i in range(len(associates_)):
            # noinspection PyProtectedMember,PyTypeChecker
            associates_[i]["key"] = base64.b64encode(associates_[i]["key"]._public_key).decode("utf-8")

        msg = {
            "action": "get-logins",
            "url": url,
            "keys": associates_
        }

        self.send_encrypted_message(msg)
        response = self.get_encrypted_response()
        if not response["count"]:
            return []
        else:
            return response["entries"]

    def get_database_groups(self) -> dict:
        msg = {
            "action": "get-database-groups",
        }

        self.send_encrypted_message(msg)
        response = self.get_encrypted_response()
        return response

    def get_database_entries(self) -> dict:
        msg = {
            "action": "get-database-entries",
        }

        self.send_encrypted_message(msg)
        response = self.get_encrypted_response()
        return response

    def get_unencrypted_response(self) -> dict:
        data = []
        while True:
            new_data = self.socket.recv(4096)
            if new_data:
                data.append(new_data.decode('utf-8'))
            else:
                break
            if len(new_data) < 4096:
                break
        return json.loads(''.join(data))

    def get_encrypted_response(self) -> dict:
        raw_response = self.get_unencrypted_response()
        if "error" in raw_response:
            raise ResponseUnsuccesfulException(raw_response)
        server_nonce = base64.b64decode(raw_response["nonce"])
        decrypted = self.box.decrypt(base64.b64decode(raw_response["message"]), server_nonce)
        response = json.loads(decrypted)
        if not response["success"]:
            raise ResponseUnsuccesfulException(raw_response)
        return response

    def send_encrypted_message(self, msg: dict, trigger_unlock: bool = False) -> None:
        encrypted = base64.b64encode(self.box.encrypt(json.dumps(msg).encode("utf-8"), nonce=self.nonce).ciphertext)
        msg = {
            "action": msg["action"],
            "message": encrypted.decode("utf-8"),
            "nonce": base64.b64encode(self.nonce).decode("utf-8"),
            "clientID": self.client_id
        }
        if trigger_unlock:
            msg['triggerUnlock'] = 'true'
        self.socket.sendall(json.dumps(msg).encode("utf-8"))
        self.nonce = (int.from_bytes(self.nonce, "big") + 1).to_bytes(24, "big")
