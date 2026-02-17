---
name: wm-atlas-movement
description: >
  Generate a movement-focused map showing only components with evolve
  arrows plus their immediate dependencies. Produces a change-programme
  view highlighting what moves, why, and what that movement requires.
  Produces atlas/movement/ with map and analysis.
compatibility: Requires Node.js (npx) for OWM rendering via cli-owm
metadata:
  author: monkeypants
  version: "0.1"
  skillset: wardley-mapping
  stage: "atlas"
  freedom: medium
---

# Atlas: Movement Map

You are generating a movement-focused view of the Wardley Map. This map
isolates evolution -- every component that has an evolve arrow, plus the
immediate context needed to understand what each movement means for the
value chain. This is the "change programme" view.

## Prerequisites

Check that the project directory (`clients/{org}/projects/{project-slug}/`)
contains:
- `strategy/map.agreed.owm` -- the comprehensive strategy map
- `evolve/map.agreed.owm` -- the evolution-positioned map
- `evolve/assessments/*.md` -- evolution assessment documents

If `strategy/map.agreed.owm` is missing, tell the user to complete
`wm-strategy` first.

## Staleness check

Check whether `atlas/movement/map.owm` already exists. If it does,
compare the modification times of:
- `strategy/map.agreed.owm`
- `evolve/map.agreed.owm`
- All files in `evolve/assessments/`

against `atlas/movement/map.owm`. If all source files are older than
the output, report that the movement atlas is up to date and skip
regeneration. If any source is newer, regenerate.

## Step 1: Extract moving components

Read `strategy/map.agreed.owm` and identify:

1. **Every `evolve` statement** -- these are the components in motion.
   Record the component name, current position, target position, and
   any decorator changes (e.g. strategy shift from build to buy).
2. **Direct dependents** -- for each evolving component, include
   components that depend on it (one level up). These are affected by
   the movement.
3. **Direct dependencies** -- for each evolving component, include
   components it depends on (one level down). These may enable or
   constrain the movement.
4. **Inertia markers** -- any `inertia` keyword on moving components
   or their direct context. This tension is critical.

Omit all other components, dependencies, annotations, and notes.

## Step 2: Analyse each movement

For each evolving component, read the relevant evolution assessment
from `evolve/assessments/` and determine:

- **What is driving this evolution?** Market maturation, technology
  shift, competitor pressure, strategic decision?
- **What stage transition does it represent?** Genesis to Custom,
  Custom to Product, Product to Commodity? Each has different
  implications.
- **What capabilities are needed?** Does moving this component
  require new skills, vendor relationships, or organisational changes?
- **What happens to dependents?** When a component moves right on the
  evolution axis, its dependents may need to adapt. A capability
  moving from custom to product means dependents can standardise.
- **What happens to dependencies?** Does this movement require its
  dependencies to also evolve? Are there blockers below?
- **What is the timeline?** Is this a 6-month shift or a 3-year
  transformation?

## Step 3: Generate movement map

Read [owm-dsl-reference.md](../wm-evolve/references/owm-dsl-reference.md)
for OWM syntax.

Write `atlas/movement/map.owm` containing:
- A `title` (e.g. `title {Organisation} -- Evolution Movement`)
- Components identified in Step 1 at their **current** positions
  (from the strategy map)
- All evolve arrows from the strategy map
- Dependencies only between included components
- Inertia markers preserved from the source
- Annotations summarising what drives each movement (numbered, under
  12 words each)
- Notes for timeline indicators or capability requirements
- Accelerators and decelerators relevant to the moving components
- `style wardley`

The map should be readable as a standalone change programme: "these
things move, for these reasons, with these dependencies and risks."

## Step 4: Write analysis

Write `atlas/movement/analysis.md`:

```markdown
# Movement Analysis

## Overview

{How many components are evolving? What is the overall direction --
is the organisation commoditising, productising, or building new
capabilities? What does the movement pattern suggest about the
organisation's strategic posture?}

## Movement inventory

{For each evolving component, a structured entry:}

### {Component Name}: {current stage} to {target stage}

- **Current position**: {maturity value} ({stage name})
- **Target position**: {maturity value} ({stage name})
- **Driver**: {what is pushing this evolution}
- **Capability required**: {what the organisation needs to execute}
- **Timeline estimate**: {urgency and duration}
- **Dependent impact**: {what changes for components above}
- **Dependency risk**: {what could block from below}

## Sequencing

{Which movements must happen first? Are there dependencies between
the evolve arrows themselves? If component A's evolution depends on
component B having already moved, that sequencing is critical.
Propose an order of execution.}

## Combined impact

{What does the map look like after all movements complete? What is
the "future state" shape? Does the overall structure become more
commoditised, more differentiated, or shift its centre of gravity?}

## Inertia conflicts

{Which evolving components also carry inertia markers? These are the
hardest changes -- the strategy says "move" but something resists.
What is the resistance? What would it take to overcome it?}

## Resource implications

{What does executing all these movements simultaneously require?
Is it realistic or does the organisation need to phase the changes?}
```

## Step 5: Render

After writing the `.owm` file, render it to SVG:
```
bin/ensure-owm.sh clients/{org}/projects/{slug}/atlas/movement/map.owm
```

Then regenerate the deliverable site:
```
bin/render-site.sh clients/{org}/projects/{slug}/
```

## Output

- `atlas/movement/map.owm` -- focused movement map
- `atlas/movement/map.svg` -- rendered visualisation
- `atlas/movement/analysis.md` -- movement and change programme analysis

## Guidelines

- **Show only what moves and what is touched by movement.** This is not
  the full map. It is a change programme overlay.
- **Make the arrows the star.** The evolve arrows are the point. Every
  annotation and note should help the reader understand why something
  moves and what that means.
- **Sequence matters.** If the analysis cannot propose an execution order,
  it is incomplete. Movements have dependencies.
- **Inertia + evolve = tension.** Where both appear on the same
  component, that is the most important thing on the map. Highlight it.
