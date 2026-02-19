---
source_hash: sha256:b7ac8826cf121aa32a79d7268dd68a94773fd9e201c424a0f69a8b3e60b72630
---
Pipeline declaration is the foundational integration point. Skillsets declare `SKILLSETS` in `__init__.py` containing `Skillset` entities with ordered `PipelineStage` entries. Each stage declares order, skill name, prerequisite_gate, produces_gate, description, and consumes list.

The practice layer derives engagement state from these declarations: `engagement status` checks gate existence against declared pipelines, `engagement next` recommends the next skill, `project progress` reports current stage. The decision-title join matches recorded decisions against stage descriptions.

Pipeline is a directed graph of gate dependencies. Stage N's `produces_gate` is stage N+1's `prerequisite_gate`. The `consumes` list makes inter-stage coupling explicit and testable (consumer-driven contract).

Discovery via filesystem scanning (`bc_discovery.py`), wired through DI container. Verified by three zero-token doctrine tests: pipeline coherence, decision-title join, gate consumes declared. Maturity: mature.
