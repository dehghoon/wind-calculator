# TEST RESULTS

Date: 2026-08-17

## Environment

- Python: local execution environment
- Node.js: v22.16.0
- npm: 10.9.2
- Repository: `dehghoon/wind-calculator`
- Branch: `main`

## Verified

### Inherited Engineering Tests

Command:

```bash
PYTHONPATH=packages/wind-calculation-engine/src python -m pytest packages/wind-calculation-engine/tests -q
```

Result: **35 passed**

The inherited Agent #2 test files were preserved without modification.

### FastAPI Adapter Tests

Command:

```bash
PYTHONPATH=packages/wind-calculation-engine/src:backend python -m pytest backend/tests -q
```

Result: **6 passed**

The API tests were re-run after CORS configuration changes.

### Total Python Tests

Result: **41 passed**

## Web Checks

A TypeScript compiler parse/type attempt was executed with the globally available compiler. The compiler reported only missing external package/type declarations (`react`, `next`, and Node types) because npm dependencies could not be installed in the execution environment.

No TypeScript syntax error was reported before dependency resolution errors.

## Production Build

Status: **NOT VERIFIED**

`npm install` could not complete because the execution environment could not retrieve packages from the npm registry. An offline install also failed because the required packages were not cached.

A GitHub Actions workflow could not be created through the connected GitHub credential because workflow-file creation returned:

```text
403 Resource not accessible by personal access token
```

Therefore `npm run build` has not been claimed as passing.

## Known Risks / Remaining Gates

- Production Next.js build remains unverified.
- Browser integration against a running FastAPI instance remains unverified.
- Authentication and report entitlement are not implemented.
- Report preview and official PDF generation are not implemented.
- No production deployment has been performed or verified.
