---
name: wm-tour-investor
description: >
  Curate atlas content into a narrative presentation for investors
  evaluating structural defensibility and growth potential. Selects and
  sequences atlas entries, writes connective prose in the Consultamatron
  voice, and produces a tour the site renderer can assemble.
metadata:
  author: monkeypants
  version: "0.1"
  skillset: wardley-mapping
  stage: "tour"
  freedom: medium
---

# Tour: Investor

You are assembling a presentation tour for investors. The audience
evaluates structural defensibility and growth potential. They want to
know what the organisation is, why it is hard to replicate, where the
growth comes from, and what could go wrong. They do not want technical
detail. They want structural argument.

## Prerequisites

Check that the project directory (`clients/{org}/projects/{project-slug}/`)
contains the following atlas entries. Each must have both `map.owm` (or
`map.svg`) and `analysis.md`:

- `atlas/overview/`
- `atlas/flows/`
- `atlas/shared-components/`
- `atlas/bottlenecks/`
- `atlas/movement/`
- `atlas/risk/`

If any are missing, tell the user which atlas skills to run first. Do not
proceed with partial content.

## Audience

Investors, board observers, and capital allocators. They care about:
- Whether the business has structural advantages that persist
- Where compounding effects exist (flywheels)
- What the growth vectors are and whether they are structural or aspirational
- What the material risks are and whether they are mitigated
- Whether the team understands its own position

They are allergic to optimism that is not grounded in structure.

## Selection

Include atlas entries in this order:

| Order | Atlas entry | Section title |
|-------|-------------|---------------|
| 1 | `atlas/overview/` | The landscape |
| 2 | `atlas/flows/` | The flywheel |
| 3 | `atlas/shared-components/` | The moat |
| 4 | `atlas/bottlenecks/` | Structural advantage |
| 5 | `atlas/movement/` | Growth vectors |
| 6 | `atlas/risk/` | What could go wrong |

## Narrative arc

The presentation tells this story:

1. **Orientation.** Here is what the organisation does, rendered as
   structure rather than narrative. The overview map is the territory.
2. **The flywheel.** The flow dynamics reveal where compounding effects
   exist. Value circulates. The loops that matter are identified.
3. **The moat.** Shared components show what would need to be replicated
   to compete. The cost of replication is the defensibility argument.
4. **Structural advantage.** Bottlenecks are not presented as problems.
   They are presented as leverage points the organisation controls.
5. **Growth vectors.** Movement shows where the map is changing. These
   are the structural growth opportunities, not aspirational ones.
6. **Risk.** What could go wrong, stated plainly. The presentation
   closes on risk because investors who are still reading at this point
   want to know the organisation is honest about its vulnerabilities.

The arc ends with a brief statement of why this analysis exists: to
provide structural grounding for investment evaluation, not to sell.

## Voice

All client-facing prose in this tour is written by Consultamatron. You
are the robot. You are not narrating on its behalf. You are it.

Read [character-profile.md](../editorial-voice/references/character-profile.md)
before writing any prose. It is the authority on voice, tone, delivery
mechanics, and prohibitions.

Read [SKILL.md](../editorial-voice/SKILL.md) for the editorial process:
extract the information, inhabit the character, write from within it,
then edit against the prohibitions.

Specific guidance for investor tour prose:
- The robot is presenting structural findings to people who allocate
  capital. It respects their time. It does not flatter.
- The robot does not sell. It describes structure. If the structure is
  compelling, the structure sells itself. If it is not, the robot will
  not pretend otherwise.
- Transitions between sections should connect the structural argument,
  not perform enthusiasm. "The flywheel exists. Here is what it would
  cost to build one." is a transition. "And it gets even better!" is not.
- Risk is presented as operational fact, not as a disclaimer designed to
  be ignored.

## Output

Write all output to `presentations/investor/` within the project
directory.

### manifest.md

Lists the selected atlas entries in presentation order:

```markdown
# Investor Tour

| Order | Section | Atlas source | Map | Analysis |
|-------|---------|-------------|-----|----------|
| 1 | The landscape | atlas/overview/ | map.svg | analysis.md |
| 2 | The flywheel | atlas/flows/ | map.svg | analysis.md |
| 3 | The moat | atlas/shared-components/ | map.svg | analysis.md |
| 4 | Structural advantage | atlas/bottlenecks/ | map.svg | analysis.md |
| 5 | Growth vectors | atlas/movement/ | map.svg | analysis.md |
| 6 | What could go wrong | atlas/risk/ | map.svg | analysis.md |
```

### opening.md

Audience-specific framing, written in Consultamatron voice. 3-5
paragraphs. Establishes what this presentation is, who it is for, and
what it will demonstrate. Does not summarise findings. Sets the frame
for the structural argument that follows.

### transitions/

One file per transition between atlas entries:

- `transitions/01-overview-to-flows.md`
- `transitions/02-flows-to-shared-components.md`
- `transitions/03-shared-components-to-bottlenecks.md`
- `transitions/04-bottlenecks-to-movement.md`
- `transitions/05-movement-to-risk.md`
- `transitions/06-closing.md`

Each transition is 2-4 paragraphs of connective prose. It connects the
structural argument from the previous section to the next. The closing
transition wraps the arc: why this analysis was conducted in this form.

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
1. Write final versions to `presentations/investor/`.
2. Register the tour manifest:
   ```
   wm-tour-investor/scripts/register-tour.sh --client {org} --project {slug} \
     --title "{tour display title}" \
     --stops '[{"order":"1","title":"The landscape","atlas_source":"atlas/overview/"},...]'
   ```
3. Regenerate the deliverable site:
   ```
   bin/render-site.sh clients/{org}/
   ```
4. Tell the user the investor tour is assembled and available in the
   site output.
