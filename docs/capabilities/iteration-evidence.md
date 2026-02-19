---
type: capability
name: iteration-evidence
description: >
  Practice provides the rs-assess improvement pipeline. Skillsets should
  supply fitness functions and accumulated evidence from engagement
  reviews that feed domain-specific quality evaluation and improvement
  planning.
direction: driven
mechanism: undefined
adapter_contract: >
  Not yet defined. The expected shape: a durable channel from the review
  skill's engagement findings to the rs-assess skill's evidence intake.
  Fitness functions as evaluable predicates about skillset quality
  (e.g. "wm-chain produces 15-25 components for a typical engagement").
  An evidence register within the BC package that accumulates findings
  across engagements. A fitness function catalogue that rs-assess reads
  to evaluate the skillset against concrete criteria.
discovery: not_defined
maturity: nascent
hidden_decision: >
  What quality looks like for a specific methodology. The practice layer
  provides the improvement pipeline (assess, plan, iterate). The
  skillset knows what "good" means in its domain — what granularity is
  appropriate, what negotiation quality indicates, what operator
  outcomes matter.
information_expert: >
  Split across time. The review skill (engagement-time) observes what
  happened. The rs-assess skill (engineering-time) evaluates what it
  means. The skillset author defines the fitness functions. Evidence
  accumulates across engagements; evaluation happens during skillset
  engineering.
structural_tests: []
semantic_verification: null
---

# Iteration Evidence

Iteration evidence is the feedback channel from engagement execution
to skillset improvement. The review skill produces findings; the
rs-assess pipeline consumes them. The channel between them does not
yet exist as a structured capability.

## What the practice layer provides

The skillset engineering pipeline: `rs-assess` evaluates a skillset
against fitness functions, `rs-plan` designs specific improvements,
`rs-iterate` applies changes and verifies acceptance criteria. This
pipeline exists and works — but it relies on the operator and agent
reconstructing evidence from memory and workspace artifacts rather
than reading a structured evidence base.

## What the skillset should supply

Three things are missing:

**A feedback channel**: review findings about a specific skillset should
be depositable somewhere that `rs-assess` can discover later, across
sessions and agents. Currently, findings are written to
`{project}/review/` — inside a client workspace that is gitignored.
The evidence evaporates when the engagement ends.

**An evidence register**: each BC package should accumulate operational
evidence. Not a flat issue list — a structured register where each
entry describes: what happened, which skill, what the operator's
assessment was, how many engagements confirm the observation. The
register is the domain-specific equivalent of a GitHub issue tracker,
structured for the rs-assess pipeline.

**A fitness function catalogue**: evaluable predicates about skillset
quality. "bmc-segments surfaces at least one alternative revenue
architecture before gate agreement." "wm-chain produces an initial
component count within 15-25 for a typical engagement." Fitness
functions are richer than issue descriptions — they are evaluable,
they have evidence requirements, they return pass/fail.

## The boundary test

When a review finding arises, apply this test: does fixing it require
understanding a specific consulting methodology, or does it require
understanding the Consultamatron platform?

Methodology knowledge → feed rs-assess inside the bounded context.
Platform knowledge → raise a GitHub issue on the repository.

This boundary test (from the domain-specific iteration article)
determines where evidence flows. The iteration evidence capability is
the structured mechanism for the methodology-knowledge path.

## Architectural rationale

Raising skillset-specific issues on GitHub bypasses the structured
improvement mechanism. It takes evidence that should feed rs-assess
and dumps it into a generic tracker where it loses its evaluative
structure. The iteration evidence capability is the alternative: a
domain-specific quality surface where evidence accumulates, fitness
functions are defined, and improvements are planned with domain fluency.

## References

- [Domain-Specific Iteration](../articles/need-for-domain-specific-iteration.md) —
  why skillset findings do not belong in the GitHub repository
