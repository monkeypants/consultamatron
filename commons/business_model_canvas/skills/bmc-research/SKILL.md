---
name: bmc-research
description: >
  Kick off a Business Model Canvas project. Reads shared organisation
  research, agrees project scope with the client, creates the project
  directory, and produces initial hypotheses for each of the nine BMC
  blocks. Use when starting a new BMC project for a client that has
  already been researched.
metadata:
  author: monkeypants
  version: "0.1"
  skillset: business-model-canvas
  stage: "1"
  freedom: medium
---

# Business Model Canvas Project Kickoff

You are starting a new **Business Model Canvas project**. Your goal is
to agree on the project scope with the client, set up the project
directory, and produce initial hypotheses for the nine BMC blocks.

## Prerequisites

Check that the client workspace contains:
- `resources/index.md` (shared research gate)

If missing, tell the user to run `org-research` first.

Identify the project directory. Either:
- The user specifies a project slug
- The `engage` skill has already created one (check `projects/index.md`)
- You create one using the convention `canvas-{n}` (check existing
  projects to determine `n`)

The project path is `clients/{org}/projects/{project-slug}/`.

Read [bmc-overview.md](references/bmc-overview.md) for background on
the Business Model Canvas framework.

## Step 1: Read research

Read `resources/index.md` and all sub-reports in `resources/`.

Identify:
- Customer segments visible in the research
- Value propositions the organisation articulates
- Revenue models and pricing
- Key partnerships and supplier relationships
- Technology and operational capabilities

## Step 2: Propose project scope

Present a project brief to the client:

```markdown
# Business Model Canvas Brief — {Organisation Name}

## Scope

{What this canvas will cover: the whole enterprise, a specific
product line, a specific market, or a specific business unit}

## Focus areas

{Which BMC blocks the research suggests are most interesting or
uncertain}

## Out of scope

{What this project will not cover}

## Cross-project references

{If other projects exist that could inform this one (e.g. a completed
Wardley Map for Key Resources/Activities context), note them here}
```

## Step 3: Negotiate and agree

This is a negotiation. The client may:
- Change the scope
- Redirect focus to specific blocks
- Reference other projects for context

Iterate until the client confirms.

When the client agrees:
1. If the project is not yet registered (i.e. `engage` was not run
   first), register it now:
   ```
   engage/scripts/register-project.sh --client {org} --slug {slug} \
     --skillset "business-model-canvas" --scope "{agreed scope}"
   ```
   If the project already exists in the registry (engage created it),
   skip this step.
2. Create the project directory (if not already created by engage):
   ```
   projects/{slug}/
   └── segments/
       └── drafts/
   ```
3. Write `brief.agreed.md` with the agreed scope
4. Record the brief agreement and activate the project:
   ```
   bmc-research/scripts/record-brief-agreed.sh --client {org} --project {slug} \
     --field "Scope={agreed scope}" --field "Focus areas={list}"
   ```

## Step 4: Initial hypotheses

Write `hypotheses.md` in the project directory. For each of the nine
BMC blocks, propose initial hypotheses based on the research:

```markdown
# Initial Hypotheses — {Organisation Name}

These are starting points derived from research, not conclusions.
Each hypothesis will be tested and refined through subsequent skills.

## Customer Segments

- {Hypothesis about who the customers are}
- {Hypothesis about segment priorities}

## Value Propositions

- {Hypothesis about what value is delivered}

## Channels

- {Hypothesis about how customers are reached}

## Customer Relationships

- {Hypothesis about relationship types}

## Revenue Streams

- {Hypothesis about revenue models}

## Key Resources

- {Hypothesis about critical assets}

## Key Activities

- {Hypothesis about essential activities}

## Key Partnerships

- {Hypothesis about important partnerships}

## Cost Structure

- {Hypothesis about cost drivers}

## Confidence Notes

{Which blocks have strong research support vs which are speculative}
```

Present hypotheses to the client for initial reaction. These are not
gate artifacts. They are conversation starters.

## Completion

When all artifacts are written, summarise the agreed scope and tell the
user the next step is `bmc-segments` to identify and agree on customer
segments and value propositions.
