---
name: handoff-package-checklist
description: "Verify frontend/backend handoff package completeness before QA gate, ensuring all required evidence and contract details are present."
---

# Handoff Package Checklist

Use this skill before QA gate dispatch.

## Required Artifacts

- `_workspace/{phase}/handoff/frontend.md`
- `_workspace/{phase}/handoff/backend.md`
- `_workspace/{phase}/contracts/api-contract.md` (if API changed)

## Frontend Handoff Must Include

- scope implemented
- changed files
- acceptance criteria mapping
- test/build evidence
- known limitations/risks

## Backend Handoff Must Include

- routes/services changed
- request/response examples
- changed files
- test evidence
- rollback note

## Pre-QA Decision

- COMPLETE: all required fields and artifacts present
- INCOMPLETE: list exact missing fields/files and block QA dispatch

## Output

Return concise checklist result with:

- completeness status
- missing items (if any)
- ready-for-QA flag
