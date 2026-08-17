# Wind Calculator

Engineering wind-load application for the approved `WIND-DUAL-001` calculation specification covering NBC 2010 and NBC 2020 routes.

## Architecture

```text
Approved Agent #2 Engine
        |
        v
FastAPI Adapter
        |
        +--> Next.js Web Client
        +--> Future Mobile Client
        +--> Report Service
```

Engineering formulas, validation, units, warnings, and applicability remain in `packages/wind-calculation-engine`. The web client consumes the FastAPI contract and does not reproduce engineering calculations.

## Repository Structure

```text
backend/                               FastAPI adapter and API tests
packages/wind-calculation-engine/      Approved Agent #2 Python engine and inherited tests
web/                                   Responsive Next.js client
docs/                                  Architecture notes
```

## Implemented Routes

- `WIND-LR` — Low-Rise applicability
- `WIND-GS` — General Static pressure coefficients
- `WIND-CC` — Components & Cladding area lookup

Unsupported or unresolved engineering rules fail explicitly instead of being estimated.

## Run API

```bash
export PYTHONPATH="$(pwd)/packages/wind-calculation-engine/src"
python -m pip install -r backend/requirements.txt
export API_ALLOWED_ORIGINS="http://localhost:3000"
cd backend
uvicorn app.main:app --reload
```

## Run Web

```bash
cd web
cp .env.example .env.local
npm install
npm run dev
```

The API base URL is configured through `NEXT_PUBLIC_API_BASE_URL`.

## Tests

Inherited engineering tests:

```bash
PYTHONPATH=packages/wind-calculation-engine/src python -m pytest packages/wind-calculation-engine/tests -q
```

API adapter tests:

```bash
PYTHONPATH=packages/wind-calculation-engine/src:backend python -m pytest backend/tests -q
```

Web quality gates:

```bash
cd web
npm install
npm run type-check
npm run build
```

See `TEST_RESULTS.md` for the latest verified status.

## Engineering Boundaries

- NBC 2010 exact clause/table/figure references remain externally unverified.
- NBC 2010 General Static `Cg` selection remains unavailable until an approved edition-specific dataset is supplied.
- Components & Cladding roof logic must not be generalized beyond explicitly extracted configurations.
- `Ch` remains a project engineering parameter until its exact source basis is verified.

## Next Layers

1. Add report-content assembly matching the approved Report Specification.
2. Integrate approved LinkoTech authentication and server-side report entitlement when the auth contract is available.
3. Add report preview and premium official PDF generation.
4. Add application-generated wind/zone schematics without embedding engineering calculations in visualization code.
5. Add portable deployment configuration and CI when repository workflow permissions allow it.
