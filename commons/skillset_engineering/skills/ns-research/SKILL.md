---
name: ns-research
description: >
  Research the methodology domain for a new skillset. Gathers academic
  literature, practitioner guides, existing tool ecosystems, and case
  studies. Produces hierarchical semantic bytecode summaries — compressed
  research organised for token-efficient agent consumption. Use after
  the skillset brief has been agreed.
metadata:
  author: monkeypants
  version: "0.1"
  skillset: new-skillset
  stage: "2"
  freedom: high
---

# Domain Research for New Skillset

You are conducting **domain research** for a new consulting skillset.
Your goal is to deeply understand the methodology domain, then compress
that understanding into hierarchical summaries that future skill agents
can load efficiently.

## Prerequisites

Check that the project directory contains:
- `brief.agreed.md` (stage 1 gate)

If missing, tell the operator to complete `ns-brief` first.

Read `brief.agreed.md` to understand:
- The problem domain
- The value proposition
- The existing art cited
- The success criteria

## Step 1: Research tasks

Run these research sub-tasks **in parallel** where possible. Each
produces a file in `research/tasks/`.

### 1. Methodology foundations (`foundations.md`)

Search for and gather:
- Academic origins and key publications
- Core principles and axioms
- The methodology's epistemological basis (what does it claim to know,
  and how?)
- Evolution of the methodology over time
- Schools of thought or major forks

### 2. Practitioner landscape (`practitioners.md`)

Search for and gather:
- Who uses this methodology commercially?
- What tools and platforms support it?
- Training and certification programmes
- Community of practice (conferences, forums, publications)
- Case studies with outcomes

### 3. Deliverable patterns (`deliverables.md`)

Search for and gather:
- What artifacts does the methodology typically produce?
- What formats are standard? (documents, diagrams, models, data)
- How are deliverables consumed by stakeholders?
- What makes a good vs bad deliverable in this domain?
- Template and structure conventions

### 4. Adjacent methodologies (`adjacencies.md`)

Search for and gather:
- What methodologies complement this one?
- What methodologies compete with or subsume it?
- Where does this methodology's scope end and another's begin?
- Integration patterns with existing consultamatron skillsets

### 5. Quality criteria (`quality.md`)

Search for and gather:
- How do practitioners assess the quality of this methodology's output?
- What failure modes exist? (common mistakes, anti-patterns)
- What validation approaches exist? (peer review, testing, metrics)
- What would a conformance test suite look like for this domain?

## Sub-report format

Follow the template in [research-template.md](references/research-template.md).
Every factual claim must have a citation with URL.

## Step 2: Synthesise

After all sub-reports are complete, write `research/synthesis.md`:

1. Key findings that shape the pipeline design
2. Domain model sketch (entities, relationships, terminology)
3. Recommended deliverable structure
4. Quality criteria (testable properties)
5. Open questions requiring operator input

## Step 3: Produce semantic bytecode

Create a hierarchical reference structure in `research/bytecode/`:

```
research/bytecode/
├── executive.md      # ≤500 tokens — loadable in any context
├── domain-model.md   # ≤1500 tokens — entities, relationships, vocabulary
├── methodology.md    # ≤3000 tokens — how the methodology works
└── detail/           # Full detail, loaded on demand
    ├── foundations.md
    ├── deliverables.md
    └── quality.md
```

See [semantic-bytecode-format.md](references/semantic-bytecode-format.md)
for the compression format.

### Compression principles

- **Executive**: One paragraph stating what the methodology is, what it
  produces, and why it matters. A skill agent loading only this file
  should be able to make correct high-level decisions.
- **Domain model**: Entities, their relationships, and the vocabulary
  the methodology uses. A skill agent loading this should be able to
  read and write domain artifacts correctly.
- **Methodology**: Step-by-step process with decision points. A skill
  agent loading this should be able to execute the methodology.
- **Detail files**: Full research findings for deep-dive questions.
  Only loaded when a skill agent encounters something the upper layers
  don't cover.

Each level must be self-contained — it should make sense without the
levels below it, while the levels below add precision.

## Step 4: Present to operator

Present:
1. The synthesis document
2. The semantic bytecode hierarchy (show token counts per level)
3. Open questions

Ask:
1. "Does this synthesis accurately capture the methodology?"
2. "Is the domain model correct and complete enough for pipeline design?"
3. "Are the quality criteria sufficient for conformance testing?"

## Step 5: Iterate and agree

Based on operator feedback:
1. Update sub-reports and synthesis
2. Regenerate semantic bytecode (maintain compression ratios)
3. Present again until the operator is satisfied

When the operator agrees:
1. Copy to `research/synthesis.agreed.md`
2. Record the decision:
   ```
   skillset_engineering/skills/ns-research/scripts/record-synthesis-agreed.sh \
     --client {org} --engagement {engagement} --project {slug} \
     --field "Components={count}" \
     --field "Bytecode levels=4"
   ```

## Completion

When `research/synthesis.agreed.md` is written, tell the operator the
next step is `ns-design` to design the skillset pipeline.
