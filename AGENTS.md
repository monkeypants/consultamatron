# Consultamatron: Multi-Product Consulting Practice

This repository contains agent skills for conducting strategic consulting
engagements. Skills are organised into **skillsets** (product lines) that
share a common client workspace and research base.

## Architecture

```
org-research → engage → {skillset pipeline} → review
```

1. **org-research** gathers information about a client organisation
2. **engage** plans which projects to run and in what order
3. Each project follows its skillset's pipeline
4. **review** captures lessons learned and raises improvement issues

Skills read from `skillsets/*.md` manifests to discover available
products and their pipelines.

## Available skillsets

| Skillset | Skills | Output |
|----------|--------|--------|
| Wardley Mapping (core) | wm-research, wm-needs, wm-chain, wm-evolve, wm-strategy, wm-iterate | OWM map files |
| Wardley Mapping (atlas) | wm-atlas-overview, wm-atlas-anchor-chains, wm-atlas-need-traces, wm-atlas-bottlenecks, wm-atlas-shared-components, wm-atlas-layers, wm-atlas-plays, wm-atlas-sourcing, wm-atlas-movement, wm-atlas-inertia, wm-atlas-flows, wm-atlas-forces, wm-atlas-doctrine, wm-atlas-risk, wm-atlas-teams, wm-atlas-pipelines, wm-atlas-evolution-mismatch | Focused OWM maps + analysis |
| Wardley Mapping (tours) | wm-tour-investor, wm-tour-technical, wm-tour-executive, wm-tour-operations, wm-tour-onboarding, wm-tour-competitive | Curated presentations |
| Business Model Canvas | bmc-research, bmc-segments, bmc-canvas, bmc-iterate | Structured markdown canvas |

See `skillsets/` for full pipeline definitions, gates, and project
directory structures.

## Shared skills

| Skill | Purpose |
|-------|---------|
| org-research | Research an organisation from public sources |
| engage | Plan engagements, create projects, direct next steps |
| editorial-voice | Rewrite artifacts in Consultamatron's editorial voice |
| review | Post-implementation review of completed projects, producing sanitised GitHub issues |

## Operator workspace

The operator's working directory has three layers, each `.gitignored`
by the commons repository:

```
consultamatron/                       # commons (public repo)
├── clients/                          # operator-private client workspaces
│   └── {org-slug}/
│       ├── resources/                # Shared research (managed by org-research)
│       ├── projects/                 # One directory per project
│       ├── review.md                 # Engagement-level review synthesis
│       └── engagement.md            # Cross-project engagement history
└── partnerships/                     # operator-private partnership repos
    ├── {personal-vault}/             # personal proprietary skills
    └── {partnership}/                # shared proprietary skills
```

`clients/` and `partnerships/` are typically private git repositories
cloned into these `.gitignored` directories. See `GETTING_STARTED.md`
for setup instructions.

See `org-research/assets/workspace-layout.md` for the full client
workspace directory structure including per-skillset project layouts.

Before starting any skill, check `clients/` for existing engagements.
If work already exists for an organisation, resume from where it left
off. Read `engagement.md` and project `decisions.md` files to understand
what has already been agreed.

## Partnership skillsets

Operators may have proprietary skillsets in `partnerships/`. Each
partnership subdirectory is an independent git repository containing:

```
partnerships/{name}/
├── skillsets/{domain}.md             # skillset manifest (same format as commons)
├── resources/{topic}.md              # proprietary domain knowledge
├── skills/{skill-name}/SKILL.md      # partnership skills (same format as commons)
└── reviews/                          # de-cliented engagement findings
```

The `engage` skill discovers partnership skillsets by reading
`partnerships/*/skillsets/*.md` alongside commons `skillsets/*.md`.
Partnership skills are injected at three points in the engagement
pipeline:

- **Partner-1** (after plan, before execute): domain enrichment
- **Partner-2** (after synthesis, before delivery): domain enhancement
- **Partner-3** (after delivery): domain-specific finishing

If no partnerships are configured, these injection points are skipped
and the pipeline matches the commons-only flow.

## Gate protocol

The `.agreed.md` and `.agreed.owm` suffixes mean the client has explicitly
confirmed the artifact. Skills create these only after the client says the
output is acceptable. Never create a gate artifact without client
agreement.

Each skillset defines its own gate sequence. Gates are relative to the
project directory. See `skillsets/*.md` for the specific gates per
skillset.

## OWM rendering

Wardley Mapping stages 4+ produce `.owm` map files. To render to SVG:
```
bin/ensure-owm.sh path/to/map.owm
```

This script checks for `cli-owm`, installs it via npm if missing, and
writes an SVG next to the OWM file. Node.js (npx) is required. Always
render after writing or updating an OWM file so the client can see the
visual map.

## Artifact format discipline

- **Organisation research**: Markdown with citations
- **Wardley Mapping stages 1-3**: Markdown only. The evolution axis is
  unknown, so OWM would impose false precision.
- **Wardley Mapping stage 1 exception**: `landscape.owm` is a coarse
  sketch acknowledged as approximate.
- **Wardley Mapping stages 4-5**: OWM files. Both axes have grounded
  meaning.
- **Wardley Mapping atlas**: OWM projections of the strategy map plus
  analytical markdown. Same coordinates as the comprehensive map.
- **Wardley Mapping tours**: Markdown prose in the Consultamatron
  editorial voice. Tours reference atlas content, not duplicate it.
- **Business Model Canvas**: Markdown throughout. BMC has no meaningful
  second axis.

## Site generation

After any skill completes (or after manual edits to workspace artifacts),
regenerate the deliverable site:

```
bin/render-site.sh clients/{org-slug}/
```

This produces a self-contained static HTML site in the workspace's `site/`
directory, suitable for sharing with stakeholders. The site renderer
detects which projects exist and dispatches to per-skillset renderers.

## Client-in-the-loop

Every skill follows a propose-negotiate-agree loop. The agent proposes
output, presents it to the user, incorporates feedback, and only writes
the gate artifact when the user confirms. The agent never decides that
output is "good enough" on its own.

## Choosing the right skill

- "Research this organisation" / "What do we know about X?" →
  **org-research**
- "What should we do for this client?" / "Plan the engagement" →
  **engage**
- "Start a Wardley Map" / "Map this organisation" →
  **wm-research** (after org-research)
- "What are the user needs?" →
  **wm-needs**
- "How does the organisation deliver this?" →
  **wm-chain**
- "Where are these components on the evolution axis?" →
  **wm-evolve**
- "What strategic moves should we make?" →
  **wm-strategy**
- "Update the map" / "This component feels wrong" →
  **wm-iterate**
- "Generate the atlas" / "Produce all derived views" →
  **wm-atlas-*** (run all applicable atlas skills)
- "Create the investor presentation" / "Make a tour for the board" →
  **wm-tour-{audience}**
- "Generate all presentations" →
  **wm-tour-*** (run all applicable tour skills)
- "Start a Business Model Canvas" / "What's their business model?" →
  **bmc-research** (after org-research)
- "Who are the customer segments?" →
  **bmc-segments**
- "Build the full canvas" →
  **bmc-canvas**
- "Update the canvas" →
  **bmc-iterate**
- "Rewrite this in the right voice" →
  **editorial-voice**
- "How did that go?" / "Review the project" / "Lessons learned" →
  **review**

If the user's request is ambiguous, check which gate artifacts exist in
the workspace to determine where the engagement is and which skill applies.

## What is Wardley Mapping

Wardley Mapping is a strategy method that maps the components needed to
serve user needs, positioned by visibility (how visible to the user) on
the Y-axis and evolution (how mature, from genesis to commodity) on the
X-axis. The method was created by Simon Wardley. The Wardley Mapping
skillset encodes a structured approach to producing these maps.

## What is Business Model Canvas

The Business Model Canvas is a strategic management tool that describes
a business model through nine building blocks: Customer Segments, Value
Propositions, Channels, Customer Relationships, Revenue Streams, Key
Resources, Key Activities, Key Partnerships, and Cost Structure. It was
developed by Alexander Osterwalder and Yves Pigneur.
