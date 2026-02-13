# Wardley Mapping Workspace Layout

All skills in this methodology operate on a shared **workspace directory**.
The workspace is created by `wm-research` and consumed by subsequent skills.

## Convention

The default workspace path is `./maps/{org-slug}/` relative to the
project root. The user may specify an alternative path.

## Directory Structure

```
maps/{org-slug}/
├── 1-research/
│   ├── tasks/                     # Parallel sub-reports with citations
│   │   ├── corporate-overview.md
│   │   ├── products-services.md
│   │   ├── technology-landscape.md
│   │   ├── market-position.md
│   │   ├── regulatory-environment.md
│   │   ├── partnerships-suppliers.md
│   │   └── ...
│   ├── summary.md                 # Synthesised from all sub-reports
│   └── landscape.owm              # Coarse enterprise-level map (~10-15 components)
│
├── 2-needs/
│   ├── drafts/                    # Per-user-class working drafts
│   │   ├── {user-class-slug}.md
│   │   └── ...
│   ├── needs.md                   # Consolidated needs proposal
│   └── needs.agreed.md            # After client sign-off
│
├── 3-chain/
│   ├── chains/                    # Per-need dependency trees
│   │   ├── {need-slug}.md
│   │   └── ...
│   ├── supply-chain.md            # Consolidated dependency graph
│   └── supply-chain.agreed.md     # After client sign-off
│
├── 4-evolve/
│   ├── assessments/               # Per-cluster evolution reasoning
│   │   ├── {cluster-slug}.md
│   │   └── ...
│   ├── map.owm                    # First positioned Wardley Map (OWM)
│   └── map.agreed.owm             # After client sign-off
│
├── 5-strategy/
│   ├── plays/                     # Individual strategic analyses
│   │   ├── {play-slug}.md
│   │   └── ...
│   ├── map.owm                    # Strategy-annotated OWM
│   └── map.agreed.owm             # After client sign-off
│
└── decisions.md                   # Running log of all client agreements
```

## Stage Gates

Each stage produces a `.agreed.md` or `.agreed.owm` artifact when the
client confirms the output. Subsequent skills check for these gate
artifacts before proceeding.

| Skill      | Requires                          | Produces                        |
|------------|-----------------------------------|---------------------------------|
| wm-research | (nothing)                        | `1-research/summary.md`        |
| wm-needs   | `1-research/summary.md`          | `2-needs/needs.agreed.md`      |
| wm-chain   | `2-needs/needs.agreed.md`        | `3-chain/supply-chain.agreed.md` |
| wm-evolve  | `3-chain/supply-chain.agreed.md` | `4-evolve/map.agreed.owm`      |
| wm-strategy | `4-evolve/map.agreed.owm`       | `5-strategy/map.agreed.owm`    |
| wm-iterate | Any existing `.owm` file          | Updated `.owm` file            |

## Artifact Formats

- **Stages 1-3**: Markdown only. These stages lack evolution positioning,
  so OWM would impose false precision. Markdown dependency trees honestly
  represent what is known (visibility/depth) without what is not (evolution).
- **Stage 1 exception**: `landscape.owm` is a coarse sketch acknowledged
  as approximate. It provides early visual orientation, not commitment.
- **Stages 4+**: OWM files. Both axes (visibility and evolution) now
  have grounded meaning.

## The decisions.md Log

Every client agreement is appended to `decisions.md` with:

```markdown
## {Date} — {Stage}: {Brief description}

**Agreed**: {What was agreed}
**Context**: {Why / any caveats}
```

This provides an audit trail of the mapping engagement.
