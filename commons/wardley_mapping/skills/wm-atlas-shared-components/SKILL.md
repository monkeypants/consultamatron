---
name: wm-atlas-shared-components
description: >
  Generate a map showing only components that appear in multiple value
  chains, plus the needs and anchors they connect. Distinguishes
  strategic leverage points from incidental sharing.
compatibility: Requires Node.js (npx) for OWM rendering via cli-owm
metadata:
  author: monkeypants
  version: "0.1"
  skillset: wardley-mapping
  stage: "atlas"
  freedom: medium
---

# Atlas: Shared Components

You are generating a **shared component map** from a comprehensive
Wardley Map. This shows only components that participate in multiple
value chains (serve multiple needs or anchors), revealing where the
organisation's delivery structures overlap and where changes have
cross-cutting impact.

## Prerequisites

Check that the project directory contains:
- `strategy/map.agreed.owm`
- `chain/supply-chain.agreed.md`

If `strategy/map.agreed.owm` is missing, tell the user to complete
`wm-strategy` first.

The project path is `clients/{org}/projects/{project-slug}/`.

## Staleness check

Compare modification times:
- **Sources**: `strategy/map.agreed.owm`,
  `chain/supply-chain.agreed.md`
- **Outputs**: `atlas/shared-components/map.owm`,
  `atlas/shared-components/analysis.md`

If all outputs exist and are newer than all sources, report that the
shared components atlas is up to date and skip regeneration. If any
source is newer, or any output is missing, proceed.

## Step 1: Identify value chains

Read `strategy/map.agreed.owm` and enumerate distinct value chains.
A value chain is the path from an anchor through a need down to leaf
components. Each anchor-need pair defines a chain root.

Read `chain/supply-chain.agreed.md` for the narrative structure of
chains and the rationale behind dependencies.

## Step 2: Find shared components

For each component, determine how many distinct value chains it
appears in. A component is **shared** if it is reachable from two or
more anchor-need pairs.

For each shared component, record:
- Which value chains include it
- Which anchors ultimately depend on it
- Whether the sharing is **structural** (the component inherently
  serves multiple purposes) or **incidental** (two chains happen to
  use the same thing but could use alternatives)

## Step 3: Classify sharing

Categorise each shared component:

- **Strategic leverage point**: Shared because it provides a common
  capability that multiple value chains deliberately build upon.
  Changing it amplifies impact across the organisation. Examples:
  a shared platform, a core data model, a central API.

- **Shared infrastructure**: Commodity or near-commodity components
  used by many chains as a utility. Low risk of cross-chain coupling.
  Examples: cloud hosting, email service, DNS.

- **Incidental coupling**: Components shared by coincidence or
  historical accident. The sharing creates unexpected dependencies.
  Modifying the component for one chain may break another. These are
  often candidates for decomposition.

## Step 4: Generate shared components map

Read [owm-dsl-reference.md](../wm-evolve/references/owm-dsl-reference.md)
for full OWM syntax.

Write `atlas/shared-components/map.owm`:

```owm
title {Organisation} — Shared Components
// Derived from strategy/map.agreed.owm — do not edit directly

// Anchors (all)
anchor {User Class} [{vis}, {mat}]

// Needs that connect to shared components
component {Need} [{vis}, {mat}]

// Shared components
component {Shared Component} [{vis}, {mat}]

// Dependencies (only paths that pass through shared components)
{Anchor}->{Need}
{Need}->{Shared Component}

// Annotations classifying key shared components
annotation 1 [{vis}, {mat}] Leverage point — serves {n} chains

annotations [0.90, 0.03]
style wardley
```

Guidelines:
- **Include all anchors and the needs that route through shared
  components.** Omit needs and chains that are entirely private to
  one anchor.
- **Include only shared components and their immediate connections**
  (one hop up and one hop down from each shared component).
- **Use annotations** to mark the classification (leverage point,
  shared infra, incidental coupling) for the most significant shared
  components.
- **Preserve original positions** from the source map.

## Step 5: Write analysis

Write `atlas/shared-components/analysis.md`:

```markdown
# Shared Components Analysis

## Summary

{Total shared components, what fraction of the map they represent,
how many value chains exist, average sharing degree.}

## Shared component inventory

| Component | Chains | Anchors | Classification |
|-----------|--------|---------|----------------|
| {name} | {count} | {anchor list} | {leverage/infra/incidental} |

## Strategic leverage points

{For each leverage point: what it does, why it's shared, what the
impact of modifying it would be. These are components where investment
has outsized returns — or where mistakes have outsized consequences.}

## Shared infrastructure

{List commodity/utility shared components. These are usually low-risk
sharing — but note any that are single-sourced or have vendor lock-in.}

## Incidental coupling

{Components shared by accident. What risks does this create? Should
they be decomposed into separate instances per chain? What would
decomposition cost vs the risk of leaving them coupled?}

## Modification cost model

{General observations: when a shared component needs to change, how
many teams/chains are affected? Is there a governance process for
shared components, or do changes propagate uncontrolled?}
```

## Step 6: Render

```
bin/ensure-owm.sh clients/{org}/projects/{slug}/atlas/shared-components/map.owm
```

## Output

| File | Purpose |
|------|---------|
| `atlas/shared-components/map.owm` | Shared component map |
| `atlas/shared-components/map.svg` | Rendered SVG |
| `atlas/shared-components/analysis.md` | Sharing classification and analysis |

Present the SVG and the shared component inventory table to the user.
This is a derived view — no client agreement gate is needed.

After completion, regenerate the deliverable site:
```
bin/render-site.sh clients/{org}/projects/{slug}/
```
