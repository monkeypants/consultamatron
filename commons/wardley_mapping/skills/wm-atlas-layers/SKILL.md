---
name: wm-atlas-layers
description: >
  Generate depth-separated maps by visibility layer: user-visible
  (vis > 0.80), capabilities (0.45-0.80), and infrastructure (< 0.45).
  Analyses what characterises each layer in terms of evolution maturity,
  complexity, and cost.
compatibility: Requires Node.js (npx) for OWM rendering via cli-owm
metadata:
  author: monkeypants
  version: "0.1"
  skillset: wardley-mapping
  stage: "atlas"
  freedom: medium
---

# Atlas: Layers

You are generating **depth-separated maps** from a comprehensive
Wardley Map. The map is sliced horizontally into three layers by
visibility, producing one map per layer. This reveals how the character
of the organisation's landscape changes as you move from user-facing
components down to infrastructure.

## Prerequisites

Check that the project directory contains:
- `strategy/map.agreed.owm`

If `strategy/map.agreed.owm` is missing, tell the user to complete
`wm-strategy` first.

The project path is `clients/{org}/projects/{project-slug}/`.

## Staleness check

Compare modification times:
- **Sources**: `strategy/map.agreed.owm`
- **Outputs**: `atlas/layers/user-visible.owm`,
  `atlas/layers/capabilities.owm`, `atlas/layers/infrastructure.owm`,
  `atlas/layers/analysis.md`

If all outputs exist and are newer than all sources, report that the
layers atlas is up to date and skip regeneration. If any source is
newer, or any output is missing, proceed.

## Layer definitions

| Layer | Visibility range | Contains |
|-------|-----------------|----------|
| User-visible | > 0.80 | Anchors, user needs, directly visible capabilities |
| Capabilities | 0.45 - 0.80 | Mid-chain capabilities, business logic, services |
| Infrastructure | < 0.45 | Foundational components, platforms, utilities |

These thresholds match the visibility mapping convention from
`wm-evolve`. Adjust boundaries if the source map uses a different
distribution — the goal is meaningful separation, not rigid cutoffs.

## Step 1: Partition components

Read `strategy/map.agreed.owm` and assign each component (and anchor)
to a layer based on its visibility coordinate. Record:

- Per layer: component count, evolution range (min, max, mean),
  list of components
- Cross-layer edges: dependencies where the source is in one layer
  and the target in another

## Step 2: Identify cross-layer interfaces

For each pair of adjacent layers, list the dependencies that cross the
boundary. These are the **interfaces** between layers. A component in
the capabilities layer that depends on something in the infrastructure
layer represents a coupling point.

Components that sit near a boundary (within 0.05 of a threshold)
should be noted — their layer assignment is somewhat arbitrary.

## Step 3: Generate per-layer maps

Read [owm-dsl-reference.md](../wm-evolve/references/owm-dsl-reference.md)
for full OWM syntax.

For each layer, include:
- All components within that layer's visibility range
- Dependencies **within** the layer
- **Stub components** for cross-layer dependencies: if a component in
  this layer depends on a component in another layer, include the
  foreign component as a stub with a note indicating its home layer

### User-visible layer

Write `atlas/layers/user-visible.owm`:

```owm
title {Organisation} — User-Visible Layer
// Derived from strategy/map.agreed.owm — do not edit directly
// Components with visibility > 0.80

anchor {User Class} [{vis}, {mat}]
component {Need} [{vis}, {mat}]

// Stubs from capabilities layer
component {Capability} [{vis}, {mat}]
note +Capabilities layer [{vis}, {mat}]

{dependencies}

style wardley
```

### Capabilities layer

Write `atlas/layers/capabilities.owm`:

```owm
title {Organisation} — Capabilities Layer
// Derived from strategy/map.agreed.owm — do not edit directly
// Components with visibility 0.45 - 0.80

component {Capability} [{vis}, {mat}]

// Stubs from adjacent layers
component {Need} [{vis}, {mat}]
note +User-visible layer [{vis}, {mat}]
component {Infra} [{vis}, {mat}]
note +Infrastructure layer [{vis}, {mat}]

{dependencies}

style wardley
```

### Infrastructure layer

Write `atlas/layers/infrastructure.owm`:

```owm
title {Organisation} — Infrastructure Layer
// Derived from strategy/map.agreed.owm — do not edit directly
// Components with visibility < 0.45

component {Infra} [{vis}, {mat}]

// Stubs from capabilities layer
component {Capability} [{vis}, {mat}]
note +Capabilities layer [{vis}, {mat}]

{dependencies}

style wardley
```

Guidelines:
- **Preserve original positions** from the source map.
- **Keep stub components visually distinct** using `note` markers.
- **Carry forward annotations** that apply to components in the layer.
- **Include strategic elements** (evolve arrows, inertia markers) that
  apply to components within the layer.

## Step 4: Write analysis

Write `atlas/layers/analysis.md`:

```markdown
# Layer Analysis

## Layer summary

| Layer | Components | Evolution range | Mean evolution |
|-------|-----------|----------------|----------------|
| User-visible | {n} | {min} - {max} | {mean} |
| Capabilities | {n} | {min} - {max} | {mean} |
| Infrastructure | {n} | {min} - {max} | {mean} |

## User-visible layer

{What characterises this layer? Are the components mature (product/
commodity) or immature (genesis/custom)? What does that say about
the organisation's user experience? Where is innovation happening
vs where is it stable?}

## Capabilities layer

{What characterises the middle? Is this where engineering complexity
concentrates? Are capabilities mostly custom-built or leveraging
products? Where is inertia strongest?}

## Infrastructure layer

{What does the foundation look like? Is it mostly commodity (healthy)
or does it contain custom infrastructure (risky)? What's the cost
profile — is infrastructure spend on commodity utilities or on
maintaining bespoke systems?}

## Cross-layer interfaces

| From (layer) | Component | To (layer) | Component |
|-------------|-----------|------------|-----------|
| {layer} | {name} | {layer} | {name} |

{How many cross-layer dependencies exist? Are the interfaces clean
(few, well-defined) or tangled (many, ad-hoc)? What does interface
density suggest about architectural modularity?}

## Evolution gradient

{Does evolution maturity increase as you go deeper (infrastructure
more commodity, user-facing more custom)? Or is the pattern inverted
or flat? What does the gradient imply about the organisation's
strategic posture — building differentiators on commodity foundations,
or custom all the way down?}
```

## Step 5: Render

```
bin/ensure-owm.sh clients/{org}/projects/{slug}/atlas/layers/user-visible.owm
bin/ensure-owm.sh clients/{org}/projects/{slug}/atlas/layers/capabilities.owm
bin/ensure-owm.sh clients/{org}/projects/{slug}/atlas/layers/infrastructure.owm
```

## Output

| File | Purpose |
|------|---------|
| `atlas/layers/user-visible.owm` | User-visible layer map |
| `atlas/layers/user-visible.svg` | Rendered SVG |
| `atlas/layers/capabilities.owm` | Capabilities layer map |
| `atlas/layers/capabilities.svg` | Rendered SVG |
| `atlas/layers/infrastructure.owm` | Infrastructure layer map |
| `atlas/layers/infrastructure.svg` | Rendered SVG |
| `atlas/layers/analysis.md` | Cross-layer analysis |

Present all three SVGs and the layer summary table to the user. This
is a derived view — no client agreement gate is needed.

After completion, regenerate the deliverable site:
```
bin/render-site.sh clients/{org}/projects/{slug}/
```
