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

| Order | Skill | Prerequisite gate | Produces gate | Description |
|-------|-------|-------------------|---------------|-------------|
| 1 | wm-research | `resources/index.md` | `brief.agreed.md` | Project kickoff: scope agreement, landscape sketch |
| 2 | wm-needs | `brief.agreed.md` | `needs/needs.agreed.md` | Identify user classes and their needs |
| 3 | wm-chain | `needs/needs.agreed.md` | `chain/supply-chain.agreed.md` | Decompose needs into supply chains |
| 4 | wm-evolve | `chain/supply-chain.agreed.md` | `evolve/map.agreed.owm` | Position components on evolution axis |
| 5 | wm-strategy | `evolve/map.agreed.owm` | `strategy/map.agreed.owm` | Add strategic annotations |
| 6+ | wm-iterate | any `.owm` file | updated `.owm` file | Refine existing maps |

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
└── decisions.md
```

## Project slug convention

`maps-{n}` (e.g. `maps-1`, `maps-2`)

## Artifact format discipline

- **Skills 1-3** (wm-research through wm-chain): Markdown only. The
  evolution axis is unknown, so OWM would impose false precision.
- **Exception**: `landscape.owm` is a coarse sketch acknowledged as
  approximate. It provides orientation, not commitment.
- **Skills 4+** (wm-evolve onward): OWM files. Both axes have grounded
  meaning.

## OWM rendering

After writing or updating any `.owm` file, render to SVG:
```
bin/ensure-owm.sh path/to/map.owm
```

## What it produces

OWM files (plain-text DSL for Wardley Maps), renderable to SVG or
pasteable into [onlinewardleymaps.com](https://onlinewardleymaps.com).
