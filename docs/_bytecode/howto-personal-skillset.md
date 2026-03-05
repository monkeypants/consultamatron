---
source_hash: sha256:5b25f08af0ac6463ea6c8481614e489f45f226da13bc3b5ea61f692650b415a8
---
Personal vault (`personal/`) is gitignored — safe for experimental skillsets. A skillset declares pipelines (actor-goal sequences) and skills (methodology steps).

Steps: (1) `practice skillset add --name my-methodology` — scaffolds `personal/my_methodology/` with `__init__.py`, `skills/`, `docs/`. (2) Fill `PIPELINES` in `__init__.py`: each Pipeline has slug, actor_goal, and stages (order, skill, description, gate). Multiple distinct use cases → multiple pipelines. (3) Write `SKILL.md` in `personal/my_methodology/skills/{name}/`; set `skillset:` and `stage:` in frontmatter to mark as pipeline skill. (4) Verify with `uv run pytest -m doctrine`. (5) Test via `practice project init/engagement create/project register/engagement next`.

Generic skills (no `skillset:` metadata) go in `personal/skills/`; sync with `practice skill link sync`. Next: howto-contribute-to-commons.
