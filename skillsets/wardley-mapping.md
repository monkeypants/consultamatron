---
name: wardley-mapping
display_name: Wardley Mapping
description: >
  Strategic mapping methodology that positions components by visibility
  to the user and evolutionary maturity. Produces OWM map files suitable
  for strategic decision-making.
---

# Wardley Mapping

Wardley Mapping is a strategy method created by Simon Wardley. It maps
the components needed to serve user needs, positioned by visibility (how
visible to the user) on the Y-axis and evolution (how mature, from
genesis to commodity) on the X-axis.

## Pipeline

### Core pipeline (client-in-the-loop)

| Order | Skill | Prerequisite gate | Produces gate | Description |
|-------|-------|-------------------|---------------|-------------|
| 1 | wm-research | `resources/index.md` | `brief.agreed.md` | Project kickoff: scope agreement, landscape sketch |
| 2 | wm-needs | `brief.agreed.md` | `needs/needs.agreed.md` | Identify user classes and their needs |
| 3 | wm-chain | `needs/needs.agreed.md` | `chain/supply-chain.agreed.md` | Decompose needs into supply chains |
| 4 | wm-evolve | `chain/supply-chain.agreed.md` | `evolve/map.agreed.owm` | Position components on evolution axis |
| 5 | wm-strategy | `evolve/map.agreed.owm` | `strategy/map.agreed.owm` | Add strategic annotations |
| 6+ | wm-iterate | any `.owm` file | updated `.owm` file | Refine existing maps |

### Atlas (derived views, no client gate)

Atlas skills derive focused views from the comprehensive strategy map.
Each produces OWM map files and analytical prose in `atlas/{topic}/`.
Run all applicable atlas skills after strategy is agreed, or after
wm-iterate changes the comprehensive map. Skills check staleness and
skip if their output is newer than the source map.

| Skill | Input | Focus |
|-------|-------|-------|
| wm-atlas-overview | strategy map | Simplified landscape with submaps |
| wm-atlas-anchor-chains | strategy map, needs | Per-user-class value chain |
| wm-atlas-need-traces | strategy map, chain | Per-need supply chain trace |
| wm-atlas-bottlenecks | strategy map | High-fan-in components, blast radius |
| wm-atlas-shared-components | strategy map, chain | Components serving multiple chains |
| wm-atlas-layers | strategy map | Depth-separated views (user, capabilities, infrastructure) |
| wm-atlas-plays | strategy map, plays | Per-strategic-play focused maps |
| wm-atlas-sourcing | strategy map, research | Build/buy/outsource with vendor analysis |
| wm-atlas-movement | strategy map, evolve | Evolution arrows and change programme |
| wm-atlas-inertia | strategy map, evolve | Change resistance and tension |
| wm-atlas-flows | strategy map | Flow links and feedback loops |
| wm-atlas-forces | strategy map, research | Accelerators, decelerators, market dynamics |
| wm-atlas-doctrine | strategy map, all artifacts | Wardley doctrine assessment |
| wm-atlas-risk | strategy map, chain, research | Risk clusters and mitigation |
| wm-atlas-teams | strategy map | Pioneers/Settlers/Town Planners overlay |
| wm-atlas-pipelines | strategy map, evolve, research | Pipeline candidates and migration paths |
| wm-atlas-evolution-mismatch | strategy map | Sourcing vs evolution stage mismatches |

### Tours (curated presentations)

Tour skills select atlas entries, sequence them for a specific audience,
and write connective prose in the Consultamatron editorial voice.
Output goes to `presentations/{tour-name}/`.

| Skill | Audience | Arc |
|-------|----------|-----|
| wm-tour-investor | Investors | Defensibility, flywheel, growth, risk |
| wm-tour-technical | Technical leadership | Architecture, layers, sourcing, teams |
| wm-tour-executive | Board and C-suite | Risk, inertia, movement, doctrine |
| wm-tour-operations | Delivery teams | Sourcing, bottlenecks, teams, priorities |
| wm-tour-onboarding | New team members | Landscape, users, structure, dynamics |
| wm-tour-competitive | Strategy team | Forces, movement, positioning, plays |

All gates are relative to the project directory:
`clients/{org}/projects/{project-slug}/`.

## Project directory structure

```
projects/{slug}/
├── brief.agreed.md
├── landscape.owm
├── needs/
│   ├── drafts/{user-class-slug}.md
│   ├── needs.md
│   └── needs.agreed.md
├── chain/
│   ├── chains/{need-slug}.md
│   ├── supply-chain.md
│   └── supply-chain.agreed.md
├── evolve/
│   ├── assessments/{cluster-slug}.md
│   ├── map.owm
│   └── map.agreed.owm
├── strategy/
│   ├── plays/{play-slug}.md
│   ├── map.owm
│   └── map.agreed.owm
├── atlas/
│   └── {topic}/                     # One directory per atlas view
│       ├── map.owm                  # Focused map (subset of strategy map)
│       ├── map.svg
│       └── analysis.md              # Analytical prose
├── presentations/
│   └── {tour-name}/                 # One directory per audience tour
│       ├── manifest.md              # Selected atlas entries + order
│       ├── opening.md               # Audience-specific framing (in voice)
│       └── transitions/             # Connective prose between entries
│           └── NN-{slug}.md
├── review/                         # Post-implementation review
│   ├── review.md                   # Private review (not shared)
│   └── findings.md                 # Sanitised findings for GitHub issues
└── decisions.md
```

## Project slug convention

`maps-{n}` (e.g. `maps-1`, `maps-2`)

## Artifact format discipline

- **Skills 1-3** (wm-research through wm-chain): Markdown only. The
  evolution axis is unknown, so OWM would impose false precision.
- **Exception**: `landscape.owm` is a coarse sketch acknowledged as
  approximate. It provides orientation, not commitment.
- **Skills 4-5** (wm-evolve, wm-strategy): OWM files. Both axes have
  grounded meaning.
- **Atlas**: OWM files (projections of the strategy map) plus analytical
  markdown. Atlas maps use the same coordinates as the comprehensive map
  for consistency.
- **Tours**: Markdown prose in the Consultamatron editorial voice. Tours
  reference atlas content, they do not duplicate it.

## OWM rendering

After writing or updating any `.owm` file, render to SVG:
```
bin/ensure-owm.sh path/to/map.owm
```

## What it produces

OWM files (plain-text DSL for Wardley Maps), renderable to SVG or
pasteable into [onlinewardleymaps.com](https://onlinewardleymaps.com).
