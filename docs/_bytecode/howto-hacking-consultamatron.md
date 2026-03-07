---
source_hash: sha256:032dd93bd5158450bf0ada51faa7e0336af924381ed395a405edf395402c326e
---
Hexagonal architecture: `src/practice/` (domain — entities, protocols, use cases), `bin/cli/` (application — DI, commands), `bin/cli/infrastructure/` (filesystem implementations), `tests/` (test suite).

Semantic waist: `practice` package is the narrow waist. Allowed: `bin/cli/` → `practice`, BC → `practice`. Forbidden: `bin/cli/` → BC directly, BC → BC. Doctrine test enforces no cross-BC imports.

BC discovery: `bc_discovery.discover_all_bc_modules()` scans for packages with `PIPELINES` export. Sources: `commons/`, `personal/`, `partnerships/`.

Dev setup: `git clone`, `uv sync --group test --group lint`, `uv run pytest`, `uv run pytest -m doctrine`, `uv run ruff check/format`.

Adding new entities: define in `entities.py` → protocol in `repositories.py` → implement in `infrastructure/` → wire in `di.py` → use case in `usecases.py` → DTOs in `dtos.py` → CLI in `main.py` → tests (entities → usecases → CLI).

CLI commands: Pydantic request model + use case class + `generate_command()` in `main.py`. `generate_command()` auto-generates Click options from model fields. Manual commands for rich formatting.

Pack-and-wrap: `practice pack compile` summarises pack items into `_bytecode/` mirrors (SHA-256 freshness). See `src/practice/pack_and_wrap.py`. New structural invariants → doctrine test in `test_conformance.py`.
