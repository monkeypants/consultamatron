---
name: wm-atlas-bottlenecks
description: >
  Generate a map highlighting components with high fan-in (many
  dependents). Draws on evolution assessments, supply chain, and
  strategy plays to assess failure impact. Produces a focused
  bottleneck map with blast radius analysis.
compatibility: Requires Node.js (npx) for OWM rendering via cli-owm
metadata:
  author: monkeypants
  version: "0.1"
  skillset: wardley-mapping
  stage: "atlas"
  freedom: medium
---

# Atlas: Bottlenecks

You are generating a **bottleneck analysis map** from a comprehensive
Wardley Map. This identifies components with high fan-in — many other
components depend on them — and assesses the consequences of their
failure or degradation.

## Prerequisites

Check that the project directory contains:
- `strategy/map.agreed.owm`
- `chain/supply-chain.agreed.md`
- `evolve/assessments/*.md`
- `strategy/plays/*.md`
- `decisions.md`

If `strategy/map.agreed.owm` is missing, tell the user to complete
`wm-strategy` first.

The project path is `clients/{org}/projects/{project-slug}/`.

## Staleness check

Compare modification times:
- **Sources**: `strategy/map.agreed.owm`,
  `chain/supply-chain.agreed.md`, `evolve/assessments/*.md`
- **Outputs**: `atlas/bottlenecks/map.owm`,
  `atlas/bottlenecks/analysis.md`

If all outputs exist and are newer than all sources, report that the
bottleneck atlas is up to date and skip regeneration. If any source
is newer, or any output is missing, proceed.

## Step 1: Compute fan-in

Read `strategy/map.agreed.owm` and parse the dependency graph. For
every component, count its **fan-in**: the number of other components
(and anchors) that directly or transitively depend on it.

Rank components by fan-in descending. Identify **bottlenecks** as
components whose fan-in is notably higher than the median — typically
the top 5-8 components, but use judgement. A component with fan-in of
2 in a small map is not a bottleneck; a component depended on by 60%
of the map is.

## Step 2: Compute blast radius

For each bottleneck, determine its **blast radius**: the set of
components and anchors that would be affected if the bottleneck
failed or became unavailable.

Walk the dependency graph **backward** from the bottleneck (who
depends on it, and who depends on them, up to the anchors). Record:
- Which anchors are in the blast radius
- Which needs are in the blast radius
- Total component count affected
- Whether any alternative path exists (can dependents route around
  this component?)

## Step 3: Assess bottleneck context

For each bottleneck, read the analytical artifacts from earlier stages:

1. **Evolution assessments** (`evolve/assessments/*.md`): What
   evolution stage is this component at? Is it marked with inertia?
   What was the evidence for its positioning? A bottleneck in genesis
   is riskier than one in commodity.
2. **Supply chain** (`chain/supply-chain.agreed.md`): Where does this
   component sit in the agreed dependency structure? Are there
   structural details not captured in OWM dependencies?
3. **Strategy plays** (`strategy/plays/*.md`): Do any plays depend on
   or propose changes to this bottleneck? A bottleneck targeted by
   an evolve arrow has strategic urgency.
4. **Decisions log** (`decisions.md`): Were there client agreements
   about this component's positioning or importance?

Use primary research (`resources/`) only to supplement where the
analytical artifacts lack specific detail (e.g. vendor concentration
or outage history not captured in assessments).

## Step 4: Generate bottleneck map

Read [owm-dsl-reference.md](../wm-evolve/references/owm-dsl-reference.md)
for full OWM syntax.

Write `atlas/bottlenecks/map.owm`:

```owm
title {Organisation} — Bottleneck Analysis
// Derived from strategy/map.agreed.owm — do not edit directly

// Anchors (all, to show blast radius reach)
anchor {User Class} [{vis}, {mat}]

// Bottleneck components (annotated with fan-in)
component {Bottleneck} [{vis}, {mat}]

// Key dependents (components that directly depend on bottlenecks)
component {Dependent} [{vis}, {mat}]

// Dependencies (show paths through bottlenecks)
{Dependent}->{Bottleneck}

// Annotations highlighting fan-in and risk
annotation 1 [{vis}, {mat}] Fan-in {n} — {risk summary}

annotations [0.90, 0.03]
style wardley
```

Guidelines:
- **Include all anchors** so the reader sees which user classes are
  exposed.
- **Include bottleneck components and their direct dependents.** Omit
  components that are not part of any bottleneck's blast radius.
- **Use annotations** (numbered, max 8) to call out the highest-risk
  bottlenecks with their fan-in count and a short risk note.
- **Use `note`** elements to mark components with no alternative path.
- **Preserve original positions** from the source map.

## Step 5: Write analysis

Write `atlas/bottlenecks/analysis.md`:

```markdown
# Bottleneck Analysis

## Summary

{How many bottlenecks identified, what fraction of the map they
represent, overall risk posture.}

## Bottleneck inventory

| Component | Fan-in | Blast radius | Anchors affected | Alternatives? |
|-----------|--------|-------------|-----------------|---------------|
| {name} | {n} | {count} components | {anchor list} | {yes/no} |

## Detailed assessment

### {Bottleneck Name}

**Fan-in**: {n} direct, {m} transitive
**Blast radius**: {list of affected anchors and needs}
**Alternatives**: {Are there alternative paths or substitute
components? What would switching cost?}
**Analytical context**: {Evolution stage and evidence from assessments,
strategic plays targeting this component, client feedback from
decisions log. Supplement with primary research for specific detail.}
**Risk rating**: {High/Medium/Low with brief justification}

{Repeat for each bottleneck}

## Structural observations

{Are bottlenecks concentrated in one layer (e.g. all infrastructure)?
Are they in custom or commodity territory? Does the map have single
points of failure that affect all anchors?}

## Mitigation patterns

{General observations about what could reduce bottleneck risk:
redundancy, evolution toward commodity, decomposition, alternative
sourcing. Do not prescribe specific actions — that is strategy work.}
```

## Step 6: Render

```
bin/ensure-owm.sh clients/{org}/projects/{slug}/atlas/bottlenecks/map.owm
```

## Output

| File | Purpose |
|------|---------|
| `atlas/bottlenecks/map.owm` | Bottleneck-focused map |
| `atlas/bottlenecks/map.svg` | Rendered SVG |
| `atlas/bottlenecks/analysis.md` | Blast radius and risk analysis |

Present the SVG and the bottleneck inventory table to the user. This
is a derived view — no client agreement gate is needed.

After completion, regenerate the deliverable site:
```
bin/render-site.sh clients/{org}/projects/{slug}/
```
