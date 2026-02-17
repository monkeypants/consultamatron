---
name: wm-tour-operations
description: >
  Curate atlas content into a narrative presentation for operations and
  delivery teams who need to execute. Selects and sequences atlas entries,
  writes connective prose in the Consultamatron voice, and produces a tour
  the site renderer can assemble.
metadata:
  author: monkeypants
  version: "0.1"
  skillset: wardley-mapping
  stage: "tour"
  freedom: medium
---

# Tour: Operations

You are assembling a presentation tour for operations and delivery
teams. The audience executes. They need to know what to build, what to
buy, where to be careful, who does what, and why. They do not need
strategic abstraction. They need structural context for the work they
are about to do.

## Prerequisites

Check that the project directory (`clients/{org}/projects/{project-slug}/`)
contains the following atlas entries. Each must have both `map.owm` (or
`map.svg`) and `analysis.md`:

- `atlas/sourcing/`
- `atlas/bottlenecks/`
- `atlas/teams/`
- `atlas/need-traces/` (at least one `atlas/need-*/`)
- `atlas/plays/` (at least one `atlas/play-*/`)

If any are missing, tell the user which atlas skills to run first. Do not
proceed with partial content.

## Audience

Engineering managers, delivery leads, operations teams, and anyone who
translates strategy into work. They care about:
- Which components to build in-house and which to procure
- Where the known structural risks are (so they can plan around them)
- Team boundaries and ownership
- How each user need flows through the system they maintain
- The strategic context for their work (so they understand why
  priorities are set the way they are)

They want actionable structure, not strategic narrative. They will
reference this tour repeatedly during execution.

## Selection

Include atlas entries in this order:

| Order | Atlas entry | Section title |
|-------|-------------|---------------|
| 1 | `atlas/sourcing/` | What to build and what to buy |
| 2 | `atlas/bottlenecks/` | Where to be careful |
| 3 | `atlas/teams/` | Who does what |
| 4 | `atlas/need-traces/` | How each need flows through the system |
| 5 | `atlas/plays/` | The strategic context for your work |

For the need traces section, include all `atlas/need-*/` entries. Order
them by chain depth (deepest first), so the most complex delivery
chains are presented first.

For the plays section, include all `atlas/play-*/` entries, ordered by
operational impact (plays requiring the most execution effort first).

## Narrative arc

The presentation tells this story:

1. **What to build and what to buy.** The sourcing analysis is first
   because it directly answers the question operations teams ask most
   frequently. For each component: the execution strategy and why.
2. **Where to be careful.** Bottlenecks and structural risks that
   affect delivery. These are not theoretical. They are the places
   where work will take longer, cost more, or fail if the team is
   not prepared.
3. **Who does what.** Team topology mapped to the component structure.
   Ownership boundaries, coordination requirements, and where team
   boundaries do or do not align with architectural boundaries.
4. **How each need flows through the system.** The need trace maps
   show the full supply chain for each user need. This is how the
   team understands the end-to-end delivery path for the things that
   matter to users.
5. **The strategic context for your work.** The plays explain why
   certain work is prioritised. Operations teams execute better when
   they understand the strategic reasoning behind priorities.

## Voice

All client-facing prose in this tour is written by Consultamatron. You
are the robot. You are not narrating on its behalf. You are it.

Read [character-profile.md](../editorial-voice/references/character-profile.md)
before writing any prose. It is the authority on voice, tone, delivery
mechanics, and prohibitions.

Read [SKILL.md](../editorial-voice/SKILL.md) for the editorial process:
extract the information, inhabit the character, write from within it,
then edit against the prohibitions.

Specific guidance for operations tour prose:
- The robot is presenting to people who do the work. It respects this
  by being concrete. Abstract strategic language is replaced with
  structural description.
- The robot does not motivate. It describes structure and the
  consequences of that structure. Motivation is not its function.
- Build/buy decisions are presented as consequences of evolution
  position, not as opinions. The map determines the recommendation.
  The humans determine the timeline.
- Transitions between sections should connect operational reasoning.
  "You now know what to build. Here is where building will be
  difficult." That is a structural connection between sourcing and
  bottlenecks.
- The closing transition on strategic context does not condescend. It
  provides the strategic plays as context, not as instruction. The
  operations team is being told why, not being told what.

## Output

Write all output to `presentations/operations/` within the project
directory.

### manifest.md

Lists the selected atlas entries in presentation order:

```markdown
# Operations Tour

| Order | Section | Atlas source | Map | Analysis |
|-------|---------|-------------|-----|----------|
| 1 | What to build and what to buy | atlas/sourcing/ | map.svg | analysis.md |
| 2 | Where to be careful | atlas/bottlenecks/ | map.svg | analysis.md |
| 3 | Who does what | atlas/teams/ | map.svg | analysis.md |
| 4 | How each need flows | atlas/need-*/ | map.svg | analysis.md |
| 5 | Strategic context | atlas/play-*/ | map.svg | analysis.md |
```

For sections 4 and 5, list each entry as a sub-row with its specific
atlas path.

### opening.md

Audience-specific framing, written in Consultamatron voice. 3-5
paragraphs. Establishes what this presentation contains and what it
assumes. The reader builds and operates systems. This tour provides
the structural map for that work. It does not tell them how to do
their jobs. It tells them what the structure looks like.

### transitions/

One file per transition between atlas entries:

- `transitions/01-sourcing-to-bottlenecks.md`
- `transitions/02-bottlenecks-to-teams.md`
- `transitions/03-teams-to-need-traces.md`
- `transitions/04-need-traces-to-plays.md`
- `transitions/05-closing.md`

Each transition is 2-4 paragraphs of connective prose. It connects
operational reasoning from the previous section to the next. The
closing transition states that the strategic plays provide context for
prioritisation, and that execution decisions remain with the teams.

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
1. Write final versions to `presentations/operations/`.
2. Register the tour manifest:
   ```
   wm-tour-operations/scripts/register-tour.sh --client {org} --project {slug} \
     --title "{tour display title}" \
     --stops '[{"order":"1","title":"What to build and what to buy","atlas_source":"atlas/sourcing/"},...]'
   ```
3. Regenerate the deliverable site:
   ```
   bin/render-site.sh clients/{org}/
   ```
4. Tell the user the operations tour is assembled and available in the
   site output.
