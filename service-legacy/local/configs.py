from pydantic import BaseModel


class Deployment:
    def __init__(self) -> None:

        self._api_auth_key: str = "7123eacb2744a02faca2508a82304c3bf154bf0b285da35c2faa2b8498b09872"
        self._lib_codes = {
            111003: "강남",
            111004: "강동",
            111005: "강서",
            111006: "개포",
            111007: "고덕",
            111008: "고척",
            111009: "구로",
            111010: "남산",
            111022: "노원",
            111011: "도봉",
            111012: "동대문",
            111013: "동작",
            111014: "마포",
            111016: "서대문",
            111030: "송파",
            111015: "양천",
            111018: "영등포",
            111019: "용산",
            111020: "정독",
            111021: "종로",
        }

    @property
    def api_auth_key(self):
        return self._api_auth_key

    @property
    def lib_codes(self):
        return self._lib_codes
