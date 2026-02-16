# Semantic Bytecode Format

Semantic bytecode is compressed, hierarchical research organised for
token-efficient agent consumption. Each level is self-contained and
makes sense without the levels below.

## Principles

1. **Compression over completeness** — omit detail that doesn't change
   decisions. A skill agent reading the executive summary should make
   the same high-level choices as one reading the full research.
2. **Vocabulary precision** — use the domain's exact terminology.
   Ambiguous paraphrasing costs tokens downstream when agents must
   reconcile different wordings.
3. **Structural fidelity** — preserve the relationships between
   concepts. The domain model level is a lossless representation of
   entity structure even though it omits evidence and narrative.
4. **Progressive disclosure** — each level adds precision without
   contradicting the levels above. An agent loading executive + domain
   model should never be surprised by what methodology says.

## Token budgets

| Level | File | Budget | Purpose |
|-------|------|--------|---------|
| L0 | `executive.md` | ≤500 tokens | High-level decisions |
| L1 | `domain-model.md` | ≤1500 tokens | Read/write domain artifacts |
| L2 | `methodology.md` | ≤3000 tokens | Execute the methodology |
| L3 | `detail/*.md` | Unbounded | Deep-dive answers |

## Format per level

### L0: Executive

```markdown
# {Methodology Name}

{One paragraph: what it is, what it produces, why it matters.}

**Domain**: {problem domain}
**Produces**: {deliverable list}
**Key insight**: {the one thing that distinguishes this methodology}
```

### L1: Domain Model

```markdown
# Domain Model — {Methodology Name}

## Entities

- **{Entity}**: {one-line definition}
  - Relationships: {list}

## Vocabulary

| Term | Meaning |
|------|---------|
| {term} | {precise definition} |

## Invariants

- {Structural rule that must always hold}
```

### L2: Methodology

```markdown
# Methodology — {Methodology Name}

## Process

1. **{Stage}** — {what happens, what it produces}
   - Input: {prerequisite}
   - Output: {artifact}
   - Decision: {what the operator/client decides at this point}

## Quality Criteria

- {Testable property}

## Anti-patterns

- {Common mistake and how to avoid it}
```

### L3: Detail

Full research findings organised by topic. No token budget.
Reference sub-reports by filename for traceability.
