---
name: business-model-canvas
display_name: Business Model Canvas
description: >
  Structured analysis of an organisation's business model across nine
  building blocks. Produces evidence-linked canvas documents grounded
  in research.
---

# Business Model Canvas

The Business Model Canvas is a strategic management tool developed by
Alexander Osterwalder. It describes a business model through nine
building blocks: Customer Segments, Value Propositions, Channels,
Customer Relationships, Revenue Streams, Key Resources, Key Activities,
Key Partnerships, and Cost Structure.

## Pipeline

| Order | Skill | Prerequisite gate | Produces gate | Description |
|-------|-------|-------------------|---------------|-------------|
| 1 | bmc-research | `resources/index.md` | `brief.agreed.md` | Project kickoff: scope, initial hypotheses |
| 2 | bmc-segments | `brief.agreed.md` | `segments/segments.agreed.md` | Identify customer segments and value propositions |
| 3 | bmc-canvas | `segments/segments.agreed.md` | `canvas.agreed.md` | Construct full 9-block canvas |
| 4+ | bmc-iterate | `canvas.agreed.md` | updated `canvas.agreed.md` | Refine existing canvas |

All gates are relative to the project directory:
`clients/{org}/projects/{project-slug}/`.

## Project directory structure

```
projects/{slug}/
├── brief.agreed.md
├── hypotheses.md
├── segments/
│   ├── drafts/{segment-slug}.md
│   ├── segments.md
│   └── segments.agreed.md
├── canvas.md
├── canvas.agreed.md
├── review/                        # Post-implementation review
│   ├── review.md                  # Private review (not shared)
│   └── findings.md                # Sanitised findings for GitHub issues
└── decisions.md
```

## Project slug convention

`canvas-{n}` (e.g. `canvas-1`, `canvas-2`)

## The nine building blocks

1. **Customer Segments**: Who are the most important customers?
2. **Value Propositions**: What value is delivered to each segment?
3. **Channels**: How are segments reached and served?
4. **Customer Relationships**: What type of relationship does each
   segment expect?
5. **Revenue Streams**: What are customers willing to pay for?
6. **Key Resources**: What assets are required to deliver the model?
7. **Key Activities**: What activities are essential?
8. **Key Partnerships**: Who are the key partners and suppliers?
9. **Cost Structure**: What are the most important costs?

## Artifact format

Markdown throughout. The Business Model Canvas has no meaningful second
axis that would warrant a specialised format. The canvas is a structured
markdown document with sections for each building block, evidence links
to research, and confidence assessments.

## Cross-product interaction

A completed Wardley Map can inform BMC Key Resources and Key Activities
blocks. If the project brief references a Wardley Mapping project, the
bmc-canvas skill will use the component inventory as input for those
blocks.
