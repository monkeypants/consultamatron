---
name: wm-atlas-doctrine
description: >
  Evaluate the strategy against Wardley doctrine principles. Assesses
  sourcing alignment, inertia management, transparency, flow
  optimisation, and appropriate use of common components. Prose-heavy
  analysis with optional focused map excerpts highlighting specific
  doctrine adherences or violations.
compatibility: Requires Node.js (npx) for OWM rendering via cli-owm
metadata:
  author: monkeypants
  version: "0.1"
  skillset: wardley-mapping
  stage: "atlas"
  freedom: medium
---

# Atlas: Doctrine Assessment

You are evaluating a Wardley mapping strategy against **Wardley doctrine
principles**. This is the most prose-heavy atlas view. The primary output
is a structured analysis document with optional focused maps that
highlight specific doctrine adherences or violations.

## Prerequisites

Check that the project directory contains:
- `strategy/map.agreed.owm`

Also check for (use all that are present):
- `strategy/plays/*.md`
- `chain/supply-chain.agreed.md`
- `needs/needs.agreed.md`
- `evolve/assessments/*.md`
- `decisions.md`
- `brief.agreed.md`

If `strategy/map.agreed.owm` is missing, tell the user to complete
`wm-strategy` first.

The project path is `clients/{org}/projects/{project-slug}/`.

## Staleness check

Compare modification times:
- **Sources**: `strategy/map.agreed.owm`, `strategy/plays/*.md`,
  `decisions.md`
- **Outputs**: `atlas/doctrine/analysis.md`

If all outputs exist and are newer than all sources, report that the
doctrine atlas is up to date and skip regeneration. If any source is
newer, or any output is missing, proceed.

## Step 1: Parse the strategy map

Read `strategy/map.agreed.owm` and catalogue:
1. All components with their positions and decorators (build/buy/outsource)
2. All evolve arrows and their targets
3. All pipelines
4. All annotations and notes
5. All forces (accelerators/decelerators)
6. All inertia markers
7. All flow links

Read `strategy/plays/*.md` for the reasoning behind strategic moves.
Read `decisions.md` for context on what was agreed at each stage.

## Step 2: Assess each doctrine principle

Evaluate the strategy against each principle below. For each, assign
a verdict: **Follows**, **Partially follows**, **Violates**, or
**Not assessable** (insufficient information).

### Principle 1: Use appropriate methods

Does the sourcing strategy match evolution? Check every component with
a `(build)`, `(buy)`, or `(outsource)` decorator:
- Genesis/Custom components should be built (experimentation, learning)
- Product components can be bought (leverage existing markets)
- Commodity components should be outsourced or use utility services

Flag mismatches. Note that deliberate mismatches (explained in plays)
are not violations -- they are strategic choices to interrogate.

### Principle 2: Manage inertia

Does the strategy acknowledge and address inertia? Check:
- Are components marked `inertia` addressed by evolve arrows or plays?
- Are there components that should have inertia markers but don't?
- Do the plays describe how inertia will be overcome?

### Principle 3: Think small (focus)

Is the strategy focused on high-impact moves, or does it try to
change everything at once? Count evolve arrows and strategic plays.
A focused strategy has 3-5 key moves, not 15.

### Principle 4: Be transparent

Does the map reveal assumptions? Check:
- Are uncertain positions acknowledged (in assessments or notes)?
- Are dependencies explicit, or are there hidden assumptions?
- Does the map show what the organisation doesn't know?

### Principle 5: Move fast where appropriate

Are commodity and product components being treated with appropriate
urgency? Genesis components deserve patience; commodity adoption
should be swift. Check whether evolve arrows on commodity components
suggest unnecessarily slow migration.

### Principle 6: Use common components

Are there duplicated capabilities in the map? Multiple components
serving similar purposes at similar evolution stages? Check the
supply chain for redundancy that should be consolidated.

### Principle 7: Optimise flow

Does the strategy support efficient value delivery? Check:
- Are there long dependency chains that could be shortened?
- Do flow links suggest bottlenecks?
- Are high-visibility components well-supported by their chains?

## Step 3: Generate focused maps (optional)

If specific doctrine violations or adherences would be clearer with a
visual, generate focused maps. These are not mandatory -- only create
them when they genuinely aid understanding.

Read [owm-dsl-reference.md](../wm-evolve/references/owm-dsl-reference.md)
for full OWM syntax.

For example, a sourcing mismatch map:

```owm
title {Organisation} — Sourcing Alignment
// Derived from strategy/map.agreed.owm — doctrine assessment

component {Commodity Built In-House} [{vis}, {mat}] (build)
note +Mismatch: commodity being custom-built [{vis}, {mat}]

style wardley
```

Write focused maps to `atlas/doctrine/{principle-slug}.owm` and render
each with `bin/ensure-owm.sh`.

## Step 4: Write analysis

Write `atlas/doctrine/analysis.md`:

```markdown
# Doctrine Assessment

## Summary

| Principle | Verdict | Key finding |
|-----------|---------|-------------|
| Use appropriate methods | {verdict} | {one line} |
| Manage inertia | {verdict} | {one line} |
| Think small | {verdict} | {one line} |
| Be transparent | {verdict} | {one line} |
| Move fast | {verdict} | {one line} |
| Use common components | {verdict} | {one line} |
| Optimise flow | {verdict} | {one line} |

## Detailed assessment

### Use appropriate methods

**Verdict**: {Follows / Partially follows / Violates}

{Detailed analysis. List each component where sourcing matches or
mismatches evolution. Reference specific plays that explain deliberate
mismatches.}

### Manage inertia

**Verdict**: {verdict}

{Which inertia points are addressed? Which are ignored? What's the
risk of unmanaged inertia?}

### Think small

**Verdict**: {verdict}

{How many strategic moves are proposed? Are they focused on the
highest-leverage points? Is there a clear priority ordering?}

### Be transparent

**Verdict**: {verdict}

{What does the map make visible that might otherwise be hidden?
What assumptions remain implicit?}

### Move fast

**Verdict**: {verdict}

{Where is speed appropriate and being applied? Where is unnecessary
delay present? Where is premature haste a risk?}

### Use common components

**Verdict**: {verdict}

{Any duplication or missed consolidation opportunities? Are
commodity components being shared appropriately?}

### Optimise flow

**Verdict**: {verdict}

{Chain efficiency, bottleneck analysis, flow link health.}

## Overall posture

{Synthesise the individual assessments into an overall characterisation.
Is this a doctrine-aware strategy with occasional justified deviations,
or are there systemic doctrine blind spots?}

## Recommendations

{Specific, actionable recommendations to improve doctrine alignment.
Prioritise by impact. Reference specific components and plays.}
```

## Step 5: Render focused maps

For each focused map generated in Step 3:
```
bin/ensure-owm.sh clients/{org}/projects/{slug}/atlas/doctrine/{map}.owm
```

## Output

| File | Purpose |
|------|---------|
| `atlas/doctrine/analysis.md` | Doctrine assessment |
| `atlas/doctrine/{principle}.owm` | Focused map (optional, per principle) |
| `atlas/doctrine/{principle}.svg` | Rendered SVG (optional) |

Present the summary table and overall posture first, then offer the
detailed assessment. This is a derived view -- no client agreement
gate is needed.

After completion, regenerate the deliverable site:
```
bin/render-site.sh clients/{org}/projects/{slug}/
```
