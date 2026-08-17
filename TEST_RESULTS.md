# TEST RESULTS

Date: 2026-08-17

## Environment

- Repository: `dehghoon/wind-calculator`
- Branch: `main`
- Python: local execution environment
- Node.js: available, but npm registry access is unavailable in the local execution environment

## Engineering Engine

Command:

```bash
PYTHONPATH=packages/wind-calculation-engine/src python -m pytest packages/wind-calculation-engine/tests -q
```

Result: **42 passed**

Breakdown:

- 35 inherited Agent #2 tests
- 7 workbook-backed lookup regression tests

The workbook lookup tests cover:

- `Sheet1` exact and interpolated Low-Rise Main Structural `CgCp`
- `Sheet1` Load Case B slope-independent lookup
- `Sheet2` negative-zone logarithmic area interpolation
- `Sheet2` positive-zone logarithmic-difference interpolation
- `Sheet2` lookup-area lower/upper bounds
- `Sheet3a` internal-pressure `Cpi` lookup

Representative regression points were matched directly against `wind_loadf (1).xlsx`, including the workbook-calculated area `7.095337742966286 m¶`.

## FastAPI

Command:

```bash
PYTHONPATH=packages/wind-calculation-engine/src:backend python -m pytest backend/tests -q
```

Result: **9 passed**

This includes the original API adapter tests plus workbook lookup API tests for:

- `POST /api/v1/lookups/low-rise/main-structural/cgcp`
- `POST /api/v1/lookups/components-cladding/low-slope-roof/cgcp`
- `POST /api/v1/lookups/internal-pressure/cpi`

## Workbook Source Verification

The uploaded workbook was inspected directly.

Verified source ranges/formulas include:

- `Sheet1!$C$2:$N$8` — Low-Rise Main Structural `CgCp`
- `Sheet2!$B$4:$G$12` — Components & Cladding `CgCp`
- `Sheet3a!$I$9:$K$12` — internal pressure categories / `Cpi`
- `Sheet3a!$K$5` — open-terrain `Ce`
- `Sheet3a!$K$6` — rough-terrain `Ce`
- `Sheet3a!$E$24`, `G$24`, `I$24`, etc. — roof-slope interpolation
- `Sheet3b!$M$13:$M$22` — C&C workbook lookup use

`Ch` is present as an explicit workbook input (`Sheet3a!$D$12 = 1` in the example), but the supplied workbook does not define a standalone lookup or formula for deriving `Ch` from other inputs.

## Frontend

Implemented:

- Low-Rise `CgCp`  is no longer manually entered.
- Low-Rise input now uses `Load Case + Roof Slope + Surface`.
- `Ce` is calculated from `Terrain + Height`.
- C&C input now uses `Zone + Tributary Area`.
- C&C `CgCp` is returned from the workbook-backed lookup.
- Route switching clears prior result state to prevent cross-route client exceptions.
- General Static continues to obtain `Ce`, `Cg`, `Cp`, and pressure outputs from the backend engine.

A local TypeScript parser/type pass was performed with lightweight dependency stubs. No new application-code syntax errors were found; dependency-specific React/Node typing cannot replace a real production Next.js build.

## Production Build

Status: **PENDING VERCEL VERIFICATION**

The local environment cannot install npm dependencies from the registry, so `npm run build` cannot be truthfully claimed as passed locally. The latest `main` commits are intended to trigger the Vercel production build.

## Remaining Engineering Boundary

- `CgCp`, `Cpi`, and `Ce` now use the supplied workbook data/formulas where supported.
- `Ch` remains an explicit engineering input because the supplied workbook contains a sample/input value but no derivation rule.
- Full C&C pressure assembly beyond the approved current Agent #2 calculation route is not recreated in React.
