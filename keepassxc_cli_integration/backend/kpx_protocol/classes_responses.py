from typing import Literal

from pydantic import BaseModel

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


class AssociateResponse(KPXProtocolResponse):
    hash: str
    version: str
    success: Literal["true"]
    id: str
    nonce: str


class TestAssociateResponse(KPXProtocolResponse):
    hash: str
    version: str
    success: Literal["true"]
    id: str
    nonce: str


class Login(BaseModel):
    login: str
    name: str
    password: str


class GetLoginsResponse(KPXProtocolResponse):
    count: str
    nonce: str
    success: Literal["true"]
    hash: str
    version: str
    entries: list[Login]

