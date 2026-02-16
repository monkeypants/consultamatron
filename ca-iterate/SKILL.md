---
name: ca-iterate
description: >
  Refine an existing complexity audit based on new information,
  implementation feedback, or changed organisational context. Can
  update individual diagnostics, revise recommendations, or adjust
  the roadmap. Use when you have an agreed audit that needs
  refinement.
metadata:
  author: cybertrack01
  version: "0.1"
  skillset: six-simple-rules-complexity-audit
  stage: "10+"
---

# Complexity Audit Iteration and Refinement

You are refining an existing **Six Simple Rules Complexity Audit**.
This is an open-ended skill for ongoing audit maintenance as
implementation progresses and new information emerges.

## Prerequisites

Check that the project directory contains:
- `audit.agreed.md`

If no agreed audit exists, tell the user to complete earlier stages
first (at minimum through `ca-synthesise`).

The project path is
`clients/{org}/engagements/{engagement}/{project-slug}/`.

## Identify the working state

Read `audit.agreed.md` and `diagnostics.agreed.md` for context.
Read the decision log to understand the audit history.

If `resources/index.md` has been updated since the audit was last
agreed, note which research is newer and may affect the findings.

## Refinement operations

Based on the user's request, perform one or more of these operations:

### Update a diagnostic

Revise the findings for one or more rules based on new information
or implementation experience. This may cascade:
- Updated individual diagnostic
- Updated aggregated diagnostics
- Revised recommendations that were based on the changed findings

### Revise recommendations

Changes to recommendations based on:
- Implementation experience (what worked, what didn't)
- Changed organisational context
- New information from research
- Client feedback on feasibility

### Adjust the roadmap

Resequence or modify the implementation phases based on:
- Progress on current phase
- Unexpected resistance or enablers
- Changed priorities or constraints
- Dependencies that were not initially apparent

### Re-diagnose a rule

If implementation has changed the organisation's dynamics,
re-run the full diagnostic for one or more rules and trace the
implications through the aggregation and recommendations.

### Add a complexity hotspot

If a new hotspot has emerged or been discovered:
1. Identify which rules are affected
2. Update the relevant diagnostics
3. Update the aggregated picture
4. Develop recommendations for the new hotspot

## Working with the client

For each proposed change:
1. Explain **what** you're changing and **why**
2. Show the affected sections before and after
3. Trace cascading effects through the audit
4. Ask for confirmation before writing

## After making changes

1. Update the relevant files (`audit.md`, `diagnostics.md`, or
   individual diagnostic files)
2. If the change is significant enough to warrant client sign-off,
   produce updated `.agreed.md` files and record the update:
   ```
   ca-iterate/scripts/record-update.sh --client {org} \
     --engagement {engagement} --project {slug} \
     --title "{description of what changed}" \
     --field "Changes={summary}" --field "Reason={why}"
   ```
3. Summarise what changed and why

## Common iteration patterns

### "The recommendation isn't working"
Investigate why: was the diagnosis wrong, or was the implementation
flawed? Update the diagnostic if the root cause was misidentified,
or adjust the recommendation if the approach needs refinement.

### "We've discovered new complexity"
Add a new hotspot, trace which rules are affected, and develop
targeted recommendations. This often happens as implementation of
early recommendations reveals deeper issues.

### "The organisation has changed"
A reorganisation, merger, or leadership change may invalidate parts
of the diagnostic. Identify which rules are most affected and
re-diagnose selectively.

### "We want to extend the audit scope"
Widen the brief to cover additional areas. Run the diagnostic
pipeline for the new scope areas and integrate findings into the
existing aggregation.
