---
type: article
title: Language Port Testing
description: >
  Verification strategy for capabilities that use filesystem conventions
  rather than Python Protocols. Three-tier pyramid from zero-token shape
  checks through token-conservative contract tests to token-generous
  fitness evaluation.
related:
  - ../integration-surface.md
  - ../capabilities/index.md
  - ../articles/capability-token-economics.md
  - ../conformance-testing.md
---

# Language Port Testing

Code ports have `@runtime_checkable` Protocol classes and `pytest -m
doctrine` tests. Import fails if the shape is wrong. Tests fail if the
composition is wrong. Zero tokens. Deterministic. Fast.

Language ports have none of this. A knowledge pack is a directory of
markdown files following a convention. The convention is documented,
but documentation is not enforcement. This article describes the
three-tier verification strategy for language port capabilities.

## The problem

Language port adapters are content. Content quality is not evaluable
by code alone. Code can verify that a file exists, that it has YAML
frontmatter, that required keys are present. Code cannot verify that
a luminary's invocation trigger is specific enough to produce a distinct
analytical perspective. That evaluation requires understanding the
content — it requires tokens.

But tokens are expensive, slow, and non-deterministic. A CI pipeline
that burns tokens on every commit is a pipeline that is expensive to
run, slow to complete, and unreliable in its verdicts. The verification
strategy must separate what code can check from what tokens must check,
and it must control when tokens are burned.

## Three tiers

### Tier 0: Shape (code, CI, zero tokens)

Shape tests verify structural properties of language port adapters
using conventional code. They run in CI alongside doctrine tests.

What shape tests check:
- File exists at expected conventional path
- YAML frontmatter parses without error
- Required frontmatter keys are present
- Type values match expected enumerations
- Minimum content thresholds (e.g., pantheon has at least N H2 sections)

What shape tests cannot check:
- Whether frontmatter values are meaningful
- Whether content satisfies the contract's intent
- Whether the adapter is fit for purpose

Shape tests extend the existing `pytest -m doctrine` suite. They are
fast, deterministic, and cheap. They catch structural errors — missing
files, malformed frontmatter, wrong type values — before tokens are
involved.

### Tier 1: Contract (language, token-conservative)

Contract tests verify that the adapter satisfies the structural
expectations documented in the capability's `adapter_contract` field.
They burn tokens — they are language tests, not code tests.

The verification approach: describe the types of contract violation and
ask for a list of them, rated by severity:

- **Violation**: the adapter fails to satisfy a documented contract
  requirement. A pantheon item with no invocation trigger. A pipeline
  stage with no description.
- **Quality warning**: the adapter satisfies the letter of the contract
  but may not serve the consuming use case well. An invocation trigger
  that is too generic to distinguish from other luminaries.
- **Observation**: a noteworthy property that is not a violation or
  warning. The pantheon has unusually few luminaries for the domain's
  breadth.

Contract tests are token-conservative. They ask focused questions about
specific structural properties. The `SemanticVerification` entity on
each Capability specifies: a reference problem (what to evaluate), a
sample size (how many items to check), a max token budget per
evaluation, and evaluation criteria (what to look for).

Contract tests verify that the adapter's structure is compatible with
the consuming use case — that the jedi council would be able to use
this pantheon, not that it would produce good analysis.

### Tier 2: Fitness (language, token-generous)

Fitness evaluation assesses whether the adapter serves its purpose
well. It is the most expensive tier — it may run the consuming use
case on sample inputs and evaluate the output quality.

The fitness function signature:

```
fitness = f(skillset_metadata, contract_requirements, adapter_implementation)
```

Fitness evaluation is powered by the contract metadata on the Capability
entity. The `SemanticVerification` fields define the assessment:
`reference_problem` describes the scenario, `evaluation_criteria`
lists the quality predicates, `sample_size` limits scope, and
`max_tokens_per_evaluation` caps cost per item.

Critically, fitness evaluation is not a gate. It is one step removed
from "how could we improve this?" The assessment produces findings —
what works, what is weak, what could be stronger — and those findings
feed directly into the improvement conversation. A fitness evaluation
that reveals weak invocation triggers does not block anything; it
opens rs-plan with concrete evidence about what to fix.

This makes fitness evaluation part of the development cycle, not a
checkpoint before deployment. The quality gate is the development
conversation itself: rs-assess surfaces findings, rs-plan designs
changes, rs-iterate applies them, and the cycle repeats until the
skillset engineer is satisfied. Fitness evaluation is the instrument
that makes that conversation evidence-based rather than vibes-based.

## When tokens burn

Tokens do not burn in CI. Tokens burn during skillset engineering.

**Change triggers need for review.** When a PR modifies a language port
adapter (adds a luminary, restructures a knowledge pack, revises a
research strategy), the change triggers the need for contract and
fitness assessment. The existing skillset engineering pipeline
(rs-assess → rs-plan → rs-iterate) is the vehicle.

**The reviewer burns the tokens, not CI.** The skillset engineering
skillset defines its own review process. When rs-assess evaluates a
skillset, it reads the Capability entities, checks contract compliance,
and runs fitness evaluations. This is an engineering activity — it
happens during skillset development, not on every commit.

**BYOT (Burn Your Own Tokens).** The skillset author runs assessment
during development. The PR reviewer runs assessment during review.
Neither is an automated CI gate. The token cost is borne by the party
who needs the confidence — the engineer improving the skillset, or the
reviewer accepting the change.

This model inverts the standard CI testing pyramid. In code testing,
cheap tests run always and expensive tests run selectively. In language
port testing, cheap tests (Tier 0) run in CI and expensive tests
(Tier 1, Tier 2) run during engineering sessions — when a human is
present to interpret results and make judgements.

## Shape tests in practice

Shape tests for language port capabilities extend the doctrine test
suite. A shape test for the analysis capability:

```python
@pytest.mark.doctrine
def test_pantheon_shape(bc_package_path):
    """Pantheon items have required structure."""
    pantheon = bc_package_path / "docs" / "pantheon.md"
    if not pantheon.exists():
        pytest.skip("No pantheon in this BC")
    content = pantheon.read_text()
    fm = parse_frontmatter(content)
    assert fm.get("type") == "pantheon"
    # Minimum structural check - H2 sections exist
    h2_count = content.count("\n## ")
    assert h2_count >= 3, "Pantheon needs at least 3 luminaries"
```

Shape tests are parameterised by the Capability entity. The
`structural_tests` list on each capability names the doctrine tests
that verify its shape. Adding a new capability with shape requirements
means adding test functions and listing them on the entity.

## Contract tests in practice

Contract tests use the `SemanticVerification` specification on the
Capability entity. A contract test for the analysis capability:

```
reference_problem: >
  Select 3 luminaries from the pantheon. For each, evaluate: does the
  contribution description distinguish this luminary from others? Does
  the invocation trigger identify a concrete problem type? Would the
  jedi council produce a non-generic perspective from this entry?
sample_size: 3
max_tokens_per_evaluation: 2000
evaluation_criteria:
  - each luminary has a contribution description
  - each luminary has an invocation trigger that identifies concrete
    problem types
  - luminaries are distinguishable (different frameworks, different
    triggers)
  - the council would produce distinct perspectives, not generic advice
trigger: content change in pantheon or vocabulary files
```

The rs-assess pipeline reads this specification, loads the adapter
content, presents the reference problem to the evaluating agent, and
collects a structured assessment. The assessment identifies violations,
quality warnings, and observations — each with evidence. Those findings
become the input to rs-plan.

## The economics

| Tier | Cost | Frequency | Who pays | What it produces |
|---|---|---|---|---|
| Shape | Zero tokens | Every CI run | CI | Pass/fail on structure |
| Contract | Hundreds of tokens per evaluation | On change, during engineering | Skillset engineer | Violations, warnings, observations |
| Fitness | Thousands of tokens per evaluation | During rs-assess | Skillset engineer / reviewer | Improvement evidence for rs-plan |

The total token cost of language port testing is controlled by three
mechanisms: shape tests catch most errors at zero cost; contract tests
sample rather than exhaustively verify; and fitness evaluation runs
during deliberate quality assessment sessions where its findings
feed the improvement cycle.

## References

- [Integration Surface](../integration-surface.md) — what capabilities
  are and how the two mechanisms differ
- [Capability Token Economics](capability-token-economics.md) — scaling
  rules for token-burning verification across many skillsets
- [Conformance Testing](../conformance-testing.md) — the meta-capability
  for structural verification
- [Capabilities Pack](../capabilities/index.md) — the SemanticVerification
  specs on each capability
