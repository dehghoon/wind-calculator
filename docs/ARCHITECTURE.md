# Architecture

## Core Separation

```text
Approved Agent #2 Engine
        |
        v
FastAPI Adapter
        |
        +--> Web Client
        +--> Future Mobile Client
        +--> Report Service
```

The calculation engine is framework-independent. FastAPI owns transport validation, structured errors, OpenAPI, authentication/authorization integration, and report endpoints. Clients consume the API and never reproduce engineering calculations.

## Engineering Source of Truth

The approved `WIND-DUAL-001` specification and the packaged Agent #2 implementation define calculation behavior. Source-code figures are references and mapping aids; numerical coefficients must come from approved datasets, not pixel measurement.

## Report Boundary

On-screen calculation results remain available independently of subscription state. Report preview must preserve the same engineering content and ordering as the formal report. Official PDF generation/download will require server-side authentication and an approved entitlement once the LinkoTech auth/entitlement contract is supplied.

## Known Engineering Limitations

- Exact NBC 2010 clause/table/figure references require external verification.
- NBC 2010 General Static `Cg` selection has no approved dataset in the supplied package.
- Current Components and Cladding roof logic must not be generalized to unextracted roof configurations.
- `Ch` is preserved as a project engineering parameter until its exact basis is verified.

## Deployment

Frontend and backend must remain independently configurable. Provider-specific URLs and credentials belong in environment configuration, never reusable business logic.
