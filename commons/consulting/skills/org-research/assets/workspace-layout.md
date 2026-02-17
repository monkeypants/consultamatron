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
│   ├── index.md                   # L0 semantic bytecode root (gate artifact)
│   ├── strategy.agreed.md         # Agreed research strategy (Gate 1)
│   ├── summary_prose.md           # Human-friendly synthesis → reports/
│   ├── reports/                   # Primary research (token-inefficient)
│   │   ├── corporate-overview.md
│   │   ├── products-services.md
│   │   ├── technology-landscape.md
│   │   ├── market-position.md
│   │   ├── regulatory-environment.md
│   │   └── partnerships-suppliers.md
│   └── bytecode/                  # Semantic bytecode (token-efficient)
│       ├── {cluster}.md           # L1 cluster summaries → L2
│       └── {detail}.md            # L2 compressed detail → reports/
│
├── engagements/
│   ├── index.json                 # Engagement registry (status, sources, dates)
│   │
│   └── {engagement-slug}/         # One directory per engagement
│       ├── projects.json          # Project registry (status, skillset, dates)
│       │
│       └── {project-slug}/        # One directory per project
│           ├── brief.agreed.md    # Project scope agreed with client
│           ├── decisions.json     # Running log of client agreements
│           └── ...                # Skillset-specific artifacts
│
├── engagement-log.json            # Cross-engagement audit trail
└── review.md                      # Engagement-level review synthesis
```

Research is client-scoped — you research the organisation, not the
engagement. Multiple engagements share the same research base.
Projects are engagement-scoped. The audit log spans all engagements.

### Wardley Mapping project structure

```
engagements/{engagement}/{slug}/
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
│       ├── manifest.json          # Selected atlas entries + sequence
│       ├── opening.md             # Audience framing (Consultamatron voice)
│       └── transitions/
│           └── NN-{slug}.md       # Connective prose between atlas entries
├── review/                        # Post-implementation review
│   ├── review.md                  # Private review (not shared)
│   └── findings.md                # Sanitised findings for GitHub issues
└── decisions.json
```

### Business Model Canvas project structure

```
engagements/{engagement}/{slug}/
├── brief.agreed.md
├── hypotheses.md                  # Initial hypotheses for 9 BMC blocks
├── segments/
│   ├── drafts/{segment-slug}.md
│   ├── segments.md
│   └── segments.agreed.md
├── canvas.md                      # Full 9-block canvas
├── canvas.agreed.md
├── review/                        # Post-implementation review
│   ├── review.md                  # Private review (not shared)
│   └── findings.md                # Sanitised findings for GitHub issues
└── decisions.json
```

## Gate Protocol

Each skill produces a gate artifact when the client confirms the output.
Gate artifacts use `.agreed.md` or `.agreed.owm` suffixes. Subsequent
skills check for their prerequisite gates before proceeding.

### Shared gates

| Skill | Requires | Produces |
|-------|----------|----------|
| org-research | (nothing) | `resources/index.md` (via `strategy.agreed.md` internal gate) |
| engage | `resources/index.md` | engagement + project directories |

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

- **Research primary reports**: Markdown with citations (token-inefficient).
- **Research bytecode**: Compressed semantic hierarchy L0/L1/L2 (token-efficient).
  Downstream skills consume the bytecode; primary reports are for evidence tracing.
- **Wardley Mapping stages 1-3** (needs, chain): Markdown only. The
  evolution axis is unknown, so OWM would impose false precision.
- **Wardley Mapping project kickoff exception**: `landscape.owm` is a
  coarse sketch acknowledged as approximate.
- **Wardley Mapping stages 4+** (evolve, strategy, iterate): OWM files.
  Both axes have grounded meaning.
- **Business Model Canvas**: Markdown throughout. BMC has no meaningful
  second axis that would warrant a specialised format.

## The decisions.json Log

Every project has a `decisions.json` file. Every client agreement is
appended as a JSON entry with id, date, timestamp, title, and fields.
The CLI manages this file — do not edit by hand.

## The engagement-log.json Log

The client-level `engagement-log.json` tracks cross-engagement history:
research refreshes, engagement creation, project starts, project
completions, and any strategic decisions that span engagements.

## Review Artifacts

The `review` skill produces two artifacts per project:

- **`review/review.md`**: Private review containing client-specific
  observations, interview transcripts, and findings. Never shared
  outside the workspace. Its existence signals that the project has
  been reviewed.
- **`review/findings.md`**: Sanitised findings suitable for GitHub
  issues. All client-identifying information is removed.

If multiple projects are reviewed in the same engagement, a client-level
**`review.md`** captures cross-project patterns and engagement-wide
synthesis.
