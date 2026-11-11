# ASCE 7-22 / MIDAS integration gate

Status: **prototype, NOT deployable for engineering design**. Separate from NBCC 2010/2020.
The public repository [konohatrong/midas-gen-nx-asce7-directional](https://github.com/konohatrong/midas-gen-nx-asce7-directional)
is a **release-artifact** repository. Its README locates the computation source in
a separate development repository. No LICENSE file was found at the public root.
Do not copy bundled assets, reverse-engineer binaries, or represent the MIDAS
engine as licensed for commercial reuse without written authorization.

## Current implemented scope
- Isolated Python pressure arithmetic using explicitly supplied, externally
  verified q, G, Cp, and GCpi, with sign convention and input validation.
- Unit tests of arithmetic and invalid inputs. These are **not** engineering
  validation tests.
- No API or UI exposure, no production feature flag, no certified output.

## Required before an operational Linkoteq ASCE 7-22 tool
1. Obtain permission and source access for the MIDAS engine, or implement an
   independent ASCE engine from licensed standard text; record provenance.
2. Implement wind-speed/risk maps or verified manual speed input, exposure
   B/C/D, Kz, Kzt, Ke, Kd, G, enclosure GCpi, and MWFRS Cp lookup by geometry.
3. Implement directional +X/-X/+Y/-Y surfaces, pressure envelopes, roof zones,
   ASCE 7-22 Figure 27.3-8 cases and torsional load distributions with explicit
   applicability constraints and US/SI conversions.
4. Validate numerical results against licensed ASCE 7-22 Wind Loads Guide
   G3-1, low-slope roof example, and independent boundary/interpolation cases.
   The MIDAS release repo *reports* 8 G3-1 tests, 7 low-slope tests and 104/104
   placement runs; these have **not** been independently reproduced here.
5. Add engineering review, regression suite, documented unsupported cases,
   gated beta access and disclaimer before any user-facing calculation route.
6. Do not require MIDAS GEN NX for standalone Linkoteq calculations.

This document is an integration boundary and delivery checklist, not a claim
that the third-party product has been integrated or tested.
