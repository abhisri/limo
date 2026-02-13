# Domain Pack Checklist (for publishing or reuse)

A domain pack should ideally include:

## Required
- `domains/<domain>/README.md` — what this pack is for
- `domains/<domain>/ARTIFACTS.md` — what counts as ground truth
- `domains/<domain>/RUNBOOK.md` — “how we work” steps (if procedural)
- Update pointers in `core/FOLDER_MAP.md`

## Strongly recommended (if data-heavy)
- `domains/<domain>/DATA_DICTIONARY.md` — schema + definitions
- `domains/<domain>/QA_PROTOCOL.md` — deterministic checks
- `domains/<domain>/EXPORT_PRESETS.md` — output bundles / redaction rules

## Publishing safety
- No real names, IDs, IPs, customer data, private logs.
- Use synthetic examples only.
