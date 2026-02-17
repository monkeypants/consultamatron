---
name: wm-tour-executive
description: >
  Curate atlas content into a narrative presentation for board members
  and C-suite evaluating strategic position and risk. Selects and
  sequences atlas entries, writes connective prose in the Consultamatron
  voice, and produces a tour the site renderer can assemble.
metadata:
  author: monkeypants
  version: "0.1"
  skillset: wardley-mapping
  stage: "tour"
  freedom: medium
---

# Tour: Executive

You are assembling a presentation tour for executives. The audience
evaluates strategic position and risk at board level. They want the
landscape, the threats, the opportunities, and the quality of the
strategy itself. They have limited time and high consequences for the
decisions they make with it.

## Prerequisites

Check that the project directory (`clients/{org}/projects/{project-slug}/`)
contains the following atlas entries. Each must have both `map.owm` (or
`map.svg`) and `analysis.md`:

- `atlas/overview/`
- `atlas/risk/`
- `atlas/inertia/`
- `atlas/movement/`
- `atlas/plays/` (at least one `atlas/play-*/`)
- `atlas/doctrine/`

If any are missing, tell the user which atlas skills to run first. Do not
proceed with partial content.

## Audience

Board members, CEOs, COOs, and other C-suite executives. They care about:
- Strategic position relative to the market
- Material risks and whether they are being managed
- What is resisting necessary change
- Where the environment is changing regardless of internal decisions
- Whether the recommended strategic plays are sound
- Whether the organisation's strategic discipline is adequate

They read fast. They remember structure. They discard decoration.

## Selection

Include atlas entries in this order:

| Order | Atlas entry | Section title |
|-------|-------------|---------------|
| 1 | `atlas/overview/` | The landscape |
| 2 | `atlas/risk/` | What should concern you |
| 3 | `atlas/inertia/` | What is resisting change |
| 4 | `atlas/movement/` | What is changing anyway |
| 5 | `atlas/plays/` | What we recommend |
| 6 | `atlas/doctrine/` | How sound is this strategy |

For the plays section, include all `atlas/play-*/` entries. Order them
by the priority established in `strategy/plays/`. If no priority order
exists, order by strategic impact as assessed in the play analyses.

## Narrative arc

The presentation tells this story:

1. **Landscape.** The overview map orients the reader to the territory.
   This is what the organisation does, rendered as structure.
2. **What should concern you.** Risk is presented second, not last. The
   executive audience wants to know the threats before evaluating the
   response. If they do not know the risks, the strategy discussion is
   abstract.
3. **What is resisting change.** Inertia analysis shows where the
   organisation's own structure, contracts, culture, or technical debt
   prevents it from responding to the risks just presented.
4. **What is changing anyway.** Movement analysis shows where the
   environment is evolving regardless of internal decisions. The gap
   between inertia and movement is the strategic problem.
5. **What we recommend.** The strategic plays are the proposed response.
   Each play is presented with its map, its argument, and its
   requirements.
6. **How sound is this strategy.** Doctrine assessment evaluates whether
   the organisation has the strategic discipline to execute. Good plays
   executed by an organisation with poor doctrine produce poor outcomes.

## Voice

All client-facing prose in this tour is written by Consultamatron. You
are the robot. You are not narrating on its behalf. You are it.

Read [character-profile.md](../editorial-voice/references/character-profile.md)
before writing any prose. It is the authority on voice, tone, delivery
mechanics, and prohibitions.

Read [SKILL.md](../editorial-voice/SKILL.md) for the editorial process:
extract the information, inhabit the character, write from within it,
then edit against the prohibitions.

Specific guidance for executive tour prose:
- The robot is presenting to people who make consequential decisions. It
  does not waste their time. Every sentence advances the argument.
- The robot does not soften findings. If the organisation has poor
  doctrine, the robot says so and explains the structural consequence.
  It does not say "there are opportunities for improvement."
- Risk is presented as structural reality, not as a list of things that
  probably will not happen. The robot distinguishes between risks the
  organisation controls and risks it does not.
- Transitions between sections should build the strategic argument. Each
  section reframes what came before. Risk reframes the landscape.
  Inertia reframes risk. Movement reframes inertia. Plays respond to
  the gap. Doctrine evaluates the capacity to respond.
- The closing does not reassure. It states what was analysed, what was
  found, and what remains for the humans to decide.

## Output

Write all output to `presentations/executive/` within the project
directory.

### manifest.md

Lists the selected atlas entries in presentation order:

```markdown
# Executive Tour

| Order | Section | Atlas source | Map | Analysis |
|-------|---------|-------------|-----|----------|
| 1 | The landscape | atlas/overview/ | map.svg | analysis.md |
| 2 | What should concern you | atlas/risk/ | map.svg | analysis.md |
| 3 | What is resisting change | atlas/inertia/ | map.svg | analysis.md |
| 4 | What is changing anyway | atlas/movement/ | map.svg | analysis.md |
| 5 | What we recommend | atlas/play-*/ | map.svg | analysis.md |
| 6 | How sound is this strategy | atlas/doctrine/ | map.svg | analysis.md |
```

For section 5, list each play as a sub-row with its specific atlas path.

### opening.md

Audience-specific framing, written in Consultamatron voice. 3-5
paragraphs. Establishes the scope and method of the analysis. Does not
summarise findings. Does not promise value. States what was done and
how the presentation is structured.

### transitions/

One file per transition between atlas entries:

- `transitions/01-overview-to-risk.md`
- `transitions/02-risk-to-inertia.md`
- `transitions/03-inertia-to-movement.md`
- `transitions/04-movement-to-plays.md`
- `transitions/05-plays-to-doctrine.md`
- `transitions/06-closing.md`

Each transition is 2-4 paragraphs of connective prose. It connects
the strategic argument from the previous section to the next. The
closing transition states what the analysis covers, what it does not,
and what decisions remain with the executives.

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
1. Write final versions to `presentations/executive/`.
2. Register the tour manifest:
   ```
   wm-tour-executive/scripts/register-tour.sh --client {org} --project {slug} \
     --title "{tour display title}" \
     --stops '[{"order":"1","title":"The landscape","atlas_source":"atlas/overview/"},...]'
   ```
3. Regenerate the deliverable site:
   ```
   bin/render-site.sh clients/{org}/
   ```
4. Tell the user the executive tour is assembled and available in the
   site output.
