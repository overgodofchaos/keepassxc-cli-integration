from pydantic import PrivateAttr, computed_field

from . import classes_responses as responses
from .classes import KPXProtocolRequest


# noinspection PyPep8Naming
class ChangePublicKeysRequest(KPXProtocolRequest[responses.ChangePublicKeysResponse]):
    _action: str = PrivateAttr("change-public-keys")
    _response: responses.ChangePublicKeysResponse = PrivateAttr(responses.ChangePublicKeysResponse)

    @computed_field()
    def publicKey(self) -> str:
        return self.config.public_key_utf8

    @computed_field()
    def nonce(self) -> str:
        return self.config.nonce_utf8

    @computed_field()
    def clientID(self) -> str:
        return self.config.client_id