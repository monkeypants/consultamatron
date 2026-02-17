---
name: ns-design
description: >
  Design the pipeline for a new skillset. Defines skills (stages), gate
  artifacts, domain model, deliverables, quality criteria, and how skills
  compose into a coherent methodology. Produces a design document that
  fully specifies what ns-implement will build. Use after domain research
  has been synthesised.
metadata:
  author: monkeypants
  version: "0.1"
  skillset: new-skillset
  stage: "3"
  freedom: medium
---

# Pipeline Design for New Skillset

You are designing the **pipeline** for a new consulting skillset. This
is the structural commitment — after this stage, the skillset's shape
is fixed. Everything in `ns-implement` follows from this design.

## Prerequisites

Check that the project directory contains:
- `brief.agreed.md` (stage 1 gate)
- `research/synthesis.agreed.md` (stage 2 gate)
- `research/bytecode/` (semantic bytecode hierarchy)

If missing, tell the operator to complete `ns-research` first.

Read all three inputs. The brief defines what we're building, the
synthesis defines the domain, the bytecode is what skill agents will
load at runtime.

## Step 1: Study exemplars

Before designing, study how existing skillsets are built:

```bash
uv run practice skillset list --implemented true
uv run practice skillset show --name wardley-mapping
uv run practice skillset show --name business-model-canvas
```

Read the `__init__.py` of each implemented BC to see how SKILLSETS,
PRESENTER_FACTORY, and pipeline stages are declared.

Read the conformance tests to understand what properties the new
skillset must satisfy:
- `tests/test_conformance.py` — pipeline coherence, gate chaining,
  unique descriptions, slug pattern, BC test ownership, presenter
  protocol, service registration, CLI registration

The design must produce a skillset that passes all of these.

## Step 2: Design the pipeline

For each stage in the pipeline, define:

```markdown
### Stage {n}: {Description}

**Skill name**: `{prefix}-{name}`
**Prerequisite gate**: `{path/to/artifact}`
**Produces gate**: `{path/to/artifact}`

#### What the skill does

{2-3 paragraphs describing the methodology step. What does the
agent do? What does the operator/client contribute? What decisions
are made?}

#### Inputs

- {What the skill reads — gate artifacts, research, bytecode levels}

#### Outputs

- {Gate artifact}
- {Any additional artifacts produced}

#### Client interaction

{How does the propose-negotiate-agree loop work for this stage?
What does the agent propose? What does the client push back on?}

#### Bash wrapper

{What practice CLI commands does the recording script invoke?
What fields does it record in the decision log?}

#### References needed

{What semantic bytecode levels does this skill load?
What reference files does it need in its skill directory?}
```

### Design constraints

- **Gate chaining**: Each stage's prerequisite must equal the previous
  stage's produces gate. The first stage's prerequisite is always
  `resources/index.md` (shared research).
- **Monotonic order**: Stage numbers must be strictly ascending.
- **Unique descriptions**: No two stages may share a description string.
  Descriptions are the fragile join with the decision log.
- **Slug pattern**: Must contain `{n}` for project numbering.
- **Skill naming**: Use a consistent prefix (e.g. `wm-` for Wardley
  Mapping, `bmc-` for BMC). Choose a 2-3 letter prefix.

## Step 3: Define the domain model

Extract from the research synthesis:

```markdown
## Domain Model

### Entities

| Entity | Description | Lifecycle |
|--------|-------------|-----------|
| {name} | {what it represents} | {created → refined → agreed} |

### Relationships

{Entity A} --{relationship}--> {Entity B}

### Value Objects

| Name | Fields | Invariants |
|------|--------|------------|
| {name} | {field list} | {rules that must hold} |

### Aggregate boundaries

{Which entities are managed together? This determines repository
boundaries if usecases are needed.}
```

## Step 4: Define deliverables

For each deliverable listed in the brief:

```markdown
### {Deliverable name}

**Format**: {markdown / OWM / JSON / HTML}
**Produced by stage**: {n}
**Consumed by**: {who reads this and for what purpose}

#### Structure

{Template or schema for the deliverable}

#### Quality criteria

- {Testable property}
- {Measurable attribute}
```

## Step 5: Define quality criteria

Enumerate properties that `rs-assess` (the refine skillset) will
evaluate:

```markdown
## Quality Criteria

### Pipeline quality
- [ ] All stages have clear, atomic gate artifacts
- [ ] Skill files are self-contained (loadable without pipeline history)
- [ ] Semantic bytecode hierarchy is within token budgets
- [ ] Bash wrappers invoke practice CLI correctly

### Deliverable quality
- [ ] {Domain-specific quality property}
- [ ] {Domain-specific quality property}

### Conformance
- [ ] Passes all doctrine tests
- [ ] Presenter returns valid ProjectContribution
- [ ] Slug pattern contains {n}
- [ ] Pipeline stages chain correctly
```

## Step 6: Identify implementation needs

Determine what `ns-implement` must produce:

```markdown
## Implementation Inventory

### Required (conformance)
- [ ] `__init__.py` with SKILLSETS and PRESENTER_FACTORY
- [ ] `presenter.py` implementing ProjectPresenter
- [ ] `tests/__init__.py` and `tests/test_presenter.py`
- [ ] Skill files (`skills/{prefix}-{name}/SKILL.md`) for each stage
- [ ] Bash wrapper scripts for each gate recording
- [ ] Semantic bytecode reference files per skill
- [ ] Symlinks from `.claude/skills/` to `{bc}/skills/{skill-name}`

### Optional (if the methodology requires)
- [ ] Custom usecases (if domain logic exceeds what skill files handle)
- [ ] Custom repository types
- [ ] CLI subcommands (`cli.py` with `register_commands`)
- [ ] `register_services` hook for container wiring
- [ ] Custom infrastructure modules
```

## Step 7: Present to operator

Present the complete design document. Ask:

1. "Does this pipeline capture the methodology correctly?"
2. "Are the gate artifacts the right checkpoints?"
3. "Is the domain model complete?"
4. "Are the quality criteria sufficient?"
5. "What custom infrastructure does this skillset need, if any?"

## Step 8: Iterate and agree

Based on operator feedback, update the design. When agreed:
1. Write `design/design.agreed.md`
2. Record the decision:
   ```
   skillset_engineering/skills/ns-design/scripts/record-design-agreed.sh \
     --client {org} --engagement {engagement} --project {slug} \
     --field "Stages={count}" \
     --field "Prefix={skill prefix}" \
     --field "Custom infra={yes/no}"
   ```

## Completion

When `design/design.agreed.md` is written, tell the operator the next
step is `ns-implement` to scaffold and build the skillset.
