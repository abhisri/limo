# Contributing

PRs welcome. LIMO is opinionated about memory architecture but permissive about domains — contributions should respect that balance.

## Principles

- **Domain-agnostic by default.** Changes to the core framework should work for any domain, not just yours.
- **Additive over breaking.** Don't change existing file formats or remove fields — existing LIMO users have populated files that depend on them.
- **Earned complexity.** New patterns belong in `advanced_patterns.md` until they've proven their worth across multiple domains.
- **Easy to audit.** LIMO is Markdown. Keep it that way. No build steps, no dependencies, no tooling requirements.

## What's helpful

- **Bug fixes** in templates, framework spec, or instructions
- **New tool-specific setup guides** in `INSTRUCTIONS.md` (e.g., Copilot Workspace, Replit Agent, etc.)
- **Advanced patterns** that emerged from real multi-session usage — add to `advanced_patterns.md` with provenance
- **Improvements to invariants or never-again patterns** that are genuinely universal (not domain-specific)
- **Translations** of the framework or instructions

## What doesn't fit

- Domain-specific content (that goes in your own LIMO domain, not the framework)
- Dependencies on external tools, databases, or APIs
- Changes that make the framework heavier rather than more useful

## Style

- Write prose, not bullet soup
- Keep templates copy-pasteable
- Use `[DOMAIN]`, `[USER]`, `[DATE]` as placeholders
- Include provenance when adding patterns ("this emerged from X sessions in Y domain")
