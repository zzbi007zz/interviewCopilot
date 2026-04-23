---
name: phase-gate-playbook
description: "Define and execute incremental QA gate checks per phase, with objective pass/fail criteria, boundary coherence validation, and unblock recommendations."
---

# Phase Gate Playbook

Use this playbook to run phase-level quality gates before promoting work.

## Why this exists

Final-only QA is too late. Phase gates catch integration mismatches early and reduce rework.

## Required Inputs

- phase acceptance criteria
- frontend handoff artifact
- backend handoff artifact
- contract note if API changed

## Gate Checklist

### 1) Evidence Completeness

- handoff artifacts exist
- changed-files list present
- tests/build evidence attached
- rollback note present

### 2) Boundary Coherence (mandatory)

- API response shape matches frontend expectations
- linked routes/path values map to real routes
- status/state transitions align between definitions and implementation
- no secret values exposed in client-side code

### 3) Phase-Specific Checks

- bootstrap phase: ownership conflicts, required files, flow consistency
- contract phase: schema/defaults compatibility
- backend phase: route/auth/error handling tests
- frontend phase: loading/error/empty/success states + integration sanity
- integration phase: e2e journey + latency/rollback/security checks

## Decision Rule

- PASS when all mandatory checks pass and no high-severity risk remains.
- FAIL when any mandatory check fails or evidence is missing.

## Required Output

Write gate report to:

- `plans/reports/qa-gate-{date}-{phase}.md`

Report sections:

1. Scope
2. Checks Run
3. Evidence
4. Failed Checks
5. Risk Rating
6. Gate Decision (PASS/FAIL)
7. Unblock Recommendation
8. Rollback Note

## Remediation Loop

1. FAIL -> return exact fix list by owner.
2. Owners patch only failed checks.
3. Re-run gate for affected checks.
4. Continue until PASS.
