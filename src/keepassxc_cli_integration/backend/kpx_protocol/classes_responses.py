from typing import Literal

from pydantic import BaseModel, field_validator

from .classes import KPXProtocolResponse


class ChangePublicKeysResponse(KPXProtocolResponse):
    action: str
    version: str
    publicKey: str
    success: Literal["true"]


class GetDatabasehashResponse(KPXProtocolResponse):
    hash: str
    version: str
    nonce: str
    success: Literal["true"]


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
    count: int
    nonce: str
    success: Literal["true"]
    hash: str
    version: str
    entries: list[Login]

    # noinspection PyNestedDecorators
    @field_validator("count", mode="before")
    @classmethod
    def validate_count(cls, v: str | int) -> int:
        return int(v)
