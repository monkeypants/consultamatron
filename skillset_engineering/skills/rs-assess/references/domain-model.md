# Domain Model — Skillset Quality Assessment

## Dimensions

Four assessment dimensions, each with distinct information sources:

| Dimension | Primary source | Agent role |
|-----------|---------------|------------|
| **Structural** | Codebase, tests | Autonomous — run tests, check gates |
| **Fitness** | Human experience + context | Structure human signal into predicates |
| **Methodological** | Skill files + human knowledge | Collaborative — read artifacts, elicit tacit knowledge |
| **Operational** | Human usage experience | Record and classify human-reported friction |

Structural assessment needs no human gate. Fitness and operational
dimensions need human signal before synthesis — the agent cannot
infer these from artifacts alone.

## Entities

- **Assessment**: Collection of findings across four dimensions for
  a target skillset. Scoped to the target's current state and context.
  - Contains: findings, fitness functions, selected strategies

- **Finding**: An observed property of the target skillset with evidence.
  Classified by dimension and severity.
  - Cites: specific evidence (test output, file path, operator statement)

- **Fitness Function**: An evaluable predicate about the target's fitness
  in its current context. Returns pass/fail/partial, not a rating scale.
  - Scoped to: a dimension or cross-cutting concern

- **Smell**: A named pattern indicating potential problems. Has a
  detection heuristic and an indication of what it means if found.
  - Categorised by: structural, methodological, operational, pipeline

- **Strategy**: A self-contained assessment deepening approach loaded
  on demand. Selected based on what the assessment reveals about the
  target. Multiple strategies can be applied to the same target.

## Vocabulary

| Term | Meaning |
|------|---------|
| fitness function | Evaluable predicate about skillset fitness; replaces maturity ratings |
| smell | Named pattern indicating potential problems; has detection heuristic |
| anchor drift | Target's users or context have changed since pipeline was designed |
| evolution mismatch | Target does custom work where commodities now exist |
| situational fit | Degree to which pipeline serves its actual current users |
| vertical slice | Thin path from finding identification through to fix |
| ceremony | Process overhead per unit of change in the target |
| strategy | Loadable assessment deepening approach; selected by findings |

## Invariants

- Structural assessment produces findings without human input
- Fitness and operational dimensions require human signal before synthesis
- Every finding cites specific evidence (not inferred or assumed)
- Fitness functions are evaluable predicates, not subjective ratings
- Strategy selection depends on assessment findings, not predetermined
