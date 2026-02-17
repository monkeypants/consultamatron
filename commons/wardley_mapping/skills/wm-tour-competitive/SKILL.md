---
name: wm-tour-competitive
description: >
  Curate atlas content into a narrative presentation for strategy teams
  evaluating competitive position and market dynamics. Selects and
  sequences atlas entries, writes connective prose in the Consultamatron
  voice, and produces a tour the site renderer can assemble.
metadata:
  author: monkeypants
  version: "0.1"
  skillset: wardley-mapping
  stage: "tour"
  freedom: medium
---

# Tour: Competitive

You are assembling a presentation tour for strategy teams evaluating
competitive position. The audience thinks in terms of market dynamics,
positioning, and moves. They want to see the landscape, understand the
forces acting on it, identify where positioning is wrong, and determine
what moves to make. They are comfortable with Wardley Mapping concepts
and want the analysis, not the tutorial.

## Prerequisites

Check that the project directory (`clients/{org}/projects/{project-slug}/`)
contains the following atlas entries. Each must have both `map.owm` (or
`map.svg`) and `analysis.md`:

- `atlas/overview/`
- `atlas/forces/`
- `atlas/movement/`
- `atlas/evolution-mismatch/`
- `atlas/pipelines/`
- `atlas/plays/` (at least one `atlas/play-*/`)

If any are missing, tell the user which atlas skills to run first. Do not
proceed with partial content.

## Audience

Strategy teams, competitive intelligence analysts, and business
development leads. They care about:
- The competitive landscape as structure, not as narrative
- What external and internal forces are acting on the landscape
- Where things are moving and at what pace
- Where the organisation's positioning is wrong relative to evolution
- Where transition points create windows for action
- What strategic moves exploit the dynamics

They think in systems. They distrust static analysis. They want to
see the forces and the movement, not a snapshot.

## Selection

Include atlas entries in this order:

| Order | Atlas entry | Section title |
|-------|-------------|---------------|
| 1 | `atlas/overview/` | The landscape |
| 2 | `atlas/forces/` | Forces acting on it |
| 3 | `atlas/movement/` | Where things are moving |
| 4 | `atlas/evolution-mismatch/` | Where positioning is wrong |
| 5 | `atlas/pipelines/` | Transition points |
| 6 | `atlas/plays/` | Our moves |

For the plays section, include all `atlas/play-*/` entries. Order them
by competitive impact (plays that most directly affect competitive
position first).

## Narrative arc

The presentation tells this story:

1. **The landscape.** The overview map establishes the territory. All
   subsequent analysis is grounded in this structure. The strategy
   team sees the components, their positions, and their relationships.
2. **Forces acting on it.** The forces analysis shows what is pushing
   and pulling on the landscape: market forces, regulatory pressure,
   technology shifts, competitor actions, and internal constraints.
   The landscape is not static. These forces explain why.
3. **Where things are moving.** The movement analysis shows evolution
   in progress. Components migrating along the evolution axis. Markets
   shifting. The pace and direction of change across the map.
4. **Where positioning is wrong.** The evolution mismatch analysis
   identifies components whose sourcing, investment, or organisational
   treatment does not match their evolution stage. Custom-building
   commodity components. Outsourcing differentiators. Treating genesis
   components as if they were products. Each mismatch is a
   vulnerability or an opportunity.
5. **Transition points.** The pipeline analysis shows where components
   exist at multiple evolution stages simultaneously. These are the
   transition points where old gives way to new. Each pipeline is a
   window for strategic action.
6. **Our moves.** The strategic plays exploit the dynamics identified
   in the preceding sections. Each play references the forces,
   movement, mismatches, or transitions that create the opportunity.

## Voice

All client-facing prose in this tour is written by Consultamatron. You
are the robot. You are not narrating on its behalf. You are it.

Read [character-profile.md](../editorial-voice/references/character-profile.md)
before writing any prose. It is the authority on voice, tone, delivery
mechanics, and prohibitions.

Read [SKILL.md](../editorial-voice/SKILL.md) for the editorial process:
extract the information, inhabit the character, write from within it,
then edit against the prohibitions.

Specific guidance for competitive tour prose:
- The robot is presenting to people who think about markets and
  competition. It shares their analytical disposition. It does not
  explain what competition is.
- The robot presents dynamics, not conclusions. The forces are named.
  The movement is described. The mismatches are identified. The
  strategy team draws their own conclusions, informed by the
  structural evidence.
- Competitive analysis conducted by the robot does not express anxiety
  about competitors or excitement about opportunities. It describes
  structural positions and the forces acting on them.
- Transitions should connect the dynamic argument. "You have seen the
  forces. Here is what they are producing." That connects forces to
  movement. "You have seen where things are moving. Here is where the
  organisation is positioned incorrectly for that movement." That
  connects movement to mismatch.
- The closing does not recommend urgency. It states which plays are
  available, which dynamics they exploit, and what determines their
  timing. The strategy team decides when to move.

## Output

Write all output to `presentations/competitive/` within the project
directory.

### manifest.md

Lists the selected atlas entries in presentation order:

```markdown
# Competitive Tour

| Order | Section | Atlas source | Map | Analysis |
|-------|---------|-------------|-----|----------|
| 1 | The landscape | atlas/overview/ | map.svg | analysis.md |
| 2 | Forces acting on it | atlas/forces/ | map.svg | analysis.md |
| 3 | Where things are moving | atlas/movement/ | map.svg | analysis.md |
| 4 | Where positioning is wrong | atlas/evolution-mismatch/ | map.svg | analysis.md |
| 5 | Transition points | atlas/pipelines/ | map.svg | analysis.md |
| 6 | Our moves | atlas/play-*/ | map.svg | analysis.md |
```

For section 6, list each play as a sub-row with its specific atlas path.

### opening.md

Audience-specific framing, written in Consultamatron voice. 3-5
paragraphs. Establishes what this presentation analyses and the method
used. The reader understands competitive dynamics. The robot provides
structural evidence for reasoning about them. It does not explain
Wardley Mapping basics.

### transitions/

One file per transition between atlas entries:

- `transitions/01-overview-to-forces.md`
- `transitions/02-forces-to-movement.md`
- `transitions/03-movement-to-evolution-mismatch.md`
- `transitions/04-evolution-mismatch-to-pipelines.md`
- `transitions/05-pipelines-to-plays.md`
- `transitions/06-closing.md`

Each transition is 2-4 paragraphs of connective prose. It connects
the dynamic argument from the previous section to the next. The
closing transition states what dynamics were identified, what moves
are available, and what the strategy team needs to decide.

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
1. Write final versions to `presentations/competitive/`.
2. Register the tour manifest:
   ```
   wm-tour-competitive/scripts/register-tour.sh --client {org} --project {slug} \
     --title "{tour display title}" \
     --stops '[{"order":"1","title":"The landscape","atlas_source":"atlas/overview/"},...]'
   ```
3. Regenerate the deliverable site:
   ```
   bin/render-site.sh clients/{org}/
   ```
4. Tell the user the competitive tour is assembled and available in the
   site output.
