---
name: wm-atlas-pipelines
description: >
  Identify components that should be represented as pipelines — multiple
  variants at different evolution stages. Finds explicit pipelines in the
  strategy map and discovers implicit pipeline candidates from research
  and evolution assessments. Analyses migration paths and dual-running
  costs.
compatibility: Requires Node.js (npx) for OWM rendering via cli-owm
metadata:
  author: monkeypants
  version: "0.1"
  skillset: wardley-mapping
  stage: "atlas"
  freedom: medium
---

# Atlas: Pipeline Analysis

You are generating a **pipeline-focused map** from a comprehensive
Wardley Map. This view identifies components where multiple variants
coexist at different evolution stages — legacy alongside modern,
on-premises alongside cloud, manual alongside automated. Pipelines
reveal transition costs and migration paths.

## Prerequisites

Check that the project directory contains:
- `strategy/map.agreed.owm`
- `evolve/assessments/*.md`
- `chain/supply-chain.agreed.md`
- `strategy/plays/*.md`
- `decisions.md`

If `strategy/map.agreed.owm` is missing, tell the user to complete
`wm-strategy` first.

The project path is `clients/{org}/projects/{project-slug}/`.

## Staleness check

Compare modification times:
- **Sources**: `strategy/map.agreed.owm`, `evolve/assessments/*.md`,
  `resources/index.md`
- **Outputs**: `atlas/pipelines/map.owm`, `atlas/pipelines/analysis.md`

If all outputs exist and are newer than all sources, report that the
pipelines atlas is up to date and skip regeneration. If any source is
newer, or any output is missing, proceed.

## Step 1: Extract existing pipelines

Read `strategy/map.agreed.owm` and extract every `pipeline` element.
For each, record:
- The pipeline name and visibility position
- Each variant and its maturity position
- Which other components depend on specific variants
- Any evolve arrows targeting pipeline variants

## Step 2: Identify pipeline candidates from analytical artifacts

Read the analytical work from earlier stages:

1. **Evolution assessments** (`evolve/assessments/*.md`): The primary
   source for pipeline candidates. Look for:
   - Components assessed as "in transition" or "evolving"
   - Components where evolution evidence was mixed (some signals
     pointing to custom, others to product) -- this indicates variants
   - Inertia markers suggesting a legacy variant resisting replacement
   - Components where the client disagreed with initial positioning,
     suggesting coexisting states
2. **Supply chain** (`chain/supply-chain.agreed.md`): Look for
   components noted as having multiple implementations or parallel
   systems serving the same need.
3. **Strategy plays** (`strategy/plays/*.md`): Plays proposing
   migration or replacement inherently identify pipeline situations.
4. **Decisions log** (`decisions.md`): Client feedback during stages
   3-5 may have revealed dual-running systems or planned transitions.

Supplement from primary research (`resources/`) for:
- Legacy/modern coexistence signals not captured in assessments
- Vendor alternatives or technology transitions mentioned in research
  but not surfaced during analytical stages

## Step 3: Identify pipeline candidates

For each signal found in Step 2 that is not already a pipeline in the
strategy map, create a candidate:

| Component | Current position | Variant A | Variant B | Evidence |
|-----------|-----------------|-----------|-----------|----------|
| {name}    | [{vis}, {mat}]  | {legacy}  | {modern}  | {source} |

Assess each candidate:
- Is there genuine coexistence (both variants active), or is one
  already decommissioned?
- Would representing this as a pipeline add clarity to the map?
- Is there a clear migration direction?

Discard candidates that are speculative or would not improve
understanding.

## Step 4: Generate pipelines map

Read [owm-dsl-reference.md](../wm-evolve/references/owm-dsl-reference.md)
for full OWM syntax.

Write `atlas/pipelines/map.owm`:

```owm
title {Organisation} — Pipeline Analysis
// Derived from strategy/map.agreed.owm — do not edit directly

// Anchors
anchor {Anchor} [{vis}, {mat}]

// Existing pipelines (carried from strategy map)
pipeline {Component Name} [{vis}]
{
  component {Legacy Variant} [{mat_legacy}]
  component {Modern Variant} [{mat_modern}]
}

// Newly identified pipelines
pipeline {Candidate Name} [{vis}]
{
  component {Variant A} [{mat_a}]
  component {Variant B} [{mat_b}]
}

// Non-pipeline components (only those connected to pipeline components)
component {Connected Component} [{vis}, {mat}]

// Dependencies (show which variants serve which consumers)
{Anchor}->{Connected Component}
{Connected Component}->{Legacy Variant}; legacy path
{Connected Component}->{Modern Variant}; migration target

// Evolve arrows showing migration direction
evolve {Legacy Variant}->{Decommission Target} {mat}

// Annotations for new pipeline candidates
annotation 1 [{vis}, {mat}] New pipeline: {rationale}
annotations [0.90, 0.03]

style wardley
```

Guidelines:
- **Preserve existing pipelines** exactly as they appear in the source.
- **Add new pipeline candidates** using the OWM pipeline syntax:
  `pipeline Name { component Variant [maturity] }`
- **Show only enough context** to understand what each pipeline serves.
  Strip components unrelated to any pipeline.
- **Use annotated dependencies** (`;legacy path`, `;migration target`)
  to show which consumers use which variants.
- **Position pipeline variants** to reflect their actual evolution
  stage: legacy variants left, modern variants right.

## Step 5: Write analysis

Write `atlas/pipelines/analysis.md`:

```markdown
# Pipeline Analysis

## Pipeline inventory

### Existing pipelines (from strategy map)

| Pipeline | Variants | Evolution spread | Migration direction |
|----------|----------|-----------------|-------------------|
| {name}   | {list}   | {min}-{max mat} | {left to right}   |

### Identified pipeline candidates

| Component | Current | Proposed variants | Evidence |
|-----------|---------|-------------------|----------|
| {name}    | single  | {variant A}, {variant B} | {source} |

## Detailed pipeline analysis

### {Pipeline name}

**Variants**:
- {Variant A} (maturity {mat}): {what it is, who uses it}
- {Variant B} (maturity {mat}): {what it is, who uses it}

**Migration path**: {which direction is the organisation moving?
What triggers the transition? Is there a timeline?}

**Dual-running cost**: {what does it cost to maintain both variants?
Staff skills, infrastructure, integration complexity, licence fees.}

**Dependencies**: {which consumers use which variant? Can they be
migrated independently?}

**Decommission criteria**: {what conditions must be met before the
legacy variant can be retired?}

## Cross-pipeline interactions

{Do any pipelines share variants or dependencies? Could migrations
be coordinated? Are there cascading effects where decommissioning
one variant affects another pipeline?}

## Strategic implications

{What does the pipeline landscape say about the organisation's
technical evolution? Are there too many dual-running situations
(transition debt)? Are migrations progressing or stalled? Where
should the next migration investment go?}

## Recommendations

{Prioritised list: which pipelines need attention? Which candidates
should be formally recognised as pipelines in the strategy map?
Which migrations should be accelerated or abandoned?}
```

## Step 6: Render

```
bin/ensure-owm.sh clients/{org}/projects/{slug}/atlas/pipelines/map.owm
```

## Output

| File | Purpose |
|------|---------|
| `atlas/pipelines/map.owm` | Pipeline-focused map |
| `atlas/pipelines/map.svg` | Rendered SVG |
| `atlas/pipelines/analysis.md` | Pipeline analysis |

Present the pipeline inventory tables and SVG first, then offer the
detailed analysis. Highlight newly identified candidates that were not
in the original strategy map -- these are the primary value-add.

After completion, regenerate the deliverable site:
```
bin/render-site.sh clients/{org}/projects/{slug}/
```
