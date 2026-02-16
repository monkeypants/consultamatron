---
name: ca-synthesise
description: >
  Synthesise recommendations, roadmap, and the final audit report from
  agreed diagnostics. Builds actionable recommendations grounded in the
  Six Simple Rules framework, prioritised by leverage and feasibility.
  Produces the terminal audit report. Use after ca-aggregate is complete
  and diagnostics.agreed.md exists.
metadata:
  author: cybertrack01
  version: "0.1"
  skillset: six-simple-rules-complexity-audit
  stage: "9"
---

# Audit Synthesis: Recommendations and Report

You are producing the **final audit report** — recommendations,
roadmap, and synthesis grounded in the agreed diagnostics. This is
the terminal gate of the complexity audit pipeline.

## Prerequisites

Check that the project directory contains:
- `brief.agreed.md`
- `diagnostics.agreed.md`
- All six individual diagnostics in `diagnostics/`

If `diagnostics.agreed.md` is missing, tell the user to complete
`ca-aggregate` first.

The project path is
`clients/{org}/engagements/{engagement}/{project-slug}/`.

## Step 1: Review agreed diagnostics

Read `diagnostics.agreed.md` for the unified diagnostic picture.
Read the individual diagnostics for detail on each rule.

Note:
- Complexity hotspots and their business impact
- Root cause chains and reinforcing loops
- Highest-leverage intervention points identified in aggregation
- Open questions that may affect recommendations

## Step 2: Develop recommendations

For each complexity hotspot and high-leverage intervention point,
develop a recommendation grounded in the Six Simple Rules:

### Recommendation structure

Each recommendation should:
- **Target a specific rule or combination of rules**
- **Address a root cause, not a symptom**
- **Be actionable** — specific enough that someone could start
  implementing it
- **Acknowledge trade-offs** — what it costs, what resistance to
  expect, what could go wrong
- **Reference the diagnostic evidence** that motivates it

### Recommendation categories

Consider recommendations across these dimensions:
- **Quick wins**: low effort, immediate impact, build momentum
- **Structural changes**: reorganise boundaries, roles, or
  reporting to change cooperation dynamics
- **Incentive redesign**: change what is measured, rewarded, and
  punished
- **Feedback loop creation**: make consequences visible and
  proximate
- **Buffer removal**: eliminate self-sufficiency that prevents
  cooperation
- **Power redistribution**: create new power bases for integrators

## Step 3: Build implementation roadmap

Sequence recommendations into phases:

```markdown
## Phase 1: Quick wins (0-3 months)
{Low-risk changes that demonstrate the approach and build trust}

## Phase 2: Foundation (3-6 months)
{Structural and process changes that create the conditions for
deeper interventions}

## Phase 3: Deep change (6-12 months)
{Incentive redesign, power redistribution, and cultural shifts
that require the foundation to be in place}
```

For each phase, note:
- Prerequisites from earlier phases
- Expected resistance and how to manage it
- How to measure progress
- Decision points where the approach may need adjustment

## Step 4: Assemble audit report

Write `audit.md`:

```markdown
# Complexity Audit Report — {Organisation Name}

## Executive summary

{One page maximum: what we found, what we recommend, and why
it matters for the business}

## Audit scope

{From brief.agreed.md — what was examined and why}

## Diagnostic findings

### Summary

| Rule | Rating | Key finding |
|------|--------|-------------|
{From diagnostics.agreed.md}

### Complexity hotspots

{Summarise from diagnostics.agreed.md}

### Root causes

{Summarise from diagnostics.agreed.md}

## Recommendations

### 1. {Recommendation title}

**Target rules**: {Which rules this addresses}
**Hotspot**: {Which hotspot this targets}
**What**: {Specific action}
**Why**: {Diagnostic evidence that motivates this}
**Trade-offs**: {Costs, risks, expected resistance}
**Measure**: {How to know it's working}

### 2. {Recommendation title}
...

## Implementation roadmap

{Phased roadmap from Step 3}

## Risks and dependencies

{What could prevent the recommendations from succeeding}

## Monitoring framework

{How to track whether complexity is reducing:
- Leading indicators (cooperation behaviour changes)
- Lagging indicators (business outcome improvements)
- Warning signs (new complexity emerging)}
```

## Step 5: Present to client

Present the full audit report. Ask:
1. "Do these recommendations address the right problems?"
2. "Is the phasing realistic given your constraints?"
3. "Which recommendations have the strongest internal support?"
4. "Where do you expect the most resistance?"

## Step 6: Iterate and agree

Based on client feedback:
1. Update `audit.md`
2. Present again until the client is satisfied

When the client agrees:
1. Copy to `audit.agreed.md`
2. Record the agreement and advance the project:
   ```
   ca-synthesise/scripts/record-agreement.sh \
     --client {org} --engagement {engagement} --project {slug} \
     --field "Recommendations={count}" \
     --field "Phases={count} implementation phases"
   ```

## Completion

When `audit.agreed.md` is written, tell the user:
- The complexity audit is complete
- They can use `ca-iterate` for ongoing refinement as implementation
  progresses
- The audit can inform other projects (e.g. Wardley Mapping can use
  the organisational dynamics as context for strategic positioning)
- Consider running `review` to capture lessons learned
