# Wardley Mapping Skills

This repository contains a set of agent skills for conducting Wardley
Mapping engagements. The skills form a staged pipeline, not a pick-and-mix
menu.

## The pipeline

| Stage | Skill | Input gate | Output gate |
|-------|-------|-----------|-------------|
| 1 | wm-research | (none) | `1-research/summary.md` |
| 2 | wm-needs | `1-research/summary.md` | `2-needs/needs.agreed.md` |
| 3 | wm-chain | `2-needs/needs.agreed.md` | `3-chain/supply-chain.agreed.md` |
| 4 | wm-evolve | `3-chain/supply-chain.agreed.md` | `4-evolve/map.agreed.owm` |
| 5 | wm-strategy | `4-evolve/map.agreed.owm` | `5-strategy/map.agreed.owm` |
| 6+ | wm-iterate | any `.owm` file | updated `.owm` file |

Each stage requires its input gate artifact to exist before it will
proceed. Do not skip stages. Do not run a skill if its gate is missing —
tell the user which skill to run first.

## Gate protocol

The `.agreed.md` and `.agreed.owm` suffixes mean the client has explicitly
confirmed the artifact. Skills create these only after the client says the
output is acceptable. Never create a gate artifact without client
agreement.

## Workspace

All skills operate on a shared workspace at `./maps/{org-slug}/` (the user
may specify an alternative). The workspace is created by wm-research.
See `wm-research/assets/workspace-layout.md` for the full directory
structure.

Before starting any skill, check `maps/` for existing engagements. If work
already exists for an organisation, resume from where it left off rather
than starting over. Read `decisions.md` in the workspace to understand what
has already been agreed.

## OWM rendering

Stages 4+ produce `.owm` map files. To render these to SVG, run:
```
bin/ensure-owm.sh path/to/map.owm
```

This script checks for `cli-owm`, installs it via npm if missing, and
writes an SVG next to the OWM file. Node.js (npx) is required. Always
render after writing or updating an OWM file so the client can see the
visual map.

## Artifact format discipline

Stages 1-3 produce **markdown only**. The evolution axis is unknown at
these stages, so OWM files would require guessing half the coordinates.
Markdown dependency trees are the honest representation.

Stage 1 produces one exception: `landscape.owm`, a coarse sketch
acknowledged as approximate. It is orientation, not commitment.

Stages 4+ produce **OWM files**. Both axes (visibility and evolution) have
grounded meaning at this point. The OWM DSL reference is bundled in
`wm-evolve/references/owm-dsl-reference.md`.

## Site generation

After any skill completes (or after manual edits to workspace artifacts),
regenerate the deliverable site:

```
bin/render-site.sh maps/{org-slug}/
```

This produces a self-contained static HTML site in the workspace's `site/`
directory, suitable for sharing with stakeholders.

## Client-in-the-loop

Every skill follows a propose-negotiate-agree loop. The agent proposes
output, presents it to the user, incorporates feedback, and only writes
the gate artifact when the user confirms. The agent never decides that
output is "good enough" on its own.

## Choosing the right skill

- "Map this organisation" / "Research X for mapping" → **wm-research**
- "What are the user needs?" / picking up after research → **wm-needs**
- "How does the organisation deliver this?" / decompose needs → **wm-chain**
- "Where are these components on the evolution axis?" → **wm-evolve**
- "What strategic moves should we make?" → **wm-strategy**
- "This component feels wrong" / "Update the map" / any refinement of an
  existing map → **wm-iterate**

If the user's request is ambiguous, check which gate artifacts exist in the
workspace to determine where the engagement is and which skill applies.

## What is Wardley Mapping

Wardley Mapping is a strategy method that maps the components needed to
serve user needs, positioned by visibility (how visible to the user) on
the Y-axis and evolution (how mature, from genesis to commodity) on the
X-axis. The method was created by Simon Wardley. These skills encode a
structured approach to producing Wardley Maps through research,
stakeholder agreement, and iterative refinement.
