import base64
from collections.abc import Callable
from typing import Generic, TypeVar

from nacl.public import PublicKey
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr, ValidationError, computed_field

from keepassxc_cli_integration.backend.kpx_protocol.connection_config import ConnectionConfig

from . import errors
from .errors import ResponseUnsuccesfulException

R = TypeVar('R', bound="KPXProtocolResponse")


class KPXProtocol(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )


class KPXProtocolResponse(KPXProtocol):
    pass


class KPXProtocolRequest(Generic[R], KPXProtocol):
    _action: str = PrivateAttr("none")
    _response: type[R] = PrivateAttr(R)
    config: ConnectionConfig = Field(exclude=True)

    @computed_field
    @property
    def action(self) -> str:
        return self._action

    def send(self, send_function: Callable[['KPXProtocolRequest'], dict]) -> R:
        data = send_function(self)
        self.config.increase_nonce()
        try:
            return self._response.model_validate(data)
        except ValidationError:
            raise ResponseUnsuccesfulException(data) from errors

    def to_bytes(self) -> bytes:
        return self.model_dump_json().encode("utf-8")


class KPXEncryptedMessageRequest(KPXProtocol):
    unencrypted_request: KPXProtocolRequest = Field(exclude=True)
    trigger_unlock: bool = Field(default=False, exclude=True)

    @property
    def config(self) -> ConnectionConfig:
        return self.unencrypted_request.config

    @computed_field()
    def nonce(self) -> str:
        return self.config.nonce_utf8

    # noinspection PyPep8Naming
    @computed_field()
    def clientID(self) -> str:
        return self.config.client_id

    @computed_field()
    def action(self) -> str:
        return self.unencrypted_request.action

    @computed_field()
    def message(self) -> str:
        msg = self.unencrypted_request
        encrypted = base64.b64encode(
            self.config.box.encrypt(msg.model_dump_json().encode("utf-8"),
                                    nonce=self.config.nonce).ciphertext)
        return encrypted.decode("utf-8")

    # noinspection PyPep8Naming
    @computed_field()
    def triggerUnlock(self) -> str:
        if self.trigger_unlock:
            return "true"
        else:
            return "false"

    def to_bytes(self) -> bytes:
        return self.model_dump_json().encode("utf-8")

