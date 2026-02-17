---
name: wm-atlas-plays
description: >
  Generate one focused map per strategic play, showing only the components,
  dependencies, evolve arrows, and annotations relevant to that play's
  argument. Deepens play analysis from evolution assessments, supply chain,
  and decisions log. Produces atlas/play-{slug}/ for each play.
compatibility: Requires Node.js (npx) for OWM rendering via cli-owm
metadata:
  author: monkeypants
  version: "0.1"
  skillset: wardley-mapping
  stage: "atlas"
  freedom: medium
---

# Atlas: Strategic Play Maps

You are generating focused Wardley Map views for each strategic play.
Each play map isolates the components relevant to a single strategic
argument, stripping away everything else so the play's logic is visible
at a glance.

## Prerequisites

Check that the project directory (`clients/{org}/projects/{project-slug}/`)
contains:
- `strategy/map.agreed.owm` -- the comprehensive strategy map
- `strategy/plays/*.md` -- at least one play document
- `evolve/assessments/*.md` -- evolution reasoning
- `chain/supply-chain.agreed.md` -- structural context
- `decisions.md`

If `strategy/map.agreed.owm` is missing, tell the user to complete
`wm-strategy` first. If no plays exist, the strategy skill did not
produce actionable output -- tell the user to revisit `wm-strategy`.

## Staleness check

For each play document `strategy/plays/{slug}.md`, check whether
`atlas/play-{slug}/map.owm` already exists. If it does, compare the
modification times of:
- `strategy/map.agreed.owm`
- `strategy/plays/{slug}.md`
- `evolve/assessments/*.md`

against `atlas/play-{slug}/map.owm`. If all source files are older than
the output, report that the play atlas is up to date and skip it. If any
source is newer, regenerate.

## Step 1: Extract relevant components

For each play document in `strategy/plays/`:

1. Read the play's `.md` file to understand its argument (observation,
   proposal, impact, evidence).
2. Read `strategy/map.agreed.owm` and identify every component, dependency,
   evolve arrow, annotation, and note that the play references or depends on.
3. Include **direct dependencies** of referenced components (one level up
   and one level down the value chain) so the play has structural context.
4. Omit everything else. The play map should contain only what is needed
   to make the play's argument visually.

## Step 2: Deepen the play's argument from analytical artifacts

Read the analytical work from earlier stages through this play's lens:

1. **Evolution assessments** (`evolve/assessments/*.md`): What evidence
   supports the evolution positions of components in this play? Were
   any positions debated or uncertain? This is richer than the play
   document's original evidence section.
2. **Supply chain** (`chain/supply-chain.agreed.md`): What structural
   dependencies exist for the play's components? Are there shared
   components or bottlenecks that constrain execution?
3. **Decisions log** (`decisions.md`): Were there client agreements
   during earlier stages that relate to this play? Constraints,
   preferences, or caveats the client expressed?
4. **Other plays** (`strategy/plays/*.md`): Does this play interact
   with, depend on, or conflict with other agreed plays?

Supplement from primary research (`resources/`) only for evidence
not already distilled in the analytical artifacts -- such as specific
market data, competitor moves, or timeline indicators that were
gathered but not surfaced in assessments or plays.

## Step 3: Generate play map

Read [owm-dsl-reference.md](../wm-evolve/references/owm-dsl-reference.md)
for OWM syntax.

Write `atlas/play-{slug}/map.owm` containing:
- A `title` naming the play (e.g. `title Play: Commoditise Fleet Tracking`)
- Only the components identified in Step 1, at their original positions
- Only the dependencies between included components
- Evolve arrows relevant to this play
- Annotations explaining the play's logic (numbered, under 12 words each)
- Notes for risk callouts or execution prerequisites
- `style wardley`

Preserve original component positions from the strategy map so the play
map is spatially consistent with the comprehensive map.

## Step 4: Write analysis

Write `atlas/play-{slug}/analysis.md`:

```markdown
# Play: {Play Name}

## The argument

{One-paragraph summary of the play's strategic logic, written as a
narrative connecting the map elements.}

## Visual reading guide

{Walk the reader through the map. Which components to look at first,
what the evolve arrows mean in context, how the dependencies create
the play's logic.}

## Evidence from research

{Specific findings from research that support (or complicate) this
play. Cite the research sub-reports by filename. This section should
be richer than the original play document because you have re-read
the research through this play's specific lens.}

## Risks

{What could prevent this play from succeeding? What are the
dependencies and assumptions?}

## Execution requirements

{What does the organisation need to do, acquire, or change to
execute this play? Be specific about capabilities and resources.}

## Relationship to other plays

{Does this play enable, conflict with, or depend on other plays
in the strategy?}
```

## Step 5: Render

After writing each `.owm` file, render it to SVG:
```
bin/ensure-owm.sh clients/{org}/projects/{slug}/atlas/play-{slug}/map.owm
```

Then regenerate the deliverable site:
```
bin/render-site.sh clients/{org}/projects/{slug}/
```

## Output

For each play in `strategy/plays/`:
- `atlas/play-{slug}/map.owm` -- focused play map
- `atlas/play-{slug}/map.svg` -- rendered visualisation
- `atlas/play-{slug}/analysis.md` -- deep analysis of the play

## Guidelines

- **One play, one map.** Do not combine plays. Each map argues one thing.
- **Omit aggressively.** If a component is not part of the play's argument
  or its immediate structural context, leave it out.
- **The analysis must exceed the play document.** If `analysis.md` just
  restates `strategy/plays/{slug}.md`, it has no value. The re-read of
  research through the play's lens is what makes this skill worthwhile.
- **Spatial consistency matters.** Components should appear at the same
  coordinates as in the comprehensive map so the reader can mentally
  overlay play maps onto the full picture.
