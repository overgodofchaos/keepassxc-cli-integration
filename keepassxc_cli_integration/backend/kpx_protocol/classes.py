from collections.abc import Callable
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr, ValidationError, computed_field

from keepassxc_cli_integration.backend.kpx_protocol.connection_config import ConnectionConfig

from . import errors
from .errors import ResponseUnsuccesfulException

R = TypeVar('R', bound="KPXProtocolResponse")


class KPXProtocol(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True
    )


class KPXProtocolResponse(KPXProtocol):
    pass


class KPXProtocolRequest(Generic[R], KPXProtocol):
    _action: str = PrivateAttr("none")
    _response: type[R]
    config: ConnectionConfig = Field(exclude=True)

    @computed_field
    def action(self) -> str:
        return self._action

    def send(self, send_function: Callable[['KPXProtocolRequest'], dict]) -> R:
        data = send_function(self)

        try:
            return self._response.model_validate(data)
        except ValidationError:
            raise ResponseUnsuccesfulException(data) from errors

    def to_bytes(self) -> bytes:
        return self.model_dump_json().encode("utf-8")
