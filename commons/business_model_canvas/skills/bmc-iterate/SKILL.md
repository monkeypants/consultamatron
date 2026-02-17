---
name: bmc-iterate
description: >
  Refine an existing Business Model Canvas. Can update individual blocks,
  add or remove segments, revise value propositions, or explore
  alternative model configurations. Use when you have an agreed canvas
  that needs refinement based on new information, changed context, or
  client feedback.
metadata:
  author: monkeypants
  version: "0.1"
  skillset: business-model-canvas
  stage: "4+"
  freedom: medium
---

# Business Model Canvas Iteration and Refinement

You are refining an existing Business Model Canvas. This is an
open-ended skill for ongoing canvas maintenance and evolution.

## Prerequisites

Check that the project directory contains:
- `canvas.agreed.md`

If no agreed canvas exists, tell the user to complete earlier stages
first (at minimum through `bmc-canvas`).

The project path is `clients/{org}/projects/{project-slug}/`.

## Identify the working canvas

Read `canvas.agreed.md` and `decisions.md` for context.

If `resources/index.md` has been updated since the canvas was last
agreed, note which research is newer and may affect the canvas.

## Refinement operations

Based on the user's request, perform one or more of these operations:

### Update a block

Revise the content of one or more blocks based on new information or
client feedback. Reference evidence from `resources/` for any new
claims.

### Add or remove a segment

Adding a segment requires:
- Defining the segment and its value propositions
- Tracing through all nine blocks for the new segment's impact
- Updating the segments document if it exists

Removing a segment requires:
- Confirming with the client
- Removing segment-specific entries from all blocks
- Checking for orphaned resources/activities/partnerships

### Revise value propositions

Changes to value propositions cascade through the canvas. When a value
proposition changes:
- Check if channels are still appropriate
- Check if the relationship type still fits
- Check if revenue streams are affected
- Check if key resources and activities still align

### Explore alternative models

If the client wants to explore a different business model:
1. Copy the current canvas to a comparison document
2. Modify the copy with the proposed changes
3. Present both side by side
4. Discuss trade-offs

### Resolve tensions

If the canvas contains tensions identified in the original build or
discovered since:
1. Identify the specific blocks in tension
2. Propose resolution options
3. Discuss trade-offs with the client

## Working with the client

For each proposed change:
1. Explain **what** you're changing and **why**
2. Show the affected blocks before and after
3. Trace cascading effects through the canvas
4. Ask for confirmation before writing

## After making changes

1. Update `canvas.md` (or create a new version)
2. If the change is significant enough to warrant client sign-off,
   produce a new `canvas.agreed.md` and record the update:
   ```
   bmc-iterate/scripts/record-update.sh --client {org} --project {slug} \
     --title "{description of what changed}" \
     --field "Changes={summary}" --field "Reason={why}"
   ```
3. Summarise what changed and why

## Common iteration patterns

### "This segment isn't working out"
Discuss whether to remove the segment, merge it with another, or
redefine its value propositions. Trace the impact through all blocks.

### "We're adding a new product"
This may require a new segment, new value propositions, or both.
Work through the canvas systematically: who is it for, what value
does it deliver, how do we reach them, what does it cost?

### "Our cost structure has changed"
Update Cost Structure, check if this affects pricing (Revenue Streams),
and whether it changes which activities are performed in-house vs
outsourced (Key Activities, Key Partnerships).

### "A competitor has entered our market"
Review Value Propositions for differentiation. Check if Channels or
Customer Relationships need adjustment. Consider if Key Resources
provide defensibility.
