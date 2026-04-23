---
name: blocker-triage-research
description: "Investigate delivery blockers, evaluate options with trade-offs, and recommend a safe unblock path with concise decision memo."
---

# Blocker Triage Research

Use this skill when implementation is blocked and team needs a decision.

## Trigger Conditions

- dependency uncertainty
- external API/runtime behavior mismatch
- repeated failed attempts
- unclear contract ownership

## Input Packet

- blocker statement
- scope and affected files
- failed attempts/evidence
- constraints (security, compatibility)

## Investigation Flow

1. Clarify blocker in one sentence.
2. Identify root causes.
3. Generate 2-3 viable options.
4. Compare trade-offs: correctness, complexity, security, compatibility.
5. Recommend one option.
6. Provide rollback and residual risks.

## Output Artifact

Write decision memo to:

- `_workspace/{phase}/research/blocker-{slug}.md`

Memo sections:

- blocker
- options considered
- recommended path
- implementation notes
- risk + rollback
- unresolved questions

## Quality Rule

Prefer the smallest safe change that unblocks progress.
