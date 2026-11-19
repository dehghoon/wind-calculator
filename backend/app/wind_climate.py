import hashlib
import json
from functools import lru_cache
from urllib.request import urlopen

from fastapi import APIRouter, HTTPException

_CORE_URL = (
    "https://raw.githubusercontent.com/dehghoon/linkoteq-structural-core/"
    "2e24a26ebccc84e66e98e8077861ac2a9c19b48a/"
    "catalogs/climate/nbcc-2020/wind-pressure-first-printing.json"
)
_CORE_SHA256 = "30665ce9d521ab4979874825e75367ac94e0a36ca8cebd283b2c089b9bf7e05a"
router = APIRouter(prefix="/api/v1/climate", tags=["climate"])


@lru_cache(maxsize=1)
def _core_catalog() -> dict:
    with urlopen(_CORE_URL, timeout=8) as response:
        data = response.read(100_000)
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
