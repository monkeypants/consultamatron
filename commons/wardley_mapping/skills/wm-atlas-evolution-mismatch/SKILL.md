---
name: wm-atlas-evolution-mismatch
description: >
  Identify components where the execution strategy (build/buy/outsource)
  does not match the evolution stage. Custom-building commodities?
  Outsourcing genesis work? Also identifies components with no execution
  strategy decorator. Produces a mismatch-annotated map with notes
  explaining each discrepancy and its cost.
compatibility: Requires Node.js (npx) for OWM rendering via cli-owm
metadata:
  author: monkeypants
  version: "0.1"
  skillset: wardley-mapping
  stage: "atlas"
  freedom: medium
---

# Atlas: Evolution-Execution Mismatch

You are generating a **mismatch-focused map** from a comprehensive
Wardley Map. This view identifies components where the execution strategy
(build, buy, outsource) does not align with the component's evolution
stage. Mismatches are either costly mistakes or deliberate strategic
choices -- this analysis distinguishes between the two.

## Prerequisites

Check that the project directory contains:
- `strategy/map.agreed.owm`

Also check for (use if present, provide richer analysis):
- `strategy/plays/*.md`
- `evolve/assessments/*.md`

If `strategy/map.agreed.owm` is missing, tell the user to complete
`wm-strategy` first.

The project path is `clients/{org}/projects/{project-slug}/`.

## Staleness check

Compare modification times:
- **Sources**: `strategy/map.agreed.owm`, `strategy/plays/*.md`
- **Outputs**: `atlas/evolution-mismatch/map.owm`,
  `atlas/evolution-mismatch/analysis.md`

If all outputs exist and are newer than all sources, report that the
evolution-mismatch atlas is up to date and skip regeneration. If any
source is newer, or any output is missing, proceed.

## Step 1: Extract execution strategies

Read `strategy/map.agreed.owm` and classify every component:

For each component, record:
- **Name and position** `[visibility, maturity]`
- **Evolution stage**: Genesis (0.00-0.17), Custom (0.17-0.40),
  Product (0.40-0.70), Commodity (0.70-1.00)
- **Execution decorator**: `(build)`, `(buy)`, `(outsource)`, or **none**
- **Evolve arrow target** (if any): where the component is heading

Also record standalone execution keywords (`build X`, `buy X`,
`outsource X`) that may apply to components without inline decorators.

## Step 2: Define the alignment model

The expected alignment between evolution and execution:

| Evolution stage | Expected execution | Rationale |
|----------------|-------------------|-----------|
| Genesis | build | Novel — no market exists, must be invented |
| Custom | build | Differentiator — competitive advantage from ownership |
| Product | buy | Established market — leverage existing solutions |
| Commodity | outsource | Utility — focus on cost, not capability |

Transitions are acceptable near stage boundaries:
- Custom/Product boundary (0.35-0.45): buy or build are both reasonable
- Product/Commodity boundary (0.65-0.75): buy or outsource are both
  reasonable

## Step 3: Identify mismatches

For each component with an execution decorator, compare against the
alignment model. Classify as:

**Aligned**: execution matches evolution stage.

**Boundary**: execution is acceptable given proximity to a stage boundary.

**Mismatched**: execution conflicts with evolution stage. Subcategories:
- **Over-investing**: building or buying what should be outsourced
  (commodity treated as custom)
- **Under-investing**: outsourcing or buying what should be built
  (genesis/custom treated as commodity)
- **Wrong market engagement**: buying what should be built, or building
  what should be bought

For each mismatch, check `strategy/plays/*.md` to determine whether
the mismatch is **deliberate** (explained and justified in a play) or
**unintentional** (no play addresses it).

## Step 4: Identify missing decorators

List every component that has **no** execution strategy decorator and
no standalone execution keyword. These are components with unclear
ownership — nobody has decided how they should be sourced.

For each, recommend an execution strategy based on the alignment model.

## Step 5: Generate mismatch map

Read [owm-dsl-reference.md](../wm-evolve/references/owm-dsl-reference.md)
for full OWM syntax.

Write `atlas/evolution-mismatch/map.owm`:

```owm
title {Organisation} — Evolution/Execution Mismatches
// Derived from strategy/map.agreed.owm — do not edit directly

// Anchors
anchor {Anchor} [{vis}, {mat}]

// Aligned components (included for context, no special marking)
component {Aligned Component} [{vis}, {mat}] ({strategy})

// Mismatched components (preserve their incorrect decorator)
component {Mismatched Component} [{vis}, {mat}] ({current_strategy})

// Components with no decorator
component {Undecorated Component} [{vis}, {mat}]

// Dependencies (preserve all)
{Parent}->{Child}

// Mismatch notes — one per mismatched component
note +MISMATCH: {stage} but {strategy} [{vis}, {mat}]
note +Deliberate: see play {slug} [{vis}, {mat}]
note +No execution strategy assigned [{vis}, {mat}]

// Annotations for mismatch clusters
annotation 1 [{vis}, {mat}] {Mismatch cluster summary}
annotations [0.90, 0.03]

style wardley
```

Guidelines:
- **Preserve all components and dependencies** for full context.
- **Use notes on every mismatched component** explaining the mismatch.
  Prefix with `+` for emphasis.
- **Distinguish deliberate from accidental** mismatches in the notes.
  Deliberate mismatches should reference the justifying play.
- **Mark undecorated components** with notes recommending a strategy.
- **Use annotations** for clusters of related mismatches.

## Step 6: Write analysis

Write `atlas/evolution-mismatch/analysis.md`:

```markdown
# Evolution-Execution Mismatch Analysis

## Summary

| Category | Count | Components |
|----------|-------|-----------|
| Aligned | {n} | {list} |
| Boundary (acceptable) | {n} | {list} |
| Mismatched (deliberate) | {n} | {list} |
| Mismatched (unintentional) | {n} | {list} |
| No decorator | {n} | {list} |

## Mismatches

### {Component name}

**Position**: [{vis}, {mat}] — {evolution stage}
**Current execution**: {build/buy/outsource}
**Expected execution**: {what the alignment model says}
**Mismatch type**: Over-investing / Under-investing / Wrong engagement
**Deliberate?**: Yes (see play {slug}) / No

**Cost of this mismatch**: {What is the organisation paying for this
misalignment? Higher costs than necessary? Lost competitive advantage?
Unnecessary risk? Slower evolution?}

**Correction path**: {What would it take to align execution with
evolution? Vendor selection, in-house team, migration project? What
are the transition costs and timeline?}

## Missing execution strategies

| Component | Position | Stage | Recommended | Reasoning |
|-----------|----------|-------|-------------|-----------|
| {name}    | [{v},{m}] | {stage} | {build/buy/outsource} | {why} |

## Cost analysis

**Total over-investment**: {Components where the organisation spends
more than necessary by custom-building or buying what could be
outsourced as utility.}

**Total under-investment**: {Components where the organisation risks
competitive disadvantage by outsourcing or buying what should be
built for differentiation.}

## Deliberate mismatches

{For each deliberate mismatch: restate the justification from the
play. Is the justification still valid? What would change if the
mismatch were corrected?}

## Recommendations

{Prioritised list of corrections. Start with the highest-cost
unintentional mismatches. For each, state the current state, target
state, and first concrete step.}
```

## Step 7: Render

```
bin/ensure-owm.sh clients/{org}/projects/{slug}/atlas/evolution-mismatch/map.owm
```

## Output

| File | Purpose |
|------|---------|
| `atlas/evolution-mismatch/map.owm` | Mismatch-annotated map |
| `atlas/evolution-mismatch/map.svg` | Rendered SVG |
| `atlas/evolution-mismatch/analysis.md` | Mismatch analysis |

Present the summary table and SVG first, then offer the detailed
per-component analysis. Highlight unintentional mismatches as the
primary actionable finding. This is a derived view -- no client
agreement gate is needed.

After completion, regenerate the deliverable site:
```
bin/render-site.sh clients/{org}/projects/{slug}/
```
