---
name: wm-atlas-anchor-chains
description: >
  Generate one focused map per anchor (user class), showing only that
  anchor's transitive dependency closure. Draws on needs, supply chain,
  evolution assessments, and strategy plays for per-anchor analysis.
  Produces per-anchor maps and analyses.
compatibility: Requires Node.js (npx) for OWM rendering via cli-owm
metadata:
  author: monkeypants
  version: "0.1"
  skillset: wardley-mapping
  stage: "atlas"
  freedom: medium
---

# Atlas: Anchor Chains

You are generating **per-anchor dependency maps** from a comprehensive
Wardley Map. Each anchor (user class) gets its own map showing only the
components it transitively depends on. This reveals what each user class
actually sees and relies upon.

## Prerequisites

Check that the project directory contains:
- `strategy/map.agreed.owm`
- `needs/needs.agreed.md`
- `chain/supply-chain.agreed.md`
- `evolve/assessments/*.md`
- `strategy/plays/*.md`

If `strategy/map.agreed.owm` is missing, tell the user to complete
`wm-strategy` first.

The project path is `clients/{org}/projects/{project-slug}/`.

## Staleness check

For each anchor, compare modification times:
- **Sources**: `strategy/map.agreed.owm`, `needs/needs.agreed.md`,
  `chain/supply-chain.agreed.md`
- **Outputs**: `atlas/anchor-{slug}/map.owm`,
  `atlas/anchor-{slug}/analysis.md`

If all outputs for an anchor exist and are newer than all sources, skip
that anchor. Only regenerate anchors whose outputs are missing or stale.
Report which anchors were skipped and which were regenerated.

## Step 1: Enumerate anchors

Read `strategy/map.agreed.owm` and extract all `anchor` declarations.
For each anchor, derive a slug (lowercase, hyphens, no special chars).

## Step 2: Compute dependency closures

For each anchor, walk the dependency graph forward (anchor -> needs ->
capabilities -> infrastructure) collecting every component reachable
from that anchor. This is the **transitive closure**.

Record which components are **unique** to this anchor (not reachable
from any other anchor) and which are **shared** with other anchors.

## Step 3: Gather per-anchor context from analytical artifacts

Read the analytical work from earlier stages, filtered to this anchor:

1. **Needs** (`needs/needs.agreed.md`): Which needs belong to this
   anchor, what was agreed about their priority, and what confidence
   level was assigned.
2. **Supply chain** (`chain/supply-chain.agreed.md`): The agreed
   decomposition of this anchor's needs into capabilities. The chain
   document may note structural observations specific to this anchor's
   dependency tree.
3. **Evolution assessments** (`evolve/assessments/*.md`): Evolution
   reasoning for components in this anchor's closure. What stage are
   they at? Where is inertia?
4. **Strategy plays** (`strategy/plays/*.md`): Which plays affect
   components in this anchor's chain? What strategic moves are
   proposed for this user class's value delivery?

Use primary research (`resources/`) only to supplement with
user-class-specific findings not already distilled in the needs
document or assessments.

## Step 4: Generate per-anchor maps

Read [owm-dsl-reference.md](../wm-evolve/references/owm-dsl-reference.md)
for full OWM syntax.

For each anchor, write `atlas/anchor-{slug}/map.owm`:

```owm
title {Organisation} — {Anchor Name} Chain
// Derived from strategy/map.agreed.owm — do not edit directly

anchor {Anchor Name} [{vis}, {mat}]

// Components in this anchor's transitive closure
component {Need} [{vis}, {mat}]
component {Capability} [{vis}, {mat}]

// Dependencies (only those within this closure)
{Anchor Name}->{Need}
{Need}->{Capability}

style wardley
```

Guidelines:
- **One anchor per map.** Do not include other anchors.
- **Preserve original positions.** Components keep their coordinates
  from the source map so the reader can cross-reference.
- **Carry forward relevant annotations** from the strategy map that
  apply to components in this closure.
- **Mark shared components** with a note: `note +Shared [{vis}, {mat}]`
  so the reader sees which parts of the chain are shared infrastructure.

## Step 5: Write per-anchor analysis

For each anchor, write `atlas/anchor-{slug}/analysis.md`:

```markdown
# {Anchor Name} — Dependency Chain

## Chain summary

- **Components**: {count} total ({unique} unique, {shared} shared)
- **Chain depth**: {max dependency depth from anchor}
- **Needs served**: {list of needs this anchor depends on}

## What this user class sees

{Describe the experience from this anchor's perspective. What's directly
visible to them? What capabilities do they interact with?}

## Unique dependencies

{Components only this anchor reaches. Why are they specific to this
user class? What does that imply about serving this user differently?}

## Shared dependencies

{Components shared with other anchors. What coordination constraints
does this create? If a shared component changes, who else is affected?}

## Strategic context

{What the analytical artifacts reveal about this anchor: evolution
trajectory of its chain, inertia points blocking its value delivery,
strategic plays affecting its components, and any client feedback
from the decisions log. Supplement with primary research findings
where they add user-class-specific detail.}
```

## Step 6: Render

For each anchor:
```
bin/ensure-owm.sh clients/{org}/projects/{slug}/atlas/anchor-{slug}/map.owm
```

## Output

For each anchor `{slug}`:

| File | Purpose |
|------|---------|
| `atlas/anchor-{slug}/map.owm` | Anchor's dependency chain map |
| `atlas/anchor-{slug}/map.svg` | Rendered SVG |
| `atlas/anchor-{slug}/analysis.md` | Per-anchor analysis |

Present a summary table of all anchors (component count, chain depth,
unique vs shared ratio) followed by each anchor's SVG. This is a
derived view — no client agreement gate is needed.

After completion, regenerate the deliverable site:
```
bin/render-site.sh clients/{org}/projects/{slug}/
```
