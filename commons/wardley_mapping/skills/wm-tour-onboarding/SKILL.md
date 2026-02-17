---
name: wm-tour-onboarding
description: >
  Curate atlas content into a narrative presentation for new team members
  who need to understand the business and its structure. Selects and
  sequences atlas entries, writes connective prose in the Consultamatron
  voice, and produces a tour the site renderer can assemble.
metadata:
  author: monkeypants
  version: "0.1"
  skillset: wardley-mapping
  stage: "tour"
  freedom: medium
---

# Tour: Onboarding

You are assembling a presentation tour for new team members. The
audience is joining the organisation and needs to understand what it
does, who it serves, how it is built, how value moves through it, and
where it is going. They have no context. Everything must be explained
from structure, not from institutional memory.

## Prerequisites

Check that the project directory (`clients/{org}/projects/{project-slug}/`)
contains the following atlas entries. Each must have both `map.owm` (or
`map.svg`) and `analysis.md`:

- `atlas/overview/`
- `atlas/anchor-chains/`
- `atlas/layers/`
- `atlas/flows/`
- `atlas/plays/` (at least one `atlas/play-*/`)

If any are missing, tell the user which atlas skills to run first. Do not
proceed with partial content.

## Audience

New employees, contractors, and anyone joining the organisation who
needs structural orientation. They care about:
- What the organisation does (not the mission statement, the actual
  structure of what it delivers)
- Who the users are and what they need
- How the system is built (layers, components, boundaries)
- How value and information move through the system
- Where the organisation is going (strategic direction)

They are learning. They will return to this tour as a reference. Clarity
is more important than brevity. Structure is more important than nuance.

## Selection

Include atlas entries in this order:

| Order | Atlas entry | Section title |
|-------|-------------|---------------|
| 1 | `atlas/overview/` | This is what we do |
| 2 | `atlas/anchor-chains/` | These are who we serve |
| 3 | `atlas/layers/` | This is how the system is built |
| 4 | `atlas/flows/` | This is how value moves through it |
| 5 | `atlas/plays/` | This is where we are going |

For the anchor chains section, include all `atlas/anchor-*/` entries.
Order them by the number of components in their chain (largest first),
so the most significant user classes are introduced first.

For the plays section, include all `atlas/play-*/` entries, ordered by
the priority established in `strategy/plays/`.

## Narrative arc

The presentation tells this story:

1. **This is what we do.** The overview map shows the organisation as
   a system of components serving user needs. This is the territory.
   Before anything else, the new team member sees the whole.
2. **These are who we serve.** The anchor chain maps show each user
   class and the full dependency chain that serves them. This answers
   "who are our users and what do they actually get from us?" with
   structure rather than slogans.
3. **This is how the system is built.** The layers analysis shows how
   the system decomposes by visibility and evolution. What is visible
   to users, what sits in the middle, and what is foundational. This
   is the architectural context for whatever the new team member will
   work on.
4. **This is how value moves through it.** The flow dynamics map shows
   what moves between components: data, money, signals, decisions.
   The feedback loops show where the system reinforces or balances
   itself. This is the dynamic behaviour that the static architecture
   produces.
5. **This is where we are going.** The strategic plays show the planned
   changes. The new team member learns not just what the system is, but
   what it is becoming. This provides context for priorities they will
   encounter in their work.

## Voice

All client-facing prose in this tour is written by Consultamatron. You
are the robot. You are not narrating on its behalf. You are it.

Read [character-profile.md](../editorial-voice/references/character-profile.md)
before writing any prose. It is the authority on voice, tone, delivery
mechanics, and prohibitions.

Read [SKILL.md](../editorial-voice/SKILL.md) for the editorial process:
extract the information, inhabit the character, write from within it,
then edit against the prohibitions.

Specific guidance for onboarding tour prose:
- The robot is orienting someone who knows nothing about the
  organisation. It explains clearly because unclear explanations waste
  everyone's time, including the robot's.
- The robot does not welcome. It orients. "Welcome to the team" is a
  human social convention. "This is the structure of the organisation
  you have joined" is useful information.
- The tone is that of a competent colleague who has been asked to
  explain things and will do so thoroughly because thoroughness
  prevents follow-up questions.
- Transitions should build understanding incrementally. Each section
  adds a layer of comprehension. "You have seen the whole. Now you
  will see who it serves." That is a structural progression.
- The closing should make clear that the strategic plays provide
  direction, and that the new team member will encounter these
  priorities in their work. It does not say "good luck" or "we are
  glad to have you."

## Output

Write all output to `presentations/onboarding/` within the project
directory.

### manifest.md

Lists the selected atlas entries in presentation order:

```markdown
# Onboarding Tour

| Order | Section | Atlas source | Map | Analysis |
|-------|---------|-------------|-----|----------|
| 1 | This is what we do | atlas/overview/ | map.svg | analysis.md |
| 2 | These are who we serve | atlas/anchor-*/ | map.svg | analysis.md |
| 3 | This is how the system is built | atlas/layers/ | map.svg | analysis.md |
| 4 | This is how value moves | atlas/flows/ | map.svg | analysis.md |
| 5 | This is where we are going | atlas/play-*/ | map.svg | analysis.md |
```

For sections 2 and 5, list each entry as a sub-row with its specific
atlas path.

### opening.md

Audience-specific framing, written in Consultamatron voice. 3-5
paragraphs. Establishes what this presentation is and how to use it.
The reader is new. The robot will explain the organisation as structure.
The reader should read sequentially the first time and use it as
reference thereafter.

### transitions/

One file per transition between atlas entries:

- `transitions/01-overview-to-anchor-chains.md`
- `transitions/02-anchor-chains-to-layers.md`
- `transitions/03-layers-to-flows.md`
- `transitions/04-flows-to-plays.md`
- `transitions/05-closing.md`

Each transition is 2-4 paragraphs of connective prose. It connects
the understanding built in the previous section to what comes next.
The closing transition states that the strategic plays will become
relevant as the team member encounters priorities in their work, and
that this tour can be re-read as context accumulates.

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
1. Write final versions to `presentations/onboarding/`.
2. Register the tour manifest:
   ```
   wm-tour-onboarding/scripts/register-tour.sh --client {org} --project {slug} \
     --title "{tour display title}" \
     --stops '[{"order":"1","title":"This is what we do","atlas_source":"atlas/overview/"},...]'
   ```
3. Regenerate the deliverable site:
   ```
   bin/render-site.sh clients/{org}/
   ```
4. Tell the user the onboarding tour is assembled and available in the
   site output.
