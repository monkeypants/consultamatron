---
name: ca-diagnose-understanding
description: >
  Diagnose Rule 1 of the Six Simple Rules: Understand What People Really
  Do. Investigates actual behaviours, workarounds, and rational strategies
  people adopt to cope with complexity. Produces a diagnostic report that
  must be agreed before proceeding. Use after ca-research is complete and
  brief.agreed.md exists.
metadata:
  author: cybertrack01
  version: "0.1"
  skillset: six-simple-rules-complexity-audit
  stage: "2"
---

# Rule 1 Diagnostic: Understand What People Really Do

You are conducting the **Rule 1 diagnostic** of a Six Simple Rules
Complexity Audit. This rule asks: do we understand the actual
behaviours, goals, and constraints of the people whose cooperation
we need?

## Prerequisites

Check that the project directory contains:
- `brief.agreed.md`

Check that the client workspace contains:
- `resources/index.md` and research sub-reports in `resources/`

If `brief.agreed.md` is missing, tell the user to run `ca-research`
first.

The project path is
`clients/{org}/engagements/{engagement}/{project-slug}/`.

## The rule

**Understand What People Really Do** — not what their job descriptions
say, not what processes prescribe, but what they actually do and why.
People are intelligent strategists who adapt rationally to the context
they face. If the context makes cooperation costly and non-cooperation
painless, rational people will not cooperate.

Key diagnostic question: **Does management understand the real goals,
resources, and constraints that shape how people behave?**

## Step 1: Review research and brief

Read `brief.agreed.md` for the agreed audit scope.
Read `resources/index.md` and relevant sub-reports.

Focus on:
- Formal vs informal organisation structure
- Stated processes vs actual workflows
- Performance metrics people are measured against
- Workarounds and shadow processes
- Where people say "that's not my job"
- Complaints about other teams or functions

## Step 2: Investigate

For each area within the audit scope, investigate:

### Actual behaviours
- What do people actually do vs what they're supposed to do?
- What workarounds exist and why?
- Where do formal processes break down?

### Rational strategies
- Given the goals people are measured on, does their behaviour
  make rational sense?
- What would a rational person do given these constraints?
- Are people blamed for behaviours that are rational responses
  to their context?

### Management understanding
- Does management see the real picture or the org-chart picture?
- Are decisions based on how people actually work or how they
  should work?
- When problems arise, is the response to add rules or to
  understand root causes?

### Evidence sources
- Organisational charts vs actual communication patterns
- Process documentation vs actual workflows
- Performance reviews and metrics
- Employee surveys, exit interviews, or engagement scores
- Customer complaint patterns that reveal internal handoff failures

## Step 3: Draft diagnostic

Write `diagnostics/rule1-understanding.md`:

```markdown
# Rule 1 Diagnostic: Understand What People Really Do

## Summary

{One paragraph assessment of how well the organisation understands
actual behaviour}

## Findings

### {Finding area 1}

**Observation**: {What is actually happening}
**Formal expectation**: {What is supposed to happen}
**Gap**: {The difference and its consequences}
**Rational explanation**: {Why people behave this way given their context}

### {Finding area 2}
...

## Assessment

**Rating**: Strong / Adequate / Weak / Critical

**Key gaps in understanding**:
- {Gap 1}
- {Gap 2}

## Implications for subsequent rules

{How these findings will affect the diagnosis of Rules 2-6}

## Evidence

- From `resources/{file}`: "{relevant finding}"
```

## Step 4: Present to client

Present the diagnostic. Ask:
1. "Does this accurately describe what people actually do?"
2. "Are there behaviours or workarounds we've missed?"
3. "Does management recognise these gaps?"

The client often has insider knowledge that strengthens or corrects
the diagnostic. This is a negotiation.

## Step 5: Iterate and agree

Based on client feedback:
1. Update `diagnostics/rule1-understanding.md`
2. Present again until the client is satisfied

When the client agrees:
1. Copy to `diagnostics/rule1-understanding.agreed.md`
2. Record the agreement:
   ```
   ca-diagnose-understanding/scripts/record-agreement.sh \
     --client {org} --engagement {engagement} --project {slug} \
     --field "Rating={assessment rating}" \
     --field "Key gaps={summary of gaps}"
   ```

## Completion

When `diagnostics/rule1-understanding.agreed.md` is written, tell the
user the next step is `ca-diagnose-integrators` to diagnose Rule 2:
Reinforce Integrators.
