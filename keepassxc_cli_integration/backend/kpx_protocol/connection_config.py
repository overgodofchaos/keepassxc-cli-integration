import base64
import socket
from functools import cached_property

from nacl.public import Box, PrivateKey, PublicKey
from pydantic import BaseModel, ConfigDict, Field

from .winpipe import WinNamedPipe


class ConnectionConfig(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True,
    )

    private_key: PrivateKey
    nonce: bytes
    client_id: str
    socket: WinNamedPipe | socket.socket
    box: Box | None = None
    associates: list[dict[str, PublicKey]] | None = None

    @cached_property
    def public_key(self) -> PublicKey:
        return self.private_key.public_key

    @staticmethod
    def _decode(data: PublicKey | bytes) -> str:
        if isinstance(data, bytes):
            data_ = data
        else:
            # noinspection PyProtectedMember
            data_ = data._public_key
        return base64.b64encode(data_).decode("utf-8")

    @property
    def public_key_utf8(self) -> str:
        return self._decode(self.public_key)

    @property
    def nonce_utf8(self) -> str:
        return self._decode(self.nonce)

    def increase_nonce(self) -> None:
        self.nonce = (int.from_bytes(self.nonce, "big") + 1).to_bytes(24, "big")