---
name: ca-diagnose-future
description: >
  Diagnose Rule 4 of the Six Simple Rules: Extend the Shadow of the
  Future. Investigates whether people see the future consequences of
  their current actions and decisions. Produces a diagnostic report
  that must be agreed before proceeding. Use after ca-diagnose-power
  is complete.
metadata:
  author: cybertrack01
  version: "0.1"
  skillset: six-simple-rules-complexity-audit
  stage: "5"
---

# Rule 4 Diagnostic: Extend the Shadow of the Future

You are conducting the **Rule 4 diagnostic** of a Six Simple Rules
Complexity Audit. This rule asks: do people experience the future
consequences of their current decisions?

## Prerequisites

Check that the project directory contains:
- `brief.agreed.md`
- `diagnostics/rule1-understanding.agreed.md`
- `diagnostics/rule2-integrators.agreed.md`
- `diagnostics/rule3-power.agreed.md`

If `diagnostics/rule3-power.agreed.md` is missing, tell the user to
complete `ca-diagnose-power` first.

The project path is
`clients/{org}/engagements/{engagement}/{project-slug}/`.

## The rule

**Extend the Shadow of the Future** — when people can walk away from
the consequences of their actions, they have no reason to cooperate.
Tightening feedback loops so that today's decisions create tomorrow's
context for the same people changes the cooperation calculus.

Key diagnostic question: **Do the people making decisions today bear
the consequences of those decisions tomorrow?**

## Step 1: Review prior diagnostics

Read all agreed diagnostics. Power dynamics (Rule 3) are directly
relevant — people with no stake in outcomes have no shadow of the
future.

## Step 2: Investigate

### Feedback loop duration
- How long before the consequences of decisions become visible?
- Do the same people who make decisions handle the consequences?
- Are there handoff points where responsibility disappears?

### Consequence visibility
- Can people see the downstream effects of their work?
- Do metrics make future consequences visible or obscure them?
- Are there lagging indicators that arrive too late to change
  behaviour?

### Escape routes
- Can people rotate out before consequences materialise?
- Do reorganisations break the link between decisions and outcomes?
- Are there roles that produce outputs but never deal with the
  results?

### Strategic horizons
- Do planning cycles encourage long-term or short-term thinking?
- Are targets set on timescales that reward front-loading or
  sustainability?
- Do people optimise for this quarter or this year?

### Evidence sources
- Typical tenure in roles (especially decision-making roles)
- How work is handed off between teams or phases
- Performance evaluation timescales
- Post-implementation review practices (or lack thereof)

## Step 3: Draft diagnostic

Write `diagnostics/rule4-future.md`:

```markdown
# Rule 4 Diagnostic: Extend the Shadow of the Future

## Summary

{Assessment of how well consequences feed back to decision-makers}

## Feedback loops

### {Loop 1}
**Decision point**: {Where the decision is made}
**Consequence point**: {Where the consequence lands}
**Time lag**: {How long between decision and consequence}
**Same person?**: {Whether the decision-maker experiences the outcome}

### {Loop 2}
...

## Broken feedback

### {Break point 1}
**What breaks**: {How the feedback loop is interrupted}
**Effect**: {What behaviour this enables}
**Fix opportunity**: {How the loop could be closed}

## Assessment

**Rating**: Strong / Adequate / Weak / Critical

**Key findings**:
- {Finding 1}
- {Finding 2}

## Connections to prior rules

{How feedback loops relate to understanding (Rule 1), integrators
(Rule 2), and power dynamics (Rule 3)}

## Evidence

- From `resources/{file}`: "{relevant finding}"
```

## Step 4: Present and negotiate

Present the diagnostic. Ask:
1. "Where do you see decisions with delayed or invisible consequences?"
2. "Are there roles where people never deal with the results of
   their choices?"
3. "How often do reorganisations break feedback loops?"

## Step 5: Iterate and agree

When the client agrees:
1. Copy to `diagnostics/rule4-future.agreed.md`
2. Record the agreement:
   ```
   ca-diagnose-future/scripts/record-agreement.sh \
     --client {org} --engagement {engagement} --project {slug} \
     --field "Rating={assessment rating}" \
     --field "Key findings={summary}"
   ```

## Completion

When `diagnostics/rule4-future.agreed.md` is written, tell the user
the next step is `ca-diagnose-reciprocity` to diagnose Rule 5:
Increase Reciprocity.
