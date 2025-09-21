from typing import Literal

from .classes import KPXProtocolResponse


class ChangePublicKeysResponse(KPXProtocolResponse):
    action: str
    version: str
    publicKey: str
    success: Literal["true"]
