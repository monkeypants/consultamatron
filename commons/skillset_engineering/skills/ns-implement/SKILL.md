---
name: ns-implement
description: >
  Build the skillset from its agreed design. Scaffolds the BC package,
  writes skill files with methodology guides, creates bash wrapper
  scripts, generates semantic bytecode references, writes the presenter
  and tests, and verifies conformance. Produces a working BC that
  passes all doctrine tests. Use after the pipeline design has been
  agreed.
metadata:
  author: monkeypants
  version: "0.1"
  skillset: new-skillset
  stage: "4"
  freedom: low
---

# Skillset Implementation

You are building a **complete bounded context** from an agreed pipeline
design. This is the construction phase — every artifact you produce
must pass the conformance test suite.

## Prerequisites

Check that the project directory contains:
- `brief.agreed.md` (stage 1 gate)
- `research/synthesis.agreed.md` (stage 2 gate)
- `design/design.agreed.md` (stage 3 gate)
- `research/bytecode/` (semantic bytecode hierarchy)

If missing, tell the operator to complete `ns-design` first.

Read all four inputs. The design document is your specification.

## Step 1: Determine scaffold location

Read `brief.agreed.md` and check the **Source** section to determine
where the BC package will be created:

| Source | Location | Notes |
|--------|----------|-------|
| commons | `commons/{bc_package}/` | Committed to repo, always available |
| personal | `personal/{bc_package}/` | Operator-private, always available |
| partnership | `partnerships/{slug}/{bc_package}/` | Per-engagement access control |

The implementation process is the same regardless of source — all
three produce a full BC package with `__init__.py` exporting SKILLSETS,
a presenter, tests, and conformance coverage. The only difference is
the filesystem location.

Set `{source_dir}` to the appropriate container path and proceed to
Step 2.

## Step 2: Study the target

Before building, understand what a conformant BC looks like:

```bash
uv run practice skillset list --implemented true
uv run practice skillset show --name wardley-mapping
```

Read the conformance tests:
- `tests/test_conformance.py` — the definitive list of properties
  your BC must satisfy

Read at least one existing BC's `__init__.py`, `presenter.py`, and
`tests/test_presenter.py` as exemplars.

## Step 3: Scaffold or verify the BC package

If the BC package does not already exist, scaffold it:

```bash
uv run practice skillset scaffold --name {name} --display-name "{Display Name}"
```

This creates:
- `{bc_package}/__init__.py` with SKILLSETS and PRESENTER_FACTORY
- `{bc_package}/presenter.py` stub
- `{bc_package}/tests/__init__.py`
- `{bc_package}/tests/test_presenter.py`
- Entry in `pyproject.toml` packages list

If the package already exists (e.g. from a prospectus), verify its
structure matches the scaffold output and update as needed.

## Step 4: Populate SKILLSETS

Edit `{bc_package}/__init__.py` to declare all skillsets from the
design document. For each skillset:

```python
Skillset(
    name="{name}",
    display_name="{Display Name}",
    description="{from design}",
    slug_pattern="{prefix}-{n}",
    problem_domain="{from design}",
    value_proposition="{from design}",
    deliverables=[...],
    classification=[...],
    evidence=[...],
    pipeline=[
        PipelineStage(
            order=1,
            skill="{prefix}-{stage-name}",
            prerequisite_gate="{path}",
            produces_gate="{path}",
            description="Stage 1: {Description}",
        ),
        # ... all stages from design
    ],
)
```

### Constraints to verify

- Gate chaining: each stage's prerequisite == previous stage's produces
- First stage's prerequisite is `resources/index.md`
- Stage descriptions are unique across all skillsets in the BC
- Slug pattern contains `{n}`
- Skill names use the prefix from the design document

## Step 5: Write skill files

For each pipeline stage, create:

```
{bc_package}/skills/{skill-name}/
├── SKILL.md
├── references/
│   └── {reference files}
└── scripts/
    └── {recording scripts}
```

### SKILL.md structure

Each skill file must contain:
1. YAML frontmatter with name, description, metadata (skillset, stage)
2. Prerequisites section listing gate artifacts to check
3. Step-by-step methodology from the design document
4. Client interaction protocol (propose-negotiate-agree)
5. Gate recording instructions referencing the bash wrapper

### Writing methodology content

Draw from:
- The design document's stage descriptions
- The semantic bytecode (`research/bytecode/methodology.md`)
- The domain model (`research/bytecode/domain-model.md`)

Each skill file should be self-contained — an agent loading it with
the bytecode references should be able to execute the stage without
reading the full research.

## Step 6: Write bash wrapper scripts

For each stage that records a gate, create a bash script:

```bash
#!/usr/bin/env bash
#
# Record that {stage description}.
#
# Usage:
#   {bc_package}/skills/{skill}/scripts/{script}.sh \
#     --client CLIENT --engagement ENGAGEMENT --project PROJECT \
#     --field "Key=Value" ...

set -euo pipefail

REPO_DIR="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"
CLI="uv run --project $REPO_DIR consultamatron"

CLIENT="" ENGAGEMENT="" PROJECT=""
FIELDS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --client)     CLIENT="$2"; shift 2 ;;
    --engagement) ENGAGEMENT="$2"; shift 2 ;;
    --project)    PROJECT="$2"; shift 2 ;;
    --field)      FIELDS+=("$2"); shift 2 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "$CLIENT" || -z "$ENGAGEMENT" || -z "$PROJECT" ]]; then
  echo "Usage: $0 --client CLIENT --engagement ENGAGEMENT --project PROJECT [--field Key=Value ...]" >&2
  exit 1
fi

CMD=($CLI decision record \
  --client "$CLIENT" --engagement "$ENGAGEMENT" --project "$PROJECT" \
  --title "{Stage N: Description}" \
  --field "Agreed={gate description}")
for f in "${FIELDS[@]}"; do
  CMD+=(--field "$f")
done
"${CMD[@]}"
```

Make every script executable: `chmod +x`.

## Step 7: Create semantic bytecode references

For each skill that needs domain context, symlink or copy the
appropriate bytecode levels into `{skill}/references/`:

- Skills making high-level decisions need L0 (executive) only
- Skills working with domain artifacts need L0 + L1 (domain model)
- Skills executing methodology need L0 + L1 + L2 (methodology)
- Skills doing deep analysis can reference L3 (detail) as needed

The bytecode files live in the project's `research/bytecode/` directory.
Skill files reference them with relative paths.

## Step 8: Write the presenter

Edit `{bc_package}/presenter.py` to assemble workspace artifacts into
a `ProjectContribution`. The presenter must:

1. Read gate artifacts from the project directory
2. Assemble them into `ContentPage` objects
3. Group pages into `ProjectSection` objects
4. Return a `ProjectContribution`

Follow the pattern from existing presenters (wardley_mapping, BMC).

## Step 9: Write presenter tests

Edit `{bc_package}/tests/test_presenter.py`:

1. A `@pytest.mark.doctrine` test class verifying the presenter
   returns a valid `ProjectContribution`
2. A full-workspace test creating all gate artifacts and verifying
   pages and sections
3. An empty-workspace test verifying graceful degradation

## Step 10: Create skill symlinks

Link each skill into the Claude skills directory:

```bash
cd .claude/skills
ln -s ../../{bc_package}/skills/{skill-name} {skill-name}
```

## Step 11: Add custom infrastructure (if needed)

If the design specifies custom usecases, repositories, or CLI
subcommands:

1. Create `{bc_package}/usecases.py` for domain logic
2. Create `{bc_package}/infrastructure.py` for persistence
3. Create `{bc_package}/cli.py` with `register_commands(group)`
4. Add `register_services(container)` to `__init__.py`

Only create what the design requires. Most skillsets need only
the skill files and presenter.

## Step 12: Verify conformance

Run the full test suite:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest -m doctrine
uv run pytest
```

All doctrine tests must pass. Fix any failures before proceeding.

Key conformance checks:
- `TestSkillFileConformance` — SKILL.md frontmatter valid, name
  matches directory, symlinks exist, scripts executable
- `TestPipelineCoherence` — gates chain correctly
- `TestPresenterProtocol` — PRESENTER_FACTORY works
- `TestDecisionTitleJoin` — stage descriptions match title pattern
- `TestBoundedContextTestOwnership` — tests/ directory exists

## Step 13: Present to operator

Show the operator:
1. The BC package structure (files created)
2. Conformance test results
3. Any design decisions made during implementation
4. What the site renderer will produce for this skillset

Ask: "Does this implementation match the design? Are there any
adjustments needed before we mark it complete?"

## Step 14: Iterate and agree

Based on operator feedback, update the implementation. When agreed:
1. Write `implementation.agreed.md` summarising what was built
2. Record the decision:
   ```
   skillset_engineering/skills/ns-implement/scripts/record-implementation-agreed.sh \
     --client {org} --engagement {engagement} --project {slug} \
     --field "Package={bc_package}" \
     --field "Source={commons/partnership-slug}" \
     --field "Stages={count}" \
     --field "Tests=All passing"
   ```

## Completion

When `implementation.agreed.md` is written, the skillset is complete.
Tell the operator:
- The skillset is now registered and discoverable via `practice skillset list`
- Projects can be created with `practice project register`
- The site renderer will automatically detect projects for this skillset
- Future refinements should use `refine-skillset` (rs-assess → rs-plan → rs-iterate)
