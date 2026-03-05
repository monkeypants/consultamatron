# Hacking on Consultamatron

This page is for people who want to modify the Consultamatron platform
itself — the CLI, the domain entities, the conformance tests, or the
infrastructure layer. If you want to author skillsets, see the other
HOWTO pages.

## Architecture overview

Consultamatron follows a clean hexagonal architecture. The key layers:

```
src/practice/           domain layer (entities, protocols, use cases)
bin/cli/                application layer (DI wiring, CLI commands)
bin/cli/infrastructure/ infrastructure layer (filesystem implementations)
tests/                  test suite
```

### The semantic waist

The `practice` package is the semantic waist. Nothing outside `practice/`
may import from inside a bounded context (BC) package. All external
dependencies flow in through protocols (interfaces defined in
`src/practice/repositories.py`).

This means:
- `bin/cli/` imports from `practice` — fine
- A BC may import from `practice` — fine
- `bin/cli/` imports from a BC directly — **not allowed**
- A BC imports from another BC — **not allowed**

The no-cross-BC-import doctrine test enforces this.

### Bounded contexts

Each BC is a Python package discovered at startup. The practice layer
calls `bc_discovery.discover_all_bc_modules()` which scans for packages
with a `PIPELINES` export and registers them. BCs live in:

- `commons/{org}/{repo}/skillsets/{name}/` (commons sources)
- `personal/{bc_slug}/` (personal source)
- `partnerships/{slug}/skillsets/{name}/` (partnership sources)

### Clean architecture ports

New infrastructure (a database, a cloud API, a different filesystem
layout) goes in `bin/cli/infrastructure/`. It implements a protocol from
`src/practice/repositories.py`. It is wired into the `Container` in
`bin/cli/di.py`. The use case in `bin/cli/usecases.py` calls the protocol.
Nothing in `practice/` knows about the infrastructure.

## Development setup

```bash
git clone https://github.com/monkeypants/consultamatron.git
cd consultamatron
uv sync --group test --group lint
```

Run the full suite:

```bash
uv run pytest
```

Run only doctrine (structural conformance) tests:

```bash
uv run pytest -m doctrine
```

Lint and format:

```bash
uv run ruff check .
uv run ruff format .
```

## CLI command generation

Most CLI commands follow a pattern: a Pydantic request model in
`bin/cli/dtos.py`, a use case class in `bin/cli/usecases.py`, and a
`generate_command()` call in `bin/cli/main.py`.

`generate_command()` (in `bin/cli/config.py`) introspects the request model
and generates Click options automatically. See `dev/cli-command-generation.md`
for details.

For commands that need richer output formatting or special argument handling,
write the Click command manually (as in `practice skill link sync`).

## Adding a new entity

1. Define the entity in `src/practice/entities.py` (Pydantic BaseModel)
2. If it needs persistence, add a protocol to `src/practice/repositories.py`
3. Implement the protocol in `bin/cli/infrastructure/`
4. Wire the implementation into `Container` in `bin/cli/di.py`
5. Add a use case in `bin/cli/usecases.py`
6. Add request/response DTOs to `bin/cli/dtos.py`
7. Add CLI commands to `bin/cli/main.py`
8. Write tests (entities → usecases → CLI, in that order)

## Conformance tests

`tests/test_conformance.py` contains `@pytest.mark.doctrine` tests that
verify structural invariants. These tests run against the live repository
(not just a tmp_path) and catch problems like:

- Pipeline stages referencing nonexistent skills
- Skills with invalid frontmatter
- Cross-BC imports
- Pipeline skills appearing in agent directories

When you add a new structural invariant, add a doctrine test for it.

## Pack-and-wrap

Knowledge packs use a bytecode-compilation model. Items in a pack directory
are summarised into `_bytecode/` mirrors by the `practice pack compile`
command. These summaries let agents navigate knowledge cheaply.

See `howto-pack-and-wrap.md` for usage. See `src/practice/pack_and_wrap.py`
and `src/practice/content_hash.py` for the implementation.

## Contributing

Follow the standard GitHub fork-and-PR workflow. All PRs run CI:
`uv run ruff check`, `uv run ruff format --check`, and `uv run pytest`.
Doctrine tests must pass. PRs that break doctrine are not merged.
