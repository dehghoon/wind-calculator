import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.calculations import router as calculations_router

APP_VERSION = "0.2.0"
ENGINE_SPECIFICATION_ID = "WIND-DUAL-001"

app = FastAPI(
    title="Wind Calculator API",
    version=APP_VERSION,
    description=(
        "FastAPI adapter for the approved WIND-DUAL-001 calculation engine. "
        "Engineering formulas remain in the standalone Agent #2 package."
    ),
)

allowed_origins = [
    origin.strip()
    for origin in os.getenv("API_ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
]
if allowed_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
    )

app.include_router(calculations_router)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/version", tags=["system"])
def version() -> dict[str, str]:
    return {
        "application_version": APP_VERSION,
        "engineering_specification_id": ENGINE_SPECIFICATION_ID,
        "engineering_engine_version": "0.1.0",
    }


@app.get("/api/v1/capabilities", tags=["system"])
def capabilities() -> dict[str, object]:
    return {
        "routes": ["WIND-LR", "WIND-GS", "WIND-CC"],
        "code_editions": ["NBC_2010", "NBC_2020"],
        "limitations": [
            "NBC 2010 exact clause/table/figure references remain externally unverified.",
            "NBC 2010 General Static Cg selection is unavailable until an approved edition-specific dataset is supplied.",
            "Components and Cladding roof configurations must not be generalized beyond explicitly extracted logic.",
            "Ch remains a project engineering parameter until its exact code/source basis is verified.",
        ],
    }
