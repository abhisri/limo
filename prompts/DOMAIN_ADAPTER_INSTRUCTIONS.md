# Domain Adapter Instructions

Goal: specialize this generic workspace to a specific domain (finance, legal, HR, BI, research, coding).

## Inputs
- Domain artifacts (docs, logs, spreadsheets, policies, repos)
- The `core/` spine

## Process
1) Identify the domain’s **ground truth artifacts** (examples):
   - Finance: bank statements, invoices, ledger exports
   - Legal: contracts, filings, emails, evidence PDFs
   - HR: resumes, interview notes, scorecards, offer docs
   - BI: dashboards, query results, raw tables, definitions
   - R&D: experiment logs, calibration data, plots, notebooks
   - Coding: repro steps, logs, test outputs, perf traces

2) Define the domain’s “evidence ladder”:
   - Gold: primary sources (raw statements/logs/tests)
   - Silver: derived outputs (CSVs, summaries) with traceability
   - Bronze: narrative reasoning (must cite gold/silver)

3) Add 3–10 **domain invariants** into `core/INVARIANTS.md`
   - Use tags like `[SHARED]`
   - Make them enforceable: violation signal + auto‑action

4) Add a runbook/checklist if the domain is procedural
   - put in `domains/<domain>/RUNBOOK.md`
   - link it from `core/FOLDER_MAP.md`

5) Update `core/FOLDER_MAP.md`
   - where artifacts live
   - naming conventions
   - who owns what

## Output
- A new `domains/<domain>/` pack with:
  - `RUNBOOK.md` (optional)
  - `DATA_DICTIONARY.md` (optional)
  - `TEMPLATES/` (optional)
- Updated `core/INVARIANTS.md` + `core/FOLDER_MAP.md`
