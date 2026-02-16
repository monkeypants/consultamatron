---
name: ca-diagnose-power
description: >
  Diagnose Rule 3 of the Six Simple Rules: Increase Total Quantity of
  Power. Investigates whether the organisation creates enough power bases
  for cooperation to be positive-sum rather than zero-sum. Produces a
  diagnostic report that must be agreed before proceeding. Use after
  ca-diagnose-integrators is complete.
metadata:
  author: cybertrack01
  version: "0.1"
  skillset: six-simple-rules-complexity-audit
  stage: "4"
---

# Rule 3 Diagnostic: Increase Total Quantity of Power

You are conducting the **Rule 3 diagnostic** of a Six Simple Rules
Complexity Audit. This rule asks: is power treated as a fixed pie, or
does the organisation create new power bases so cooperation is not
zero-sum?

## Prerequisites

Check that the project directory contains:
- `brief.agreed.md`
- `diagnostics/rule1-understanding.agreed.md`
- `diagnostics/rule2-integrators.agreed.md`

If `diagnostics/rule2-integrators.agreed.md` is missing, tell the
user to complete `ca-diagnose-integrators` first.

The project path is
`clients/{org}/engagements/{engagement}/{project-slug}/`.

## The rule

**Increase Total Quantity of Power** — when power is fixed, every
gain for one person is a loss for another. People protect their turf
rather than cooperate. The solution is to create new power bases —
new areas of discretion, judgement, and influence — so that helping
others does not diminish your own position.

Key diagnostic question: **Is cooperation zero-sum in this
organisation, or can people gain power by helping others succeed?**

## Step 1: Review prior diagnostics

Read all agreed diagnostics so far. The integrator analysis (Rule 2)
is especially relevant — integrators need power to function.

## Step 2: Investigate

### Power distribution
- How concentrated is decision-making authority?
- Can people at lower levels exercise meaningful judgement?
- Are there roles with responsibility but no authority?

### Power dynamics
- When someone cooperates across boundaries, do they gain or lose
  standing?
- Are resources (budget, headcount, information) hoarded or shared?
- Do people protect territory because sharing would weaken them?

### New power creation
- Has the organisation created new domains of expertise or
  decision-making?
- Are there roles where influence comes from enabling others rather
  than controlling resources?
- Can people build reputation and career capital through cooperation?

### Evidence sources
- Decision-making authority matrices
- Budget and resource allocation patterns
- How promotions and career advancement actually work
- Knowledge-sharing patterns (or lack thereof)

## Step 3: Draft diagnostic

Write `diagnostics/rule3-power.md`:

```markdown
# Rule 3 Diagnostic: Increase Total Quantity of Power

## Summary

{Assessment of power dynamics and whether cooperation is zero-sum}

## Power landscape

### Concentrated authority
{Where decision-making is concentrated and why}

### Power gaps
{Roles with responsibility but insufficient authority}

### Power hoarding
{Where and why resources or information are protected}

## New power bases

### Existing
{Power bases that enable cooperation}

### Missing
{Opportunities to create new power bases}

## Assessment

**Rating**: Strong / Adequate / Weak / Critical

**Key findings**:
- {Finding 1}
- {Finding 2}

## Connections to prior rules

{How power dynamics relate to understanding (Rule 1) and
integrator effectiveness (Rule 2)}

## Evidence

- From `resources/{file}`: "{relevant finding}"
```

## Step 4: Present and negotiate

Present the diagnostic. Ask:
1. "Does this capture the real power dynamics?"
2. "Where is cooperation most obviously zero-sum?"
3. "What new power bases could be created?"

## Step 5: Iterate and agree

When the client agrees:
1. Copy to `diagnostics/rule3-power.agreed.md`
2. Record the agreement:
   ```
   ca-diagnose-power/scripts/record-agreement.sh \
     --client {org} --engagement {engagement} --project {slug} \
     --field "Rating={assessment rating}" \
     --field "Key findings={summary}"
   ```

## Completion

When `diagnostics/rule3-power.agreed.md` is written, tell the user
the next step is `ca-diagnose-future` to diagnose Rule 4: Extend the
Shadow of the Future.
