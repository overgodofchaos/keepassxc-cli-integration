import os

__all__ = [
    'debug'
]


class Debug:
    @property
    def debug(self) -> bool:
        x = os.environ.get("KPX_PROTOCOL_DEBUG")
        return True if (x and x == "true") else False


debug = Debug().debug