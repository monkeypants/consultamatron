---
name: wm-atlas-sourcing
description: >
  Generate a sourcing-focused map showing all components decorated with
  build/buy/outsource strategies. Groups components by execution strategy
  and annotates vendor options and market alternatives from research.
  Produces atlas/sourcing/ with map and analysis.
compatibility: Requires Node.js (npx) for OWM rendering via cli-owm
metadata:
  author: monkeypants
  version: "0.1"
  skillset: wardley-mapping
  stage: "atlas"
  freedom: medium
---

# Atlas: Sourcing Strategy Map

You are generating a sourcing-focused view of the Wardley Map. This map
shows every component from the strategy map, decorated with its execution
strategy (build, buy, or outsource) and annotated with specific vendor
options and market alternatives.

## Prerequisites

Check that the project directory (`clients/{org}/projects/{project-slug}/`)
contains:
- `strategy/map.agreed.owm` -- the comprehensive strategy map
- `evolve/assessments/*.md` -- evolution assessments with stage evidence
- `chain/supply-chain.agreed.md` -- agreed component decomposition
- `strategy/plays/*.md` -- strategic plays with execution context
- `decisions.md`

If `strategy/map.agreed.owm` is missing, tell the user to complete
`wm-strategy` first.

## Staleness check

Check whether `atlas/sourcing/map.owm` already exists. If it does,
compare the modification times of:
- `strategy/map.agreed.owm`
- `evolve/assessments/*.md`
- `chain/supply-chain.agreed.md`

against `atlas/sourcing/map.owm`. If all source files are older than
the output, report that the sourcing atlas is up to date and skip
regeneration. If any source is newer, regenerate.

## Step 1: Extract sourcing data

Read `strategy/map.agreed.owm` and catalogue every component:

1. **Already decorated**: components with `(build)`, `(buy)`, or
   `(outsource)` decorators. Record these as-is.
2. **Undecorated**: components without an execution strategy. For each,
   infer the likely strategy from its evolution position:
   - Genesis/Custom (0.00-0.40): typically `build` (competitive
     differentiator, nothing to buy)
   - Product (0.40-0.70): could be `build` or `buy` depending on
     whether it differentiates
   - Commodity (0.70-1.00): typically `buy` or `outsource` (waste of
     effort to build)
3. **Evolving components**: if an evolve arrow moves a component into a
   different stage, note the sourcing implications of that movement.

## Step 2: Assess sourcing context from analytical artifacts

Read the analytical work from earlier stages:

1. **Evolution assessments** (`evolve/assessments/*.md`): The evolution
   stage evidence directly informs sourcing logic. Genesis/custom
   components are build candidates; product/commodity are buy/outsource
   candidates. The assessments contain the reasoning behind each
   positioning.
2. **Supply chain** (`chain/supply-chain.agreed.md`): Shows which
   components serve which needs, shared dependencies, and structural
   relationships that constrain sourcing decisions.
3. **Strategy plays** (`strategy/plays/*.md`): Plays may already
   contain build/buy/outsource recommendations with rationale. Use
   these as primary input rather than re-deriving from scratch.
4. **Decisions log** (`decisions.md`): Client agreements may include
   sourcing constraints or preferences expressed during earlier stages.

Then supplement from primary research (`resources/`) for:
- **Named vendors or products** not already surfaced in plays or
  assessments
- **Service providers** and contractual implications for outsource
  candidates
- **Market alternatives** for components where the assessment noted
  multiple vendors exist

## Step 3: Generate sourcing map

Read [owm-dsl-reference.md](../wm-evolve/references/owm-dsl-reference.md)
for OWM syntax.

Write `atlas/sourcing/map.owm` containing:
- A `title` (e.g. `title {Organisation} -- Sourcing Strategy`)
- All components from the strategy map, each with an explicit execution
  strategy decorator: `(build)`, `(buy)`, or `(outsource)`
- All dependencies from the strategy map (full structure preserved)
- Evolve arrows from the strategy map, with execution strategy changes
  where the sourcing shifts (e.g. `evolve Component 0.72 (buy)`)
- Notes annotating specific vendor recommendations or provider names
  adjacent to the relevant components
- Annotations highlighting the most important sourcing decisions
  (numbered, under 12 words each)
- `style wardley`

## Step 4: Write analysis

Write `atlas/sourcing/analysis.md`:

```markdown
# Sourcing Strategy

## Overview

{High-level summary: how many components in each category, what
percentage of the map is build vs buy vs outsource, and what that
implies about organisational capability needs.}

## Build components

{For each build component: why build? What skills and investment does
it require? Is it a genuine differentiator? Flag any that look like
they should be bought instead.}

## Buy components

{For each buy component: what are the specific vendor options? Name
vendors found in research. What are the selection criteria? What are
the lock-in risks? If multiple vendors exist, note the trade-offs.}

## Outsource components

{For each outsource component: what provider options exist? What
governance model is appropriate? What are the risks of dependency?}

## Evolution-sourcing alignment

{Which components have a sourcing strategy that matches their
evolution stage? Which are mismatched? Mismatches are the most
actionable finding -- a commodity being built in-house is waste,
a differentiator being outsourced is risk.}

## Sourcing changes from evolve arrows

{For components with evolve arrows: how does the movement change
the sourcing recommendation? If something evolves from Custom to
Product, does that mean switching from build to buy?}

## Cost and risk implications

{What does this sourcing picture imply about the organisation's
cost structure and risk exposure? Where is vendor concentration
a concern?}
```

## Step 5: Render

After writing the `.owm` file, render it to SVG:
```
bin/ensure-owm.sh clients/{org}/projects/{slug}/atlas/sourcing/map.owm
```

Then regenerate the deliverable site:
```
bin/render-site.sh clients/{org}/projects/{slug}/
```

## Output

- `atlas/sourcing/map.owm` -- full map with sourcing decorators
- `atlas/sourcing/map.svg` -- rendered visualisation
- `atlas/sourcing/analysis.md` -- sourcing analysis with vendor detail

## Guidelines

- **Every component gets a decorator.** The point of this view is that
  nothing is unclassified. If the strategy map left some ambiguous,
  make a reasoned assignment and flag it in the analysis.
- **Name names.** Generic "buy from a vendor" is useless. The research
  contains specific product and vendor names -- surface them.
- **Flag mismatches loudly.** Evolution-sourcing mismatches are the
  highest-value finding. Use `note +` emphasis for these on the map.
- **Preserve full structure.** Unlike play maps, the sourcing map
  includes everything. The value is in the decorators, not in
  filtering.
