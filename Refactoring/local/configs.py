from pydantic import BaseModel


class Deployment:
    def __init__(self) -> None:

        self._api_auth_key: str = "7123eacb2744a02faca2508a82304c3bf154bf0b285da35c2faa2b8498b09872"
        self._lib_codes = [
            111003,
            111004,
            111005,
            111006,
            111007,
            111008,
            111009,
            111010,
            111022,
            111011,
            111012,
            111013,
            111014,
            111016,
            111030,
            111015,
            111018,
            111019,
            111020,
            111021,
        ]

    @property
    def api_auth_key(self):
        return self._api_auth_key

    @property
    def lib_codes(self):
        return self._lib_codes
