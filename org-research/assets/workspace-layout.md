# Client Workspace Layout

All skills operate on a shared **client workspace**. The workspace is
created by `org-research` and consumed by all downstream skills.

## Convention

The default workspace path is `./clients/{org-slug}/` relative to the
project root. The user may specify an alternative path.

## Directory Structure

```
clients/{org-slug}/
├── resources/                     # Shared research, refreshed over time
│   ├── index.md                   # Manifest + synthesis (gate artifact)
│   ├── corporate-overview.md
│   ├── products-services.md
│   ├── technology-landscape.md
│   ├── market-position.md
│   ├── regulatory-environment.md
│   └── partnerships-suppliers.md
│
├── projects/
│   ├── index.md                   # Project registry (status, type, dates)
│   │
│   ├── {project-slug}/            # One directory per project
│   │   ├── brief.agreed.md        # Project scope agreed with client
│   │   ├── decisions.md           # Running log of client agreements
│   │   └── ...                    # Skillset-specific artifacts
│   └── ...
│
└── engagement.md                  # Cross-project engagement history
```

### Wardley Mapping project structure

```
projects/{slug}/
├── brief.agreed.md
├── landscape.owm                  # Coarse sketch from project kickoff
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
├── strategy/                      # Comprehensive map (source of truth)
│   ├── plays/{play-slug}.md
│   ├── map.owm
│   └── map.agreed.owm
├── atlas/                         # Derived views (no client gate)
│   └── {topic}/
│       ├── map.owm                # Focused map (projection of strategy map)
│       ├── map.svg
│       └── analysis.md            # Analytical prose
├── presentations/                 # Audience-specific tours
│   └── {tour-name}/
│       ├── manifest.md            # Selected atlas entries + sequence
│       ├── opening.md             # Audience framing (Consultamatron voice)
│       └── transitions/
│           └── NN-{slug}.md       # Connective prose between atlas entries
└── decisions.md
```

### Business Model Canvas project structure

```
projects/{slug}/
├── brief.agreed.md
├── hypotheses.md                  # Initial hypotheses for 9 BMC blocks
├── segments/
│   ├── drafts/{segment-slug}.md
│   ├── segments.md
│   └── segments.agreed.md
├── canvas.md                      # Full 9-block canvas
├── canvas.agreed.md
└── decisions.md
```

## Gate Protocol

Each skill produces a gate artifact when the client confirms the output.
Gate artifacts use `.agreed.md` or `.agreed.owm` suffixes. Subsequent
skills check for their prerequisite gates before proceeding.

### Shared gates

| Skill | Requires | Produces |
|-------|----------|----------|
| org-research | (nothing) | `resources/index.md` |
| engage | `resources/index.md` | project directory + `projects/index.md` updated |

### Wardley Mapping gates (project-relative)

| Skill | Requires | Produces |
|-------|----------|----------|
| wm-research | `resources/index.md` | `brief.agreed.md` |
| wm-needs | `brief.agreed.md` | `needs/needs.agreed.md` |
| wm-chain | `needs/needs.agreed.md` | `chain/supply-chain.agreed.md` |
| wm-evolve | `chain/supply-chain.agreed.md` | `evolve/map.agreed.owm` |
| wm-strategy | `evolve/map.agreed.owm` | `strategy/map.agreed.owm` |
| wm-iterate | any `.owm` file | updated `.owm` file |
| wm-atlas-* | `strategy/map.agreed.owm` | `atlas/{topic}/` (no gate, derived) |
| wm-tour-* | `atlas/` entries | `presentations/{tour}/` (no gate, derived) |

### Business Model Canvas gates (project-relative)

| Skill | Requires | Produces |
|-------|----------|----------|
| bmc-research | `resources/index.md` | `brief.agreed.md` |
| bmc-segments | `brief.agreed.md` | `segments/segments.agreed.md` |
| bmc-canvas | `segments/segments.agreed.md` | `canvas.agreed.md` |
| bmc-iterate | `canvas.agreed.md` | updated `canvas.agreed.md` |

## Artifact Formats

- **Research**: Markdown with citations.
- **Wardley Mapping stages 1-3** (needs, chain): Markdown only. The
  evolution axis is unknown, so OWM would impose false precision.
- **Wardley Mapping project kickoff exception**: `landscape.owm` is a
  coarse sketch acknowledged as approximate.
- **Wardley Mapping stages 4+** (evolve, strategy, iterate): OWM files.
  Both axes have grounded meaning.
- **Business Model Canvas**: Markdown throughout. BMC has no meaningful
  second axis that would warrant a specialised format.

## The decisions.md Log

Every project has a `decisions.md` file. Every client agreement is
appended with:

```markdown
## {Date} — {Stage}: {Brief description}

**Agreed**: {What was agreed}
**Context**: {Why / any caveats}
```

This provides an audit trail of the engagement.

## The engagement.md Log

The client-level `engagement.md` tracks cross-project history:
research refreshes, project starts, project completions, and any
strategic decisions that span projects.
