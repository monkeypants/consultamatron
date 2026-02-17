---
name: wm-atlas-inertia
description: >
  Generate an inertia-focused map showing components marked with inertia,
  their dependents, and any evolve arrows acting on them. Highlights the
  tension between strategic intent and organisational resistance. Re-reads
  research for context on what causes each point of inertia. Produces
  atlas/inertia/ with map and analysis.
compatibility: Requires Node.js (npx) for OWM rendering via cli-owm
metadata:
  author: monkeypants
  version: "0.1"
  skillset: wardley-mapping
  stage: "atlas"
  freedom: medium
---

# Atlas: Inertia Map

You are generating an inertia-focused view of the Wardley Map. This map
isolates resistance to change -- every component marked with `inertia`,
the components that depend on it (and are therefore affected by the
resistance), and any evolve arrows that create tension against the
inertia. This is the "blockers and barriers" view.

## Prerequisites

Check that the project directory (`clients/{org}/projects/{project-slug}/`)
contains:
- `strategy/map.agreed.owm` -- the comprehensive strategy map
- `evolve/assessments/*.md` -- evolution assessments (contain inertia analysis)
- `strategy/plays/*.md` -- strategic plays (show tension with inertia)
- `chain/supply-chain.agreed.md` -- dependency structure
- `decisions.md`

If `strategy/map.agreed.owm` is missing, tell the user to complete
`wm-strategy` first.

## Staleness check

Check whether `atlas/inertia/map.owm` already exists. If it does,
compare the modification times of:
- `strategy/map.agreed.owm`
- All files in `evolve/assessments/`
- `strategy/plays/*.md`

against `atlas/inertia/map.owm`. If all source files are older than
the output, report that the inertia atlas is up to date and skip
regeneration. If any source is newer, regenerate.

## Step 1: Extract inertia components

Read `strategy/map.agreed.owm` and identify:

1. **Every component with `inertia`** -- these are the focal points.
2. **Direct dependents** of each inertia component (one level up, and
   recursively up to the anchors). These components are affected by
   the inertia -- they cannot fully evolve or be optimised while
   the inertia-marked component resists movement.
3. **Direct dependencies** of each inertia component (one level down).
   These may be contributing to the inertia (e.g. locked-in
   infrastructure preventing a capability from evolving).
4. **Evolve arrows on inertia components** -- the most critical
   finding. An evolve arrow on an inertia component means the
   strategy says "move this" but something is resisting. This
   tension is the whole point of the map.
5. **Evolve arrows on dependents of inertia components** -- secondary
   tension. A dependent that wants to evolve but cannot because the
   thing below it is stuck.

Omit components, dependencies, and annotations that do not relate to
inertia points or their dependency context.

## Step 2: Analyse inertia causes from analytical artifacts

For each inertia-marked component, read the analytical work from
earlier stages:

1. **Evolution assessments** (`evolve/assessments/*.md`): The inertia
   section in each assessment is the primary source. It should describe
   the resistance signal and its type. This was written with the
   client's input and represents agreed understanding.
2. **Strategy plays** (`strategy/plays/*.md`): Which plays propose
   moving inertia-marked components? The play's impact and evidence
   sections contain reasoning about what the inertia blocks.
3. **Decisions log** (`decisions.md`): Were inertia points discussed
   during client agreements? The client may have confirmed or
   elaborated on the causes during evolution or strategy sign-off.
4. **Supply chain** (`chain/supply-chain.agreed.md`): Where does the
   inertia-marked component sit structurally? What depends on it?

Classify each inertia point by type: contractual lock-in, skills
lock-in, capital lock-in, cultural attachment, political resistance,
regulatory constraint, or ecosystem dependency.

Supplement from primary research (`resources/`) only where the
analytical artifacts lack specific detail on the cause (e.g. contract
terms or regulatory specifics not captured in assessments).

## Step 3: Generate inertia map

Read [owm-dsl-reference.md](../wm-evolve/references/owm-dsl-reference.md)
for OWM syntax.

Write `atlas/inertia/map.owm` containing:
- A `title` (e.g. `title {Organisation} -- Inertia and Resistance`)
- Inertia-marked components at their original positions, preserving
  the `inertia` keyword
- Dependents and dependencies identified in Step 1
- Evolve arrows that act on inertia components or their dependents
- Annotations identifying the type and cause of each inertia point
  (numbered, under 12 words each)
- Notes with `+` emphasis on components where evolve and inertia
  co-occur -- these are the highest-tension points
- `style wardley`

## Step 4: Write analysis

Write `atlas/inertia/analysis.md`:

```markdown
# Inertia Analysis

## Overview

{How many inertia points exist? How many also have evolve arrows
(tension points)? What is the overall picture -- is the map mostly
fluid with a few stuck points, or is inertia pervasive?}

## Tension points: evolve vs inertia

{For each component that has BOTH an evolve arrow and an inertia
marker, write a dedicated section. These are the most important
findings.}

### {Component Name}

- **Current position**: {maturity} ({stage})
- **Target position**: {evolve target} ({stage})
- **Inertia type**: {contractual / skills / capital / cultural /
  political / regulatory / ecosystem}
- **Inertia detail**: {specific cause from research and assessments}
- **Dependent impact**: {what is blocked by this inertia -- trace
  up the value chain}
- **Cost of inaction**: {what happens if this component does NOT
  move despite the strategic intent}
- **Mitigation options**: {what could overcome the resistance --
  contract renegotiation, retraining, phased migration, etc.}

## Inertia without evolve arrows

{Components marked inertia but without evolve arrows. The strategy
has not proposed moving these. Are they correctly left alone, or has
the strategy overlooked them? Should they have evolve arrows?}

## Cascade effects

{Trace the impact chains. If inertia component X blocks the
evolution of dependent Y, and Y's evolution is needed for play Z,
then X's inertia undermines play Z. Map these cascades explicitly.}

## Prioritised mitigation

{Rank the inertia points by impact. Which ones block the most
strategic value? Which are easiest to overcome? Recommend a
sequence for addressing them.}

## Organisational implications

{What does the inertia picture say about the organisation's
readiness for change? Is inertia concentrated in one area (e.g.
infrastructure) or distributed? Does it require a single large
initiative or many small ones?}
```

## Step 5: Render

After writing the `.owm` file, render it to SVG:
```
bin/ensure-owm.sh clients/{org}/projects/{slug}/atlas/inertia/map.owm
```

Then regenerate the deliverable site:
```
bin/render-site.sh clients/{org}/projects/{slug}/
```

## Output

- `atlas/inertia/map.owm` -- focused inertia map
- `atlas/inertia/map.svg` -- rendered visualisation
- `atlas/inertia/analysis.md` -- inertia analysis with mitigation options

## Guidelines

- **Tension is the point.** A component with inertia but no evolve arrow
  is interesting. A component with both is critical. Weight the analysis
  accordingly.
- **Name the cause.** "This has inertia" is not analysis. "This has
  inertia because of a 5-year Oracle contract expiring in 2027" is.
  The research and assessments contain this detail -- surface it.
- **Trace the cascades.** Inertia on a low-visibility component can
  block strategic plays at the top of the map. Make these chains
  explicit so the reader understands the true cost.
- **Include dependents generously.** Unlike play maps which omit
  aggressively, inertia maps should trace upward to show what is
  affected. The reader needs to see the blast radius.
- **Do not propose removing inertia markers.** This is an atlas view,
  not an editing skill. The inertia markers were agreed in earlier
  stages. The analysis explains them; it does not change them.
