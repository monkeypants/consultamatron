---
type: article
title: Capability Token Economics
description: >
  How token costs scale as skillsets multiply. The compounding cost
  problem for language port verification and the three mechanisms
  that control it.
related:
  - language-port-testing.md
  - ../integration-surface.md
  - ../capabilities/index.md
---

# Capability Token Economics

Code port verification costs zero tokens. Language port verification
costs tokens proportional to content. As skillsets multiply, the total
verification cost scales as a product of two independent growth axes.
This article names the scaling problem and describes how the
architecture controls it.

## The cost formula

Language port verification cost for a single skillset:

```
cost_per_skillset = Σ (capability_i.sample_size × capability_i.max_tokens_per_evaluation)
                    for each language port capability with semantic verification
```

Total verification cost across the platform:

```
total_cost = Σ cost_per_skillset_j    for each registered skillset
```

This is O(n × k) where n is the number of skillsets and k is the number
of language port capabilities with semantic verification. Both n and k
grow over time — n as new methodologies are added, k as nascent
capabilities mature and acquire verification specs.

## Current scale

With two active skillsets (WM, BMC) and six language port capabilities,
the verification surface is small. Most language port capabilities are
nascent — documented but without semantic verification specs. The
token cost of full platform assessment is measured in thousands, not
millions.

## The scaling problem

The compounding cost problem (identified by Parnas in deliberation):
as skillsets multiply — dozens of methodology
domains, each with its own knowledge packs, protocols, research
strategies, and analytical vocabulary — the O(n × k) cost becomes a
ceiling on platform growth.

Ten skillsets with six verified language port capabilities, each
sampling three items at two thousand tokens: 360,000 tokens per full
platform assessment. Fifty skillsets: 1.8 million tokens. The cost
grows linearly in both dimensions, and both dimensions grow.

The architecture does not attempt to eliminate this cost. Token-burning
verification is inherently expensive because the evaluation task is
inherently linguistic. Instead, the architecture controls when and how
often the cost is incurred.

## Three cost control mechanisms

### 1. Promote structural checks to code (Tier 0)

Every structural property that can be verified by code should be. Each
property promoted from Tier 1 (token-burning contract test) to Tier 0
(zero-token shape test) permanently eliminates its token cost across
all skillsets.

Example: checking that a pantheon item has an H2 heading is structural.
It does not require understanding the content — a regex suffices.
Checking that the heading's contribution description is distinctive
requires understanding — tokens are unavoidable. The boundary between
"structurally verifiable" and "linguistically verifiable" is the
engineering optimisation surface.

Shape test promotion is a one-time investment that pays off at O(n) —
once per skillset, on every CI run, forever. The more properties
promoted to code, the smaller the token-burning surface.

### 2. Change-triggered assessment

Full platform assessment is rare. The common case is incremental:
a PR modifies one skillset's adapter files. Only the modified
capability on the modified skillset needs re-assessment.

The `SemanticVerification.trigger` field on each Capability specifies
what changes trigger re-assessment: "content change in pantheon or
vocabulary files," "structural change in docs/ pack," "new research
strategy added." The trigger scopes assessment to the blast radius
of the change.

Change-triggered assessment reduces the amortised cost from O(n × k)
per assessment cycle to O(1) per change — only the affected capability
on the affected skillset is evaluated. Full platform assessment is
reserved for major version changes or periodic quality audits.

### 3. Sample-based evaluation

The `SemanticVerification.sample_size` field caps how many items are
evaluated per capability per assessment. A pantheon with sixteen
luminaries need not evaluate all sixteen — sampling three is sufficient
to detect systematic contract violations (generic triggers, missing
contributions) while capping token cost.

Sampling trades completeness for cost. The assumption: contract
violations are systematic, not random. If three luminaries have
specific invocation triggers, the remaining thirteen probably do too.
If three items violate the contract, the finding is actionable
regardless of how many more items share the violation.

## Token cost as development signal

The fitness evaluation tier is not just verification — it is one step
removed from "how could we improve this?" The token cost of fitness
evaluation is the cost of having the improvement conversation. An
rs-assess session that evaluates a skillset's language port adapters
produces findings that feed rs-plan directly.

This reframes the token cost: it is not overhead, it is the cost of
skillset engineering. A skillset engineer who runs rs-assess is
spending tokens to understand their skillset's quality. The tokens
buy evidence-based improvement plans, not pass/fail verdicts.

The scaling question becomes: how much does skillset engineering cost
as a function of platform size? The answer: O(1) per engineering
session, because each session targets one skillset. The O(n × k)
platform assessment is a theoretical upper bound, not a routine cost.

## Embedding scaling rules on the Capability entity

The `SemanticVerification` properties on each Capability encode the
cost control parameters:

| Property | Cost control function |
|---|---|
| `sample_size` | Caps items evaluated per assessment |
| `max_tokens_per_evaluation` | Caps tokens per item |
| `trigger` | Scopes when re-assessment is needed |
| `evaluation_criteria` | Focuses evaluation on specific properties |

These properties are not just documentation — they are the parameters
that rs-assess reads to execute verification. Changing `sample_size`
from 3 to 5 increases assessment cost by 67%. Changing `trigger` from
"any content change" to "structural change only" reduces assessment
frequency. The Capability entity is the tuning surface for platform
token economics.

## The BYOT model

BYOT (Burn Your Own Tokens) completes the cost control model. The
skillset engineer burns tokens during development. The PR reviewer
burns tokens during review. CI burns zero tokens on language port
verification (only Tier 0 shape tests).

This distributes the cost to the parties who benefit from the
confidence. A skillset engineer iterating on a pantheon burns tokens
to assess quality — those tokens buy them improvement evidence. A
reviewer assessing a PR burns tokens to evaluate the change — those
tokens buy them review confidence. Neither cost is socialised across
the platform.

## References

- [Language Port Testing](language-port-testing.md) — the three-tier
  verification pyramid
- [The Integration Surface](../integration-surface.md) — what
  capabilities are and how code/language ports differ
- [Capabilities Pack](../capabilities/index.md) — the
  SemanticVerification specs that encode scaling rules
