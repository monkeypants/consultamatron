---
name: bmc-canvas
description: >
  Construct a full nine-block Business Model Canvas from agreed customer
  segments. Builds each block with evidence links to shared research.
  Produces a structured markdown canvas. Use after customer segments
  are agreed (segments.agreed.md exists).
metadata:
  author: monkeypants
  version: "0.1"
  skillset: business-model-canvas
  stage: "3"
  freedom: medium
---

# Business Model Canvas Construction

You are constructing the **full nine-block Business Model Canvas**.
Customer segments and value propositions are agreed. You are now
building out the remaining seven blocks, grounded in research evidence.

## Prerequisites

Check that the project directory contains:
- `segments/segments.agreed.md`
- `brief.agreed.md`
- `hypotheses.md`

Check that the client workspace contains:
- `resources/index.md` and research sub-reports in `resources/`

If `segments.agreed.md` is missing, tell the user to complete
`bmc-segments` first.

The project path is `clients/{org}/projects/{project-slug}/`.

Read [canvas-template.md](references/canvas-template.md) for the
output format.

## Step 1: Review agreed segments and research

Read `segments/segments.agreed.md` for the agreed customer segments
and value propositions.

Re-read `resources/index.md` and relevant sub-reports, now looking
specifically for evidence about:
- How the organisation reaches and serves customers (Channels)
- How it maintains relationships (Customer Relationships)
- How it generates revenue (Revenue Streams)
- What assets it relies on (Key Resources)
- What it does (Key Activities)
- Who it partners with (Key Partnerships)
- What costs it incurs (Cost Structure)

If the brief references other projects (e.g. a Wardley Map), read
those artifacts for additional context on resources and activities.

## Step 2: Build each block

For each of the remaining seven blocks, write a section grounded in
evidence. Every claim should reference a research sub-report or the
agreed segments document.

### Channels
For each segment, identify:
- Awareness: how do customers learn about the offering?
- Evaluation: how do customers evaluate the value proposition?
- Purchase: how do customers buy?
- Delivery: how is value delivered?
- After-sales: how is post-purchase support provided?

### Customer Relationships
For each segment, identify the relationship type:
- Personal assistance, dedicated personal assistance
- Self-service, automated services
- Communities, co-creation

### Revenue Streams
For each segment, identify:
- What customers pay for
- Pricing mechanism (fixed, dynamic, auction, market-dependent)
- Revenue type (transaction, recurring, licensing, subscription)

### Key Resources
Across all segments:
- Physical resources
- Intellectual resources (IP, brand, data)
- Human resources
- Financial resources

### Key Activities
Across all segments:
- Production activities
- Problem-solving activities
- Platform/network activities

### Key Partnerships
- Strategic alliances
- Buyer-supplier relationships
- Joint ventures
- Coopetition arrangements

### Cost Structure
- Fixed costs
- Variable costs
- Economies of scale
- Economies of scope
- Cost-driven vs value-driven orientation

## Step 3: Assemble canvas

Write `canvas.md` using the template in
[canvas-template.md](references/canvas-template.md).

The canvas should:
- Present all nine blocks in a consistent structure
- Link every assertion to evidence in `resources/` or
  `segments/segments.agreed.md`
- Flag uncertainty where research is thin
- Identify tensions or contradictions between blocks
- Note where blocks reinforce each other

## Step 4: Present to client

Present the complete canvas. Ask:

1. "Does this accurately represent your business model?"
2. "For each block, is anything missing or incorrect?"
3. "Are there tensions between blocks that concern you?"
4. "Which areas are you most uncertain about?"

The client will likely:
- Correct assumptions about internal operations
- Add revenue streams or partnerships not visible in public research
- Clarify cost structure priorities
- Identify planned changes to the model

## Step 5: Iterate and agree

Based on client feedback:
1. Update `canvas.md`
2. Present again until the client is satisfied

When the client agrees:
1. Copy to `canvas.agreed.md`
2. Record the agreement:
   ```
   bmc-canvas/scripts/record-agreement.sh --client {org} --project {slug} \
     --field "Segments={count} customer segments" \
     --field "Key tensions={any notable tensions or uncertainties}" \
     --field "Notes={any caveats}"
   ```

## Important notes

- **Output is markdown only.** The Business Model Canvas has no
  meaningful second axis that would warrant a specialised format.
  Structured markdown with sections for each block is the honest
  representation.
- **Evidence matters.** Every block should trace back to research.
  Unsupported assertions undermine the canvas.
- **The `.agreed.md` file is a gate.** The next skill (bmc-iterate)
  works from the agreed canvas.

## Completion

When `canvas.agreed.md` is written, tell the user:
- The canvas is now a working model they can act on
- They can use `bmc-iterate` for ongoing refinement
- The canvas can inform other projects (e.g. Wardley Mapping can
  use Key Resources and Key Activities as input)
