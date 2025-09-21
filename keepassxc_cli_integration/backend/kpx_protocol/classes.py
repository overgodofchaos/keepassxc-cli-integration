from pydantic import BaseModel, ConfigDict, Field, computed_field

from keepassxc_cli_integration.backend.kpx_protocol.connection_config import ConnectionConfig


class KPXProtocol(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        frozen=True
    )


class KPXProtocolRequest(KPXProtocol):
    _action = "none"
    config: ConnectionConfig = Field(exclude=True)

    @computed_field
    def action(self) -> str:
        return self._action

    def to_bytes(self) -> bytes:
        return self.model_dump_json().encode("utf-8")


# noinspection PyPep8Naming
class ChangePublicKeysRequest(KPXProtocolRequest):
    _action = "change-public-keys"

    @computed_field()
    def publicKey(self) -> str:
        return self.config.public_key_utf8

    @computed_field()
    def nonce(self) -> str:
        return self.config.nonce_utf8

    @computed_field()
    def clientID(self) -> str:
        return self.config.client_id


if __name__ == "__main__":
    import base64
    import platform
    import socket

    import nacl.utils
    from nacl.public import Box, PrivateKey, PublicKey

    from keepassxc_cli_integration.backend.kpx_protocol.winpipe import WinNamedPipe

    if platform.system() == "Windows":
        import win32file

    if platform.system() == "Windows":
        _socket = WinNamedPipe(win32file.GENERIC_READ | win32file.GENERIC_WRITE, win32file.OPEN_EXISTING)
    else:
        _socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)


    config = ConnectionConfig(
        private_key=PrivateKey.generate(),
        nonce=nacl.utils.random(24),
        client_id=base64.b64encode(nacl.utils.random(24)).decode("utf-8"),
        socket=_socket,
        box=None,
        associates=None,
    )

    x = ChangePublicKeysRequest(config=config)

    print(x.model_dump_json(indent=2))