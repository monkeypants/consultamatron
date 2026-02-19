---
type: capability
name: pipeline-declaration
description: >
  Practice orchestrates engagements through skillset pipelines. Each
  skillset declares a sequence of PipelineStage entries that the engagement
  protocol reads to track progress, recommend next actions, and verify
  pipeline coherence.
direction: driven
mechanism: code_port
adapter_contract: >
  SKILLSETS list in __init__.py containing Skillset entities with populated
  pipeline fields. Each PipelineStage declares order, skill name,
  prerequisite_gate, produces_gate, description, and consumes list.
  Descriptions must match decision titles recorded by skills (the
  decision-title join).
discovery: di_scan
maturity: mature
hidden_decision: >
  What stages a methodology requires and in what order they execute.
  The practice layer does not know whether a wardley map needs five
  stages or a BMC needs three. The pipeline declaration hides this.
information_expert: >
  The skillset author. They understand the methodology's stage sequence,
  gate dependencies, and what each stage consumes from its predecessor.
structural_tests:
  - doctrine_pipeline_coherence
  - doctrine_decision_title_join
  - doctrine_gate_consumes_declared
semantic_verification: null
---

# Pipeline Declaration

The pipeline declaration capability is the foundational integration
point. Without it, the engagement protocol cannot orchestrate a skillset.

## What the practice layer provides

Engagement orchestration: `practice engagement status` derives pipeline
position for every project by checking gate artifact existence against
the declared pipeline. `practice engagement next` recommends the next
skill to execute based on sequencing rules applied to the derived
positions.

Progress tracking: `practice project progress` reports the current stage,
completed stages, and next prerequisite for a single project. The
decision-title join matches recorded decisions against
`PipelineStage.description` values.

## What the skillset supplies

A `SKILLSETS` attribute in the BC's `__init__.py` containing a list of
`Skillset` entities. Each `Skillset` has a `pipeline` field with ordered
`PipelineStage` entries.

The pipeline is a directed graph of gate dependencies. Stage N's
`produces_gate` is stage N+1's `prerequisite_gate`. The `consumes` list
declares which sections of the prerequisite gate the stage reads — the
consumer-driven contract (Fowler) that makes the coupling between stages
explicit and testable.

## Architectural rationale

The practice layer predicts that every consulting methodology has a
different stage sequence (Protected Variations, Larman). The pipeline
declaration is the stable interface around this variation point. Adding
a new skillset means adding pipeline declarations — the engagement
protocol, progress tracking, and sequencing logic do not change.

The `SKILLSETS` attribute is discovered by filesystem scanning
(`bc_discovery.py`), not by registration. The DI container reads it
during startup. This is the plugin architecture (Uncle Bob): the core
defines the port; plugins satisfy it without modifying the core.

## Verification

Pipeline coherence is verified by three doctrine tests:
- Stages are consecutively ordered with no gaps
- Each stage's `prerequisite_gate` matches the previous stage's
  `produces_gate` (or the shared research gate for stage 1)
- Each stage with a prerequisite declares at least one `consumes` entry
- Decision title strings in the pipeline match the titles recorded by
  skills during execution

These are zero-token CI tests. No language verification is needed
because the adapter is entirely code — Python objects, not markdown.

## References

- [Engagement Protocol](../articles/engagement-protocol.md) — hexagonal
  architecture applied to engagement orchestration
- [Semantic Waist](../semantic-waist.md) — the narrow typed data layer
  that pipelines feed
- [Conformance Testing](../conformance-testing.md) — doctrine tests that
  verify pipeline composition
