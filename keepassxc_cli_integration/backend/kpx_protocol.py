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

if platform.system() == "Windows":
    import getpass

    import win32file


class ResponseUnsuccesfulException(Exception):
    pass


class WinNamedPipe:
    """ Unix socket API compatible class for accessing Windows named pipes """

    def __init__(self,
                 desired_access: int,
                 creation_disposition: int,
                 share_mode: int = 0,
                 security_attributes: bool | None = None,
                 flags_and_attributes: int = 0,
                 input_nullok: None = None) -> None:
        self.desired_access = desired_access
        self.creation_disposition = creation_disposition
        self.share_mode = share_mode
        self.security_attributes = security_attributes
        self.flags_and_attributes = flags_and_attributes
        self.input_nullok = input_nullok
        self.handle = None

    def connect(self, address: str) -> None:
        try:
            self.handle = win32file.CreateFile(
                fr'\\.\pipe\{address}',
                self.desired_access,
                self.share_mode,
                self.security_attributes,
                self.creation_disposition,
                self.flags_and_attributes,
                self.input_nullok
            )
        except Exception as e:
            raise Exception(  # noqa: B904
                f"Error: Connection could not be established to pipe {address}", e
            )

    def close(self) -> None:
        if self.handle:
            self.handle.close()

    def sendall(self, message: str | bytes) -> None:
        win32file.WriteFile(self.handle, message)

    def recv(self, buff_size: int) -> str:
        _, data = win32file.ReadFile(self.handle, buff_size)
        return data


class Connection:
    def __init__(self) -> None:
        self.private_key = PrivateKey.generate()
        self.public_key = self.private_key.public_key
        self.nonce = nacl.utils.random(24)
        self.client_id = base64.b64encode(nacl.utils.random(24)).decode("utf-8")
        if platform.system() == "Windows":
            self.socket = WinNamedPipe(win32file.GENERIC_READ | win32file.GENERIC_WRITE, win32file.OPEN_EXISTING)
        else:
            self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.associates: list[dict[str, PublicKey]] | None = None
        self.box: Box | None = None

    def connect(self, path: tuple[Any, ...] | str | Buffer | None = None) -> None:
        if path is None:
            path = Connection.get_socket_path()

        self.socket.connect(path)
        message = json.dumps(self.change_public_keys())
        self.socket.sendall(message.encode("utf-8"))
        response = self.get_unencrypted_response()
        if not response["success"]:
            raise ResponseUnsuccesfulException
        self.box = Box(self.private_key, PublicKey(base64.b64decode(response["publicKey"])))
        self.nonce = (int.from_bytes(self.nonce, "big") + 1).to_bytes(24, "big")

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

    def change_public_keys(self) -> dict[str, str | int]:
        # noinspection PyProtectedMember
        return {
            "action": "change-public-keys",
            "publicKey": base64.b64encode(self.public_key._public_key).decode("utf-8"),
            "nonce": base64.b64encode(self.nonce).decode("utf-8"),
            "clientID": self.client_id
        }

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
