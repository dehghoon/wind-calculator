import hashlib
import json
from functools import lru_cache
from urllib.request import urlopen

from fastapi import APIRouter, HTTPException

_CORE_URL = (
    "https://raw.githubusercontent.com/dehghoon/linkoteq-structural-core/"
    "e642c8aa27e0b31ff05d4b0f31778edea3fe240d/"
    "catalogs/climate/nbcc-2020/wind-pressure-second-printing.json"
)
_CORE_SHA256 = "2dc931d33b3d2e3375ad7ed5a512cd6d1544f3e590621db49eee71d921b0004d"
router = APIRouter(prefix="/api/v1/climate", tags=["climate"])


@lru_cache(maxsize=1)
def _core_catalog() -> dict:
    with urlopen(_CORE_URL, timeout=8) as response:
        data = response.read(250_000)
    if hashlib.sha256(data).hexdigest() != _CORE_SHA256:
        raise ValueError("Wind climate catalog checksum mismatch")
    return json.loads(data)


@router.get("/nbc-2020/wind-pressure")
def wind_pressures() -> dict:
    try:
        return _core_catalog()
    except (OSError, ValueError) as error:
        raise HTTPException(
            status_code=503,
            detail={"code": "WIND_CATALOG_UNAVAILABLE", "message": "The source-checked Core wind pressure catalog is unavailable."},
        ) from error
