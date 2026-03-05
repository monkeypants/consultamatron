---
source_hash: sha256:7589dfd019b64120c3c9e69660b7eb87cc0cf55474b5281afaf147a4bde5bda6
---
Commons (`commons/{org}/{repo}/skillsets/`) hosts shared skillsets. Contributions are BCs added to a hosting repository and referenced from Consultamatron's commons config.

Branch progression: **alpha** (CI warns only — methodology still shaping), **beta** (full conformance required — seeking feedback), **master** (production-quality — breaking changes need major version bump). Stage signalled by hosting repo branch.

Conformance (`uv run pytest -m doctrine`): pipeline stages reference real skills, valid SKILL.md frontmatter, names match directories, no cross-BC imports, clean knowledge pack bytecode, no pipeline skills in agent directories.

PR checklist: fork hosting repo → branch `add-{skillset}` → add BC under `skillsets/{slug}/` → add to `__all__` → run doctrine → open PR against `alpha` branch. PR body: problem domain, target operator, pipelines and their actor-goals, methodology references.

Review focuses on: coherent problem domain, distinct actor-goals per pipeline, agent-executable skill instructions, achievable gate artifacts, useful knowledge packs. Next: howto-proprietary-skillsets, howto-hacking-consultamatron.
