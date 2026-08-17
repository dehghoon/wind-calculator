# Wind Calculator

Engineering wind-load application for the approved `WIND-DUAL-001` calculation specification covering NBC 2010 and NBC 2020 routes.

## Current Status

Phase 1 establishes the repository and API boundary around the approved Agent #2 calculation engine. The engineering engine is stored unchanged under `packages/wind-calculation-engine`.

Implemented API routes expose only calculations already present in the approved engine. Missing edition-specific datasets and unresolved source references fail explicitly instead of being guessed.

## Repository Structure

```text
backend/                         FastAPI adapter and API tests
packages/wind-calculation-engine/  Approved Agent #2 Python engine
docs/                            Architecture and implementation notes
```

## Engineering Boundaries

- Engineering formulas, validation, warnings, units, and applicability remain owned by the Agent #2 package.
- The API does not recreate formulas.
- NBC editions remain isolated.
- NBC 2010 General Static `Cg` selection remains unavailable until the approved edition-specific dataset is supplied.
- Components and Cladding logic is not generalized beyond explicitly extracted configurations.
- `Ch` remains a project engineering parameter until its exact source basis is verified.

## Run API

```bash
export PYTHONPATH="$(pwd)/packages/wind-calculation-engine/src"
python -m pip install -r backend/requirements.txt
cd backend
uvicorn app.main:app --reload
```

## Tests

Run inherited engineering tests unchanged:

```bash
PYTHONPATH=packages/wind-calculation-engine/src python -m pytest packages/wind-calculation-engine/tests -q
```

Run API adapter tests:

```bash
PYTHONPATH=packages/wind-calculation-engine/src:backend python -m pytest backend/tests -q
```

## Next Implementation Layers

1. Complete typed calculation contracts around approved route datasets.
2. Add report-content assembly matching the approved Report Specification.
3. Integrate approved LinkoTech authentication and server-side report entitlement when the auth contract is available.
4. Add the responsive React/Next.js client consuming only the FastAPI contract.
5. Add application-generated wind/zone schematics without embedding engineering calculations in visualization code.
6. Add portable deployment configuration and CI.
