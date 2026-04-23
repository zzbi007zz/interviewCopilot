# Code Standards

## Core Principles

- YAGNI
- KISS
- DRY

## Naming

- Use kebab-case for file names.
- Keep names descriptive for fast codebase scanning.

## File Size Guidance

- Prefer files under ~200 lines for implementation code.
- Split by concern when a file grows too large.

## Security

- Never hardcode API keys.
- Keep provider keys in local agent `.env` only.
- Do not expose keys in web/client code.

## Implementation Discipline

- Match existing plan scope; avoid speculative features.
- Validate contracts at integration boundaries.
- Include rollback note for risky changes.

## Quality Gates

- Phase cannot progress without QA PASS report.
- Tracking docs update required after QA PASS.
