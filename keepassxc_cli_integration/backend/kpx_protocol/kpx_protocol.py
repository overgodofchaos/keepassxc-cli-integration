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
from .connection_config import Associate, Associates, ConnectionConfig
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
            box=None
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
        # self.config.increase_nonce()
        response = self.get_unencrypted_response()
        return response

    def send_encrypted(self,
                       message: k.KPXProtocolRequest,
                       trigger_unlock: bool = False
                       ) -> dict:

        message = k.KPXEncryptedMessageRequest(unencrypted_request=message, trigger_unlock=trigger_unlock)

        self.socket.sendall(message.to_bytes())
        # self.config.increase_nonce()
        response = self.get_encrypted_response()
        return response

    def connect(self, path: tuple[Any, ...] | str | Buffer | None = None) -> None:
        if path is None:
            path = Connection.get_socket_path()

        response = self.change_public_keys()

        self.config.box = Box(self.config.private_key, PublicKey(base64.b64decode(response.publicKey)))


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


    def get_databasehash(self) -> resp.GetDatabasehashResponse:
        message = req.GetDatabasehashRequest(config=self.config)
        response = message.send(self.send_encrypted)
        return response

    def associate(self) -> bool:
        id_public_key = PrivateKey.generate().public_key

        message = req.AssociateRequest(config=self.config, id_public_key=id_public_key)
        response = message.send(self.send_encrypted)
        db_hash = self.get_databasehash().hash

        self.config.associates.add(
            db_hash=db_hash, associate=Associate(db_hash=db_hash, id=response.id, key=id_public_key))

        return True

    def load_associates(self, associates: Associates) -> None:
        self.config.associates = associates.model_copy(deep=True)

    def dump_associate(self) -> Associates:
        return self.config.associates.model_copy(deep=True)

    def test_associate(self, trigger_unlock: bool = False) -> bool:
        try:
            db_hash = self.get_databasehash().hash
            associate = self.config.associates.get_by_hash(db_hash)
            message = req.TestAssociateRequest(
                config=self.config,
                id=associate.id,
                key=associate.key_utf8,
            )
            response = message.send(self.send_encrypted)
            if response.success == "true":
                return True
        except KeyError:
            pass

        return False

    def get_logins(self, url: str) -> list[resp.Login]:
        # noinspection HttpUrlsUsage
        if url.startswith("https://") is False \
                and url.startswith("http://") is False:
            url = f"https://{url}"

        db_hash = self.get_databasehash().hash

        message = req.GetLoginsRequest(
            config=self.config,
            url=url,
            associates=self.config.associates,
            db_hash=db_hash,
        )

        response = message.send(self.send_encrypted)

        return response.entries

    # def get_database_groups(self) -> dict:
    #     msg = {
    #         "action": "get-database-groups",
    #     }
    #
    #     self.send_encrypted_message(msg)
    #     response = self.get_encrypted_response()
    #     return response

    # def get_database_entries(self) -> dict:
    #     msg = {
    #         "action": "get-database-entries",
    #     }
    #
    #     self.send_encrypted_message(msg)
    #     response = self.get_encrypted_response()
    #     return response

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
        decrypted = self.config.box.decrypt(base64.b64decode(raw_response["message"]), server_nonce)
        response = json.loads(decrypted)

        return response


