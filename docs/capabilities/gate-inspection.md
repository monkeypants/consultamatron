---
type: capability
name: gate-inspection
description: >
  Practice derives project state from gate artifacts. The GateInspector
  protocol abstracts existence-checking so that use cases are insulated
  from storage mechanism (filesystem, database, test fixture).
direction: driven
mechanism: code_port
adapter_contract: >
  Gate files produced at the paths declared in PipelineStage.produces_gate,
  relative to the project workspace directory. Files use the .agreed.md or
  .agreed.owm suffix to indicate operator-confirmed artifacts. Gate content
  satisfies the consumes declarations of the next pipeline stage.
discovery: di_scan
maturity: mature
hidden_decision: >
  How and where gate artifacts are stored. The practice layer checks
  existence through GateInspector.exists() and never touches the
  filesystem directly. Today gates are files; tomorrow they could be
  manifest entries or database rows.
information_expert: >
  The skill that produces the gate. It knows the artifact format, the
  operator agreement that produced it, and the evidence it rests on.
  The GateInspector only knows whether the gate exists.
structural_tests:
  - doctrine_pipeline_coherence
semantic_verification: null
---

# Gate Inspection

Gate inspection is the state derivation mechanism. The engagement
protocol does not store engagement state — it derives state from the
existence of gate artifacts (State Derivation not State Storage, Fowler).

## What the practice layer provides

The `GateInspector` protocol with a single method:

```python
class GateInspector(Protocol):
    def exists(self, client: str, engagement: str,
               project: str, gate_path: str) -> bool: ...
```

Interface Segregation (Uncle Bob): one method, one question. The
engagement protocol needs to know if a gate exists — nothing more.

`FilesystemGateInspector` is the production adapter. It checks whether
a file exists at the expected workspace path. Test implementations
return predetermined answers.

## What the skillset supplies

Gate files at the paths declared in `PipelineStage.produces_gate`. The
gate file is produced by a skill during the propose-negotiate-agree
loop and written only when the operator explicitly confirms. The
`.agreed` suffix is the Published Language (Evans) marking the boundary
between nondeterministic LLM proposals and deterministic committed state.

Gate content must satisfy the `consumes` declarations of the downstream
stage — the consumer-driven contract. This content contract is a
language port concern that overlaps with this code port capability.

## Architectural rationale

The `GateInspector` is the canonical driven port in the hexagonal
architecture (Cockburn). Dependencies point inward: the engagement
use case depends on the `GateInspector` protocol (abstraction); the
`FilesystemGateInspector` depends on the use case layer by implementing
its protocol. Neither the use case nor the entity layer knows about
the filesystem.

Gate files are immutable after agreement. To change one, re-negotiate
and iterate — do not overwrite. This immutability makes the semantic
waist trustworthy: downstream consumers know an `.agreed` file will
not change under them.

## References

- [Engagement Protocol](../articles/engagement-protocol.md) §4 —
  hexagonal architecture, driver and driven ports
- [Semantic Waist](../semantic-waist.md) — gate artifacts as
  deterministic backbone
