---
name: wm-atlas-forces
description: >
  Map showing accelerators and decelerators affecting component evolution.
  Extracts explicit force elements from the strategy map and identifies
  implicit forces from research and evolution assessments. Analyses which
  forces the organisation is riding vs fighting and where strategy aligns
  or conflicts with external pressure.
compatibility: Requires Node.js (npx) for OWM rendering via cli-owm
metadata:
  author: monkeypants
  version: "0.1"
  skillset: wardley-mapping
  stage: "atlas"
  freedom: medium
---

# Atlas: Market Forces

You are generating a **forces-focused map** from a comprehensive Wardley
Map. This view surfaces the accelerators and decelerators shaping
component evolution -- both those already explicit in the strategy map
and those implied by research and evolution assessments.

## Prerequisites

Check that the project directory contains:
- `strategy/map.agreed.owm`
- `evolve/assessments/*.md`
- `strategy/plays/*.md`
- `decisions.md`

If `strategy/map.agreed.owm` is missing, tell the user to complete
`wm-strategy` first.

The project path is `clients/{org}/projects/{project-slug}/`.

## Staleness check

Compare modification times:
- **Sources**: `strategy/map.agreed.owm`, `evolve/assessments/*.md`,
  `resources/index.md`
- **Outputs**: `atlas/forces/map.owm`, `atlas/forces/analysis.md`

If all outputs exist and are newer than all sources, report that the
forces atlas is up to date and skip regeneration. If any source is
newer, or any output is missing, proceed.

## Step 1: Extract explicit forces

Read `strategy/map.agreed.owm` and extract every `accelerator` and
`deaccelerator` element. For each, record its label and position.

Identify which components each force is positioned near (within a
reasonable coordinate distance). These are the components the force
primarily affects.

## Step 2: Identify forces from analytical artifacts

Read the analytical work from earlier stages:

1. **Evolution assessments** (`evolve/assessments/*.md`): The primary
   source for force identification. Assessments contain:
   - Components marked with `inertia` (deceleration signals)
   - Components assessed as evolving faster or slower than expected
   - Evolution reasoning that references external pressures
   - Market maturity evidence that implies acceleration or resistance
2. **Strategy plays** (`strategy/plays/*.md`): Plays identify market
   dynamics in their evidence and impact sections. Forces may be
   implicit in why a play was proposed.
3. **Decisions log** (`decisions.md`): Client feedback during stages
   2-5 may have surfaced forces ("our regulator is about to change
   the rules", "our competitor just launched X").

Supplement from primary research (`resources/`) for:
- **Market trends** not captured in assessments (new entrants,
  consolidation signals)
- **Regulatory changes** with specific timelines or detail
- **Competitive dynamics** not yet reflected in the analytical work

## Step 3: Identify implicit forces

For each signal found in Step 2 that is not already represented by an
explicit force in the strategy map, create a candidate force:

| Force | Type | Affects | Evidence |
|-------|------|---------|----------|
| {name} | accelerator / deaccelerator | {components} | {source} |

Discard candidates that are too speculative or lack clear evidence.
Keep forces that have concrete research backing.

## Step 4: Generate forces map

Read [owm-dsl-reference.md](../wm-evolve/references/owm-dsl-reference.md)
for full OWM syntax.

Write `atlas/forces/map.owm`:

```owm
title {Organisation} — Market Forces
// Derived from strategy/map.agreed.owm — do not edit directly

// Anchors (preserve all from source map)
anchor {Anchor} [{vis}, {mat}]

// Components affected by forces (preserve original positions)
component {Component} [{vis}, {mat}]

// Dependencies (only those connecting force-affected components)
{Anchor}->{Component}

// Explicit forces (carried from strategy map)
accelerator {Force Name} [{vis}, {mat}]
deaccelerator {Force Name} [{vis}, {mat}]

// Identified forces (new — from research and assessment analysis)
accelerator {New Force} [{vis}, {mat}]
deaccelerator {New Force} [{vis}, {mat}]

// Annotations linking forces to components
annotation 1 [{vis}, {mat}] {Force explanation}
annotations [0.90, 0.03]

style wardley
```

Guidelines:
- **Preserve original positions** for all components.
- **Include enough dependency structure** to show how force-affected
  components connect to anchors. Strip unaffected branches.
- **Position new forces** near the components they affect. Accelerators
  to the right of the component (pushing toward commodity), decelerators
  to the left (resisting evolution).
- **Use notes** for brief force descriptions that don't warrant full
  annotations: `note +AI driving commoditisation [0.48, 0.72]`
- **Mark inertia** on components that have deceleration forces acting
  on them, if not already marked.

## Step 5: Write analysis

Write `atlas/forces/analysis.md`:

```markdown
# Market Forces Analysis

## Force inventory

### Accelerators

| Force | Affects | Source | Strength |
|-------|---------|--------|----------|
| {name} | {components} | {explicit / research ref} | High/Med/Low |

### Decelerators

| Force | Affects | Source | Strength |
|-------|---------|--------|----------|
| {name} | {components} | {explicit / research ref} | High/Med/Low |

## Strategic alignment

### Forces the strategy rides

{Forces that the strategy is aligned with — evolution moves that go
with the grain of market pressure. These are tailwinds.}

### Forces the strategy fights

{Forces the strategy pushes against — attempting to evolve components
that face deceleration, or holding back components under acceleration
pressure. These require extra effort and may fail.}

## Force interactions

{Where multiple forces act on the same component or cluster. Do they
reinforce or oppose each other? What net effect does the combination
produce?}

## Emerging forces

{Forces identified from research that are not yet strong but could
become significant. What signals would indicate they're strengthening?
What should the organisation watch for?}

## Recommendations

{Where should the strategy be adjusted to better align with forces?
Which fights are worth fighting and which should be abandoned? Where
can the organisation amplify a favourable force?}
```

## Step 6: Render

```
bin/ensure-owm.sh clients/{org}/projects/{slug}/atlas/forces/map.owm
```

## Output

| File | Purpose |
|------|---------|
| `atlas/forces/map.owm` | Forces-focused map |
| `atlas/forces/map.svg` | Rendered SVG |
| `atlas/forces/analysis.md` | Market forces analysis |

Present the SVG and analysis to the user. Highlight any newly identified
forces that were not in the original strategy map -- these are the
primary value-add of this atlas view.

After completion, regenerate the deliverable site:
```
bin/render-site.sh clients/{org}/projects/{slug}/
```
