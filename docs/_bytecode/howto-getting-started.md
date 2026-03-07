---
source_hash: sha256:2dd872f50863d902c854d9036c4c8358d77136aac0363108e7644c04fa65cdae
---
Consultamatron: open consulting practice platform combining a semantic knowledge base, `practice` CLI, and agent-facing skills. Operator (human) owns engagements; agent co-pilot knows methodology.

Key concepts: **Operator** — the human. **Skillset** — methodology packaged for machine use; declares pipelines and skills. **Skill** — one methodology step (SKILL.md, gates, output); type is generic (always in agent context) or pipeline (CLI-served only). **Pipeline** — skill sequence for one actor-goal (e.g. Wardley `create` vs `analyse` are separate use cases). **Engagement** — scoped assignment tracking pipeline position.

Layout: `skills/` (generic), `docs/` (knowledge pack), `src/practice/` (domain), `bin/cli/` (CLI), `commons/` (public skillsets), `personal/`/`partnerships/`/`clients/` (gitignored).

Generic/pipeline distinction: generic skills always in agent directories; pipeline skills served by CLI only. Sync with `practice skill link sync`. Next: howto-personal-skillset, howto-contribute-to-commons, howto-hacking-consultamatron.
