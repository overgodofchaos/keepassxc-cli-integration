from typing import Literal

from .classes import KPXProtocolResponse


class ChangePublicKeysResponse(KPXProtocolResponse):
    action: str
    version: str
    publicKey: str
    success: Literal["true"]


class GetDatabasehashResponse(KPXProtocolResponse):
    action: str
    hash: str
    version: str