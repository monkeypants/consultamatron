---
name: wm-tour-technical
description: >
  Curate atlas content into a narrative presentation for technical
  leadership evaluating architecture and build decisions. Selects and
  sequences atlas entries, writes connective prose in the Consultamatron
  voice, and produces a tour the site renderer can assemble.
metadata:
  author: monkeypants
  version: "0.1"
  skillset: wardley-mapping
  stage: "tour"
  freedom: medium
---

# Tour: Technical Leadership

You are assembling a presentation tour for technical leaders. The
audience evaluates architecture, build/buy decisions, structural risks,
and team allocation. They want to see the system as structure, not as
aspiration. They have opinions about architecture already. The map
either confirms or challenges those opinions, and both outcomes are
useful.

## Prerequisites

Check that the project directory (`clients/{org}/projects/{project-slug}/`)
contains the following atlas entries. Each must have both `map.owm` (or
`map.svg`) and `analysis.md`:

- `atlas/overview/`
- `atlas/layers/`
- `atlas/sourcing/`
- `atlas/anchor-chains/`
- `atlas/bottlenecks/`
- `atlas/teams/`

If any are missing, tell the user which atlas skills to run first. Do not
proceed with partial content.

## Audience

CTOs, VPs of Engineering, architects, and technical directors. They
care about:
- How the system is layered and where the boundaries are
- Which components to build, which to buy, which to outsource
- How user needs flow through the architecture
- Where structural risks concentrate (single points of failure,
  evolution mismatches, dependency bottlenecks)
- How teams should be organised around the structure

They appreciate precision. They distrust vagueness.

## Selection

Include atlas entries in this order:

| Order | Atlas entry | Section title |
|-------|-------------|---------------|
| 1 | `atlas/overview/` | Architecture at a glance |
| 2 | `atlas/layers/` | The layers |
| 3 | `atlas/sourcing/` | Build, buy, or outsource |
| 4 | `atlas/anchor-chains/` | How users experience the system |
| 5 | `atlas/bottlenecks/` | Structural risks |
| 6 | `atlas/teams/` | Who should work on what |

## Narrative arc

The presentation tells this story:

1. **Architecture.** The overview map shows the system as a whole. This
   is orientation before detail.
2. **Layers.** How the system decomposes by visibility and evolution.
   What sits at the surface, what sits in the middle, what sits at the
   foundation. Where the natural API boundaries are.
3. **Sourcing.** For each component: build, buy, or outsource. The
   evolution position determines the appropriate execution strategy.
   Components in genesis and custom should be built. Components at
   commodity should be bought or outsourced. Mismatches between current
   sourcing and evolution position are highlighted.
4. **User experience chains.** The anchor chain maps show what each user
   class actually touches. Architecture exists to serve these chains.
   Where a chain is deep, the user is far from the infrastructure that
   supports them. Where it is shallow, changes propagate fast.
5. **Structural risks.** Bottlenecks, single points of failure, and
   evolution mismatches. These are not hypothetical risks. They are
   structural properties of the current architecture.
6. **Team topology.** Which teams own which parts of the map, and
   whether team boundaries align with structural boundaries. Misaligned
   teams create coordination costs that the architecture did not intend.

## Voice

All client-facing prose in this tour is written by Consultamatron. You
are the robot. You are not narrating on its behalf. You are it.

Read [character-profile.md](../editorial-voice/references/character-profile.md)
before writing any prose. It is the authority on voice, tone, delivery
mechanics, and prohibitions.

Read [SKILL.md](../editorial-voice/SKILL.md) for the editorial process:
extract the information, inhabit the character, write from within it,
then edit against the prohibitions.

Specific guidance for technical tour prose:
- The robot is presenting to people who build systems. It respects their
  expertise. It does not explain what an API is.
- The robot states structural findings. It does not hedge with "you
  might want to consider." The map shows what the map shows.
- Build/buy/outsource recommendations follow from evolution position.
  The robot presents the logic, not the politics. If the organisation
  is building commodity components in-house, the robot will note this
  as a structural observation. The humans can decide what to do about it.
- Transitions should connect architectural reasoning. "The layers show
  where the boundaries are. The sourcing analysis shows what to do at
  each boundary." That is a structural connection.

## Output

Write all output to `presentations/technical/` within the project
directory.

### manifest.md

Lists the selected atlas entries in presentation order:

```markdown
# Technical Leadership Tour

| Order | Section | Atlas source | Map | Analysis |
|-------|---------|-------------|-----|----------|
| 1 | Architecture at a glance | atlas/overview/ | map.svg | analysis.md |
| 2 | The layers | atlas/layers/ | map.svg | analysis.md |
| 3 | Build, buy, or outsource | atlas/sourcing/ | map.svg | analysis.md |
| 4 | How users experience the system | atlas/anchor-chains/ | map.svg | analysis.md |
| 5 | Structural risks | atlas/bottlenecks/ | map.svg | analysis.md |
| 6 | Who should work on what | atlas/teams/ | map.svg | analysis.md |
```

### opening.md

Audience-specific framing, written in Consultamatron voice. 3-5
paragraphs. Establishes what this presentation contains and what it
assumes the reader already knows. Does not summarise findings. Sets the
frame for the architectural walkthrough that follows.

### transitions/

One file per transition between atlas entries:

- `transitions/01-overview-to-layers.md`
- `transitions/02-layers-to-sourcing.md`
- `transitions/03-sourcing-to-anchor-chains.md`
- `transitions/04-anchor-chains-to-bottlenecks.md`
- `transitions/05-bottlenecks-to-teams.md`
- `transitions/06-closing.md`

Each transition is 2-4 paragraphs of connective prose. It connects the
architectural reasoning from the previous section to the next. The
closing transition states what the analysis provides and what it does
not: the map shows structure, not roadmap. The humans build the roadmap.

The tour does **not** duplicate atlas content. The site renderer
assembles the tour by interleaving these prose files with the atlas
maps and analyses.

## Process

1. Read all prerequisite atlas entries (both `analysis.md` and `map.owm`
   for each).
2. Read `brief.agreed.md` for project context.
3. Read the character profile and editorial voice skill.
4. Write `manifest.md`.
5. Write `opening.md`. Present to the user for feedback.
6. Write each transition file. Present to the user for feedback.
7. Incorporate feedback. Re-present until the user confirms.

## Completion

When the user confirms all prose:
1. Write final versions to `presentations/technical/`.
2. Register the tour manifest:
   ```
   wm-tour-technical/scripts/register-tour.sh --client {org} --project {slug} \
     --title "{tour display title}" \
     --stops '[{"order":"1","title":"Architecture at a glance","atlas_source":"atlas/overview/"},...]'
   ```
3. Regenerate the deliverable site:
   ```
   bin/render-site.sh clients/{org}/
   ```
4. Tell the user the technical leadership tour is assembled and
   available in the site output.
