---
name: wm-atlas-need-traces
description: >
  Generate one focused map per user need, tracing the full supply chain
  from need down to infrastructure. Reveals chain depth, complexity
  concentration, and infrastructure dependencies for each need.
compatibility: Requires Node.js (npx) for OWM rendering via cli-owm
metadata:
  author: monkeypants
  version: "0.1"
  skillset: wardley-mapping
  stage: "atlas"
  freedom: medium
---

# Atlas: Need Traces

You are generating **per-need supply chain maps** from a comprehensive
Wardley Map. Each user need gets its own map tracing the full dependency
chain from the need through capabilities down to infrastructure. This
reveals how deep and complex the delivery of each need actually is.

## Prerequisites

Check that the project directory contains:
- `strategy/map.agreed.owm`
- `chain/supply-chain.agreed.md`

If `strategy/map.agreed.owm` is missing, tell the user to complete
`wm-strategy` first.

The project path is `clients/{org}/projects/{project-slug}/`.

## Staleness check

For each need, compare modification times:
- **Sources**: `strategy/map.agreed.owm`,
  `chain/supply-chain.agreed.md`
- **Outputs**: `atlas/need-{slug}/map.owm`,
  `atlas/need-{slug}/analysis.md`

If all outputs for a need exist and are newer than all sources, skip
that need. Only regenerate needs whose outputs are missing or stale.
Report which needs were skipped and which were regenerated.

## Step 1: Enumerate needs

Read `strategy/map.agreed.owm` and identify user needs. Needs are
components at the top of the dependency chain, directly depended on
by anchors. Cross-reference with `chain/supply-chain.agreed.md` to
confirm the need list.

For each need, derive a slug (lowercase, hyphens, no special chars).

## Step 2: Trace dependency chains

For each need, walk the dependency graph **downward** (need ->
capabilities -> sub-capabilities -> infrastructure) collecting every
component reachable from that need. This is the forward transitive
closure starting from the need.

Also record the **reverse**: which anchors depend on this need.

## Step 3: Analyse chain structure

For each need's chain, compute:
- **Depth**: longest path from need to a leaf component
- **Width**: maximum number of components at any single depth level
- **Complexity hotspot**: the depth level with the most components
- **Shared tail**: components in this chain that also appear in other
  needs' chains (infrastructure sharing)

Read `chain/supply-chain.agreed.md` for the narrative context of each
chain — why components exist, what role they play, what alternatives
were considered.

## Step 4: Generate per-need maps

Read [owm-dsl-reference.md](../wm-evolve/references/owm-dsl-reference.md)
for full OWM syntax.

For each need, write `atlas/need-{slug}/map.owm`:

```owm
title {Organisation} — {Need Name} Trace
// Derived from strategy/map.agreed.owm — do not edit directly

// Anchors that depend on this need
anchor {Anchor} [{vis}, {mat}]

// The need itself
component {Need} [{vis}, {mat}]

// Full chain below this need
component {Capability} [{vis}, {mat}]
component {Infrastructure} [{vis}, {mat}]

// Dependencies (only within this trace)
{Anchor}->{Need}
{Need}->{Capability}
{Capability}->{Infrastructure}

style wardley
```

Guidelines:
- **Include the anchors** that depend on this need, for context.
- **Preserve original positions** from the source map.
- **Carry forward relevant annotations** — evolve arrows, inertia
  markers, strategic notes that touch components in this trace.
- **Mark shared infrastructure** with notes so the reader sees where
  this chain connects to other needs' chains.

## Step 5: Write per-need analysis

For each need, write `atlas/need-{slug}/analysis.md`:

```markdown
# {Need Name} — Supply Chain Trace

## Chain summary

- **Serving anchors**: {which user classes depend on this need}
- **Chain depth**: {longest path length}
- **Total components**: {count}
- **Shared with other needs**: {count and names of shared components}

## Chain structure

{Describe the shape. Is it a narrow deep chain or a wide shallow one?
Where does branching occur? Where does it converge on shared
infrastructure?}

## Complexity concentration

{Which layer has the most components? What does that mean — is the
complexity in capabilities (hard to build) or infrastructure (hard to
operate)?}

## Infrastructure dependencies

{What does this need ultimately rest on? Are those foundations stable
(commodity) or risky (custom/genesis)? What happens if a foundation
component fails or changes?}

## Evolution profile

{How do components in this chain distribute across the evolution axis?
Is the chain mostly commodity, mostly custom, or mixed? What does that
imply about delivery cost and risk?}
```

## Step 6: Render

For each need:
```
bin/ensure-owm.sh clients/{org}/projects/{slug}/atlas/need-{slug}/map.owm
```

## Output

For each need `{slug}`:

| File | Purpose |
|------|---------|
| `atlas/need-{slug}/map.owm` | Need's supply chain trace |
| `atlas/need-{slug}/map.svg` | Rendered SVG |
| `atlas/need-{slug}/analysis.md` | Per-need chain analysis |

Present a comparison table (need, depth, component count, shared
component count) followed by each need's SVG. This is a derived
view — no client agreement gate is needed.

After completion, regenerate the deliverable site:
```
bin/render-site.sh clients/{org}/projects/{slug}/
```
