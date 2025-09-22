import base64
import socket
from functools import cached_property
from typing import List

from nacl.public import Box, PrivateKey, PublicKey
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr, computed_field, field_serializer, field_validator
from pydantic_core.core_schema import FieldSerializationInfo

from .winpipe import WinNamedPipe


class Associate(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    db_hash: str
    id: str
    key: PublicKey

    @property
    def key_utf8(self) -> str:
        # noinspection PyProtectedMember
        return base64.b64encode(self.key._public_key).decode("utf-8")

    @field_serializer('key')
    def serialize_key(self, value: PublicKey, _info: FieldSerializationInfo) -> str:
        # noinspection PyProtectedMember
        return value._public_key.hex()

    # noinspection PyNestedDecorators
    @field_validator('key', mode="before")
    @classmethod
    def parse_key(cls, value: str) -> PublicKey:
        if isinstance(value, str):
            value = PublicKey(bytes.fromhex(value))
        return value


class Associates(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
    )

    entries: dict[str, Associate] = Field(default_factory=dict)

    def get_by_hash(self, db_hash: str) -> Associate:
        associate = self.entries[db_hash]
        return associate.model_copy(deep=True)

    def delete_by_hash(self, db_hash: str) -> None:
        del self.entries[db_hash]

    def delete_all(self) -> None:
        self.entries = {}

    @property
    def list(self) -> list[Associate]:
        return [a.model_copy(deep=True) for a in self.entries.values()]

    def add(self, db_hash: str, associate: Associate) -> None:
        self.entries[db_hash] = associate.model_copy(deep=True)


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
    associates: Associates = Associates()

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