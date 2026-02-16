---
name: ca-aggregate
description: >
  Coalesce all six rule diagnostics into a unified diagnostic picture.
  Identifies cross-cutting patterns, complexity hotspots, and root cause
  analysis. The client agrees the diagnostic picture before
  recommendations are developed. Use after all six rule diagnostics
  are complete.
metadata:
  author: cybertrack01
  version: "0.1"
  skillset: six-simple-rules-complexity-audit
  stage: "8"
---

# Diagnostics Aggregation

You are **aggregating all six rule diagnostics** into a unified
picture. This is the synthesis of the diagnostic phase — identifying
cross-cutting patterns, complexity hotspots, and root causes. The
client must agree the diagnostic picture before recommendations are
developed.

## Prerequisites

Check that the project directory contains:
- `brief.agreed.md`
- `diagnostics/rule1-understanding.agreed.md`
- `diagnostics/rule2-integrators.agreed.md`
- `diagnostics/rule3-power.agreed.md`
- `diagnostics/rule4-future.agreed.md`
- `diagnostics/rule5-reciprocity.agreed.md`
- `diagnostics/rule6-rewards.agreed.md`

If any diagnostic is missing, tell the user which `ca-diagnose-*`
skill needs to be completed first.

The project path is
`clients/{org}/engagements/{engagement}/{project-slug}/`.

## Step 1: Read all diagnostics

Read all six agreed diagnostic reports and the audit brief.

For each rule, note:
- The assessment rating (Strong / Adequate / Weak / Critical)
- Key findings
- Connections to other rules noted in each diagnostic

## Step 2: Identify cross-cutting patterns

Look for patterns that span multiple rules:

### Complexity hotspots
Areas of the organisation where multiple rules are weak
simultaneously. A hotspot is where broken understanding, absent
integrators, zero-sum power, no feedback, self-sufficiency, and
perverse incentives compound each other.

### Root cause chains
Trace causal chains across rules. For example:
- Perverse incentives (Rule 6) cause people to hoard information
- Hoarding creates self-sufficiency (Rule 5 failure)
- Self-sufficiency weakens integrators (Rule 2 failure)
- Weak integrators lead to structural overlays that nobody
  understands (Rule 1 failure)

### Reinforcing loops
Identify vicious cycles where rule failures amplify each other,
and potential virtuous cycles where fixing one rule could cascade
improvements through others.

## Step 3: Draft aggregated diagnostics

Write `diagnostics.md`:

```markdown
# Aggregated Diagnostics — {Organisation Name}

## Diagnostic summary

| Rule | Rating | Key finding |
|------|--------|-------------|
| 1. Understand What People Really Do | {rating} | {one-line finding} |
| 2. Reinforce Integrators | {rating} | {one-line finding} |
| 3. Increase Total Quantity of Power | {rating} | {one-line finding} |
| 4. Extend the Shadow of the Future | {rating} | {one-line finding} |
| 5. Increase Reciprocity | {rating} | {one-line finding} |
| 6. Reward Those Who Cooperate | {rating} | {one-line finding} |

## Complexity hotspots

### {Hotspot 1: name}

**Location**: {Where in the organisation}
**Rules affected**: {Which rules are weak here}
**Manifestation**: {How complexity shows up}
**Impact**: {Business consequences}

### {Hotspot 2: name}
...

## Root cause analysis

### {Root cause chain 1}

{Trace the causal chain across rules, showing how one failure
drives others}

### {Root cause chain 2}
...

## Reinforcing loops

### Vicious cycles
{Loops where rule failures amplify each other}

### Potential virtuous cycles
{Where fixing one rule could cascade improvements}

## Highest-leverage intervention points

{Based on the root cause analysis, which points in the system
would yield the most improvement if addressed? This is not yet
a recommendation — it is an observation about system dynamics.}

## Open questions

{Genuine uncertainties requiring further investigation or
client input before recommendations can be developed}
```

## Step 4: Present to client

Present the aggregated diagnostics. Ask:
1. "Does this diagnostic picture resonate with your experience?"
2. "Have we identified the right hotspots?"
3. "Are the root cause chains plausible?"
4. "Are there dynamics we've missed?"

This is the most critical negotiation point. The client must own the
diagnostic picture before you build recommendations on it. If they
disagree with the diagnosis, the recommendations will not land.

## Step 5: Iterate and agree

Based on client feedback:
1. Update `diagnostics.md`
2. Present again until the client is satisfied

When the client agrees:
1. Copy to `diagnostics.agreed.md`
2. Record the agreement:
   ```
   ca-aggregate/scripts/record-agreement.sh \
     --client {org} --engagement {engagement} --project {slug} \
     --field "Hotspots={count} complexity hotspots identified" \
     --field "Root causes={count} causal chains traced"
   ```

## Completion

When `diagnostics.agreed.md` is written, tell the user the next step
is `ca-synthesise` to develop recommendations, a roadmap, and the
final audit report.
