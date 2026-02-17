---
name: wm-atlas-overview
description: >
  Generate a simplified landscape map from the comprehensive strategy map.
  Collapses dense component clusters into submap elements to produce a
  ~10-12 component orientation artifact. The overview map is the first
  thing a new reader should see.
compatibility: Requires Node.js (npx) for OWM rendering via cli-owm
metadata:
  author: monkeypants
  version: "0.1"
  skillset: wardley-mapping
  stage: "atlas"
  freedom: medium
---

# Atlas: Overview Map

You are generating a **simplified landscape map** from a comprehensive
Wardley Map. This is a derived artifact — it extracts and simplifies,
it does not add new analysis or require client agreement.

## Prerequisites

Check that the project directory contains:
- `strategy/map.agreed.owm`
- `brief.agreed.md`

If `strategy/map.agreed.owm` is missing, tell the user to complete
`wm-strategy` first.

The project path is `clients/{org}/projects/{project-slug}/`.

## Staleness check

Compare modification times:
- **Sources**: `strategy/map.agreed.owm`, `brief.agreed.md`
- **Outputs**: `atlas/overview/map.owm`, `atlas/overview/analysis.md`

If all outputs exist and are newer than all sources, report that the
overview atlas is up to date and skip regeneration. If any source is
newer, or any output is missing, proceed.

## Step 1: Extract structure

Read `strategy/map.agreed.owm` and catalogue:
1. All anchors (user classes)
2. All components, their positions, and their dependencies
3. All strategic annotations, evolve arrows, and pipelines

Count the total components. The overview map should have **10-12
elements** (anchors + components + submaps).

## Step 2: Identify dense clusters

Find areas where multiple components cluster together — typically
3+ components that share a parent or form a tightly connected subgraph.
Good candidates for collapsing:

- Infrastructure components that serve a single capability
- Internal sub-chains that a reader does not need to see at overview level
- Pipeline variants (collapse to a single representative component)

For each cluster, choose a name that describes the group's purpose.

## Step 3: Build the overview map

Read [owm-dsl-reference.md](../wm-evolve/references/owm-dsl-reference.md)
for full OWM syntax.

Write `atlas/overview/map.owm`:

```owm
title {Organisation} — Overview
// Derived from strategy/map.agreed.owm — do not edit directly

// Anchors (preserve all from source map)
anchor {User Class} [{vis}, {mat}]

// Visible components (keep the most important)
component {Key Component} [{vis}, {mat}]

// Collapsed clusters as submaps
submap {Cluster Name} [{vis}, {mat}]

// Dependencies (simplified — connect to submaps where applicable)
{User Class}->{Key Component}
{Key Component}->{Cluster Name}

style wardley
```

Guidelines:
- **Preserve all anchors.** Every user class from the source map appears.
- **Keep user-visible components explicit.** Anything above visibility 0.80
  should generally remain as a named component.
- **Use `submap` for collapsed clusters.** Position the submap at the
  centroid of the components it replaces.
- **Simplify dependencies.** If A->B->C and B is collapsed into a submap,
  the overview shows A->submap and submap->C.
- **Carry forward key annotations** (3-4 maximum) that convey the
  landscape's strategic posture.

## Step 4: Write analysis

Write `atlas/overview/analysis.md`:

```markdown
# Overview Map

## Landscape shape

{Describe the overall structure: how many anchors, rough depth of the
chain, whether the map is wide (many parallel chains) or deep (long
serial chains), where components cluster on the evolution axis.}

## What stands out

{2-4 observations visible at overview level: dominant evolution stages,
presence of inertia, strategic moves in flight, structural imbalances.}

## Collapsed areas

| Submap | Contains | Why collapsed |
|--------|----------|---------------|
| {name} | {component list} | {rationale} |

## Reading guide

{Brief orientation prose: where to start reading the map, what the
major groupings are, what the key dependencies mean.}
```

Read `brief.agreed.md` to ground the analysis in the agreed project
scope.

## Step 5: Render

```
bin/ensure-owm.sh clients/{org}/projects/{slug}/atlas/overview/map.owm
```

## Output

| File | Purpose |
|------|---------|
| `atlas/overview/map.owm` | Simplified landscape map |
| `atlas/overview/map.svg` | Rendered SVG |
| `atlas/overview/analysis.md` | Orientation prose |

Present the SVG and analysis summary to the user. This is a derived
view — no client agreement gate is needed.

After completion, regenerate the deliverable site:
```
bin/render-site.sh clients/{org}/projects/{slug}/
```
