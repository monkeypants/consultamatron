---
name: ca-diagnose-integrators
description: >
  Diagnose Rule 2 of the Six Simple Rules: Reinforce Integrators.
  Investigates whether the organisation has effective integrator roles
  that coordinate across silos without adding structural layers.
  Produces a diagnostic report that must be agreed before proceeding.
  Use after ca-diagnose-understanding is complete.
metadata:
  author: cybertrack01
  version: "0.1"
  skillset: six-simple-rules-complexity-audit
  stage: "3"
---

# Rule 2 Diagnostic: Reinforce Integrators

You are conducting the **Rule 2 diagnostic** of a Six Simple Rules
Complexity Audit. This rule asks: does the organisation reinforce
the people and units that naturally integrate across boundaries?

## Prerequisites

Check that the project directory contains:
- `brief.agreed.md`
- `diagnostics/rule1-understanding.agreed.md`

If `diagnostics/rule1-understanding.agreed.md` is missing, tell the
user to complete `ca-diagnose-understanding` first.

The project path is
`clients/{org}/engagements/{engagement}/{project-slug}/`.

## The rule

**Reinforce Integrators** — integrators are people or units whose
work naturally requires them to coordinate across silos. Rather than
creating new coordination roles or committees, identify those who
already sit at the intersection of multiple concerns and give them
the power and interest to integrate.

Key diagnostic question: **Are existing integrators empowered, or
are they bypassed by structural overlays (committees, matrix
reporting, coordination processes)?**

## Step 1: Review prior diagnostics

Read `brief.agreed.md` and `diagnostics/rule1-understanding.agreed.md`.

The Rule 1 diagnostic reveals where coordination breaks down. Use
these findings to identify where integrators should exist.

## Step 2: Investigate

### Identify natural integrators
- Which roles sit at the intersection of multiple teams or functions?
- Who do people go to informally when cross-functional problems arise?
- Which managers have direct reports in multiple value streams?

### Assess integrator effectiveness
- Do integrators have authority matching their coordinating role?
- Are they judged on integration outcomes or narrow function metrics?
- Do they have enough interest (stake) in the outcomes they integrate?
- Are they bypassed by escalation paths or committee structures?

### Structural overlays
- How many coordination committees, task forces, or matrix overlays
  exist?
- Do these overlays add value or simply add reporting burden?
- When a structural overlay exists, has the underlying integration
  problem been addressed or merely papered over?

### Evidence sources
- Organisation charts and reporting structures
- Meeting structures and committee memberships
- How cross-functional issues are actually resolved
- Job descriptions vs actual influence of boundary-spanning roles

## Step 3: Draft diagnostic

Write `diagnostics/rule2-integrators.md`:

```markdown
# Rule 2 Diagnostic: Reinforce Integrators

## Summary

{Assessment of integrator effectiveness in the organisation}

## Natural integrators identified

### {Role/unit 1}
**Integration scope**: {What they naturally coordinate}
**Current authority**: {Formal power relative to integration needs}
**Current interest**: {Stake in integration outcomes}
**Effectiveness**: {How well they actually integrate}

### {Role/unit 2}
...

## Structural overlays

### {Committee/process 1}
**Purpose**: {Why it was created}
**Integration effect**: {Whether it helps or hinders real integration}
**Underlying cause**: {What integration gap prompted its creation}

## Assessment

**Rating**: Strong / Adequate / Weak / Critical

**Key findings**:
- {Finding 1}
- {Finding 2}

## Connections to Rule 1

{How understanding gaps (Rule 1) relate to integrator effectiveness}

## Evidence

- From `resources/{file}`: "{relevant finding}"
```

## Step 4: Present and negotiate

Present the diagnostic. Ask:
1. "Have we identified the right integrators?"
2. "Are there coordination mechanisms we've missed?"
3. "Which structural overlays could be removed if integrators
   were properly empowered?"

## Step 5: Iterate and agree

When the client agrees:
1. Copy to `diagnostics/rule2-integrators.agreed.md`
2. Record the agreement:
   ```
   ca-diagnose-integrators/scripts/record-agreement.sh \
     --client {org} --engagement {engagement} --project {slug} \
     --field "Rating={assessment rating}" \
     --field "Integrators identified={count}"
   ```

## Completion

When `diagnostics/rule2-integrators.agreed.md` is written, tell the
user the next step is `ca-diagnose-power` to diagnose Rule 3: Increase
Total Quantity of Power.
