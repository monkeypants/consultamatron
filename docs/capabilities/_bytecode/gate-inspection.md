---
source_hash: sha256:371e19dafd89eb2e9453033070f765b6827a7b0d07eb3b17fec9c32a06598381
---
Gate inspection derives project state from gate artifacts rather than storing state. The `GateInspector` protocol has a single method `exists()` — Interface Segregation applied. `FilesystemGateInspector` is the production adapter; test implementations return predetermined answers.

Skillsets produce gate files at paths declared in `PipelineStage.produces_gate`, written only after explicit operator confirmation. The `.agreed` suffix is Published Language marking the boundary between nondeterministic LLM proposals and deterministic committed state.

Gate files are immutable after agreement. To change one, re-negotiate and iterate. This immutability makes the semantic waist trustworthy for downstream consumers.

The `GateInspector` is the canonical driven port in hexagonal architecture — dependencies point inward, neither use case nor entity layer knows about the filesystem. Maturity: mature.
