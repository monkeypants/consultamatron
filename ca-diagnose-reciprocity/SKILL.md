---
name: ca-diagnose-reciprocity
description: >
  Diagnose Rule 5 of the Six Simple Rules: Increase Reciprocity.
  Investigates whether the organisation has removed buffers and
  self-sufficiency that allow people to avoid cooperation. Produces
  a diagnostic report that must be agreed before proceeding. Use
  after ca-diagnose-future is complete.
metadata:
  author: cybertrack01
  version: "0.1"
  skillset: six-simple-rules-complexity-audit
  stage: "6"
---

# Rule 5 Diagnostic: Increase Reciprocity

You are conducting the **Rule 5 diagnostic** of a Six Simple Rules
Complexity Audit. This rule asks: does the organisation structure
work so that people genuinely need each other?

## Prerequisites

Check that the project directory contains:
- `brief.agreed.md`
- `diagnostics/rule1-understanding.agreed.md`
- `diagnostics/rule2-integrators.agreed.md`
- `diagnostics/rule3-power.agreed.md`
- `diagnostics/rule4-future.agreed.md`

If `diagnostics/rule4-future.agreed.md` is missing, tell the user
to complete `ca-diagnose-future` first.

The project path is
`clients/{org}/engagements/{engagement}/{project-slug}/`.

## The rule

**Increase Reciprocity** — when people are self-sufficient, they
have no need to cooperate. Buffers, redundant resources, and
self-contained units eliminate interdependence. Removing these
buffers forces cooperation because people cannot succeed alone.

Key diagnostic question: **Can people succeed without cooperating,
or does the structure make mutual dependence real?**

## Step 1: Review prior diagnostics

Read all agreed diagnostics. The shadow of the future (Rule 4) is
directly relevant — reciprocity requires that people both depend on
each other and experience the consequences of not cooperating.

## Step 2: Investigate

### Self-sufficiency buffers
- Which teams have built their own versions of shared capabilities?
- Where do duplicate resources, tools, or functions exist?
- Are there inventory buffers, queues, or backlogs that decouple
  teams from each other?

### Interdependence design
- Where does the organisation deliberately create mutual dependence?
- Are shared services genuinely shared or merely centralised?
- Do teams need to negotiate with each other for outcomes?

### Cooperation avoidance
- Can teams succeed on their metrics without cooperating?
- Are there workarounds that bypass the need for other teams?
- Do people route around difficult colleagues or departments?

### Rich objectives
- Do role definitions include responsibilities to other teams?
- Are individual objectives rich enough to require cooperation?
- Do job descriptions mention integration, coordination, or
  cross-functional outcomes?

### Evidence sources
- Duplicate capabilities across teams
- Inventory and buffer levels between stages
- Internal service-level agreements (often a sign of insufficient
  reciprocity — they substitute for cooperation)
- Cross-functional project success rates

## Step 3: Draft diagnostic

Write `diagnostics/rule5-reciprocity.md`:

```markdown
# Rule 5 Diagnostic: Increase Reciprocity

## Summary

{Assessment of interdependence and cooperation necessity}

## Self-sufficiency buffers

### {Buffer 1}
**What**: {The buffer or duplicated capability}
**Effect**: {How it reduces the need to cooperate}
**Cost**: {The overhead of maintaining it}

### {Buffer 2}
...

## Interdependence analysis

### Where cooperation is real
{Areas where people genuinely need each other}

### Where cooperation is optional
{Areas where people can succeed without cooperating}

## Assessment

**Rating**: Strong / Adequate / Weak / Critical

**Key findings**:
- {Finding 1}
- {Finding 2}

## Connections to prior rules

{How reciprocity relates to understanding (Rule 1), integrators
(Rule 2), power (Rule 3), and feedback (Rule 4)}

## Evidence

- From `resources/{file}`: "{relevant finding}"
```

## Step 4: Present and negotiate

Present the diagnostic. Ask:
1. "Where do you see teams that can succeed without cooperating?"
2. "Which buffers exist because cooperation failed, and which exist
   for good operational reasons?"
3. "Where would removing self-sufficiency create the most
   cooperation benefit?"

## Step 5: Iterate and agree

When the client agrees:
1. Copy to `diagnostics/rule5-reciprocity.agreed.md`
2. Record the agreement:
   ```
   ca-diagnose-reciprocity/scripts/record-agreement.sh \
     --client {org} --engagement {engagement} --project {slug} \
     --field "Rating={assessment rating}" \
     --field "Key findings={summary}"
   ```

## Completion

When `diagnostics/rule5-reciprocity.agreed.md` is written, tell the
user the next step is `ca-diagnose-rewards` to diagnose Rule 6:
Reward Those Who Cooperate.
