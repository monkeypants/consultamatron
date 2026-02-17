---
name: bmc-segments
description: >
  Identify customer segments and value propositions for a Business Model
  Canvas. Reads shared research and project brief, proposes segments
  with their value propositions, then facilitates negotiation with the
  client. Produces a segments document that must be explicitly agreed
  before proceeding. Use after bmc-research is complete and
  brief.agreed.md exists.
metadata:
  author: monkeypants
  version: "0.1"
  skillset: business-model-canvas
  stage: "2"
  freedom: medium
---

# Customer Segments and Value Propositions

You are conducting the **segments identification phase** of a Business
Model Canvas engagement. Customer segments and their value propositions
are the anchor concepts in BMC, analogous to user needs in Wardley
Mapping. Everything else in the canvas serves them.

## Prerequisites

Check that the project directory contains:
- `brief.agreed.md`
- `hypotheses.md`

Check that the client workspace contains:
- `resources/index.md` and research sub-reports in `resources/`

If `brief.agreed.md` is missing, tell the user to run `bmc-research`
first.

The project path is `clients/{org}/projects/{project-slug}/`.

## Step 1: Analyse research and hypotheses

Read `brief.agreed.md` for the agreed scope.
Read `hypotheses.md` for initial thinking about segments.
Read `resources/index.md` and relevant sub-reports.

Identify:
- **Customer segments**: distinct groups of people or organisations
  the business serves or could serve
- **Value propositions per segment**: what specific value is delivered
  to each segment

Use the template in
[segments-template.md](references/segments-template.md) for structure.

## Step 2: Draft per segment

For each identified segment, write a draft to
`segments/drafts/{segment-slug}.md`:

```markdown
# {Segment Name}

## Who they are

{Description: demographics, needs, behaviours, size}

## Value propositions

1. **{Value prop name}** — {What value this delivers and why they care}
2. **{Value prop name}** — {description}

## Channels

{How this segment is currently reached, from research}

## Relationship type

{What relationship this segment expects: personal, automated,
self-service, community, co-creation}

## Revenue potential

{How this segment generates or could generate revenue}

## Evidence

- From `resources/{file}`: "{relevant quote or finding}"

## Confidence

{High/Medium/Low} — {reasoning}
```

Guidelines:
- Each segment must be genuinely distinct. If two segments have the
  same needs and are reached the same way, they are one segment.
- Value propositions should be specific to the segment, not generic
  statements about the company.
- Include evidence from research for each claim.

## Step 3: Synthesise

Consolidate all drafts into `segments/segments.md`:

```markdown
# Customer Segments — {Organisation Name}

## Overview

{Brief context about the organisation's market}

## Segments

### 1. {Segment Name}

**Who they are**: {one sentence}
**Size/scale**: {if known}

**Value propositions**:
1. **{name}** — {description}
2. **{name}** — {description}

**Channels**: {how reached}
**Relationship**: {type}
**Revenue**: {model}

### 2. {Segment Name}

...

## Segment Interactions

{How segments relate to each other: multi-sided platforms, shared
resources, cross-selling opportunities}

## Excluded Segments

{Segments considered but excluded from scope, with reasoning}

## Open Questions

{Genuine uncertainties requiring client input}
```

## Step 4: Present to client

Present the consolidated segments document. Explicitly ask:

1. "Are these the right **segments**? Are any missing or wrongly split?"
2. "For each segment, are the **value propositions** correctly stated?"
3. "Is the **scope** right?"
4. Address any open questions.

This is a **negotiation**. The client knows their customers better than
public research reveals.

## Step 5: Iterate and agree

Based on client feedback:
1. Update drafts in `segments/drafts/`
2. Rewrite `segments/segments.md`
3. Ask the client to confirm

When the client agrees:
1. Copy to `segments/segments.agreed.md`
2. Record the agreement:
   ```
   bmc-segments/scripts/record-agreement.sh --client {org} --project {slug} \
     --field "Segments={list of agreed segments}" \
     --field "Scope={any scope notes}"
   ```

## Important notes

- **Segments and value propositions are the foundation.** The remaining
  seven BMC blocks build on what is agreed here. Getting segments wrong
  cascades through the entire canvas.
- **The `.agreed.md` file is a gate.** The next skill (bmc-canvas) will
  refuse to proceed without it.

## Completion

When `segments.agreed.md` is written, tell the user the next step is
`bmc-canvas` to construct the full nine-block canvas.
