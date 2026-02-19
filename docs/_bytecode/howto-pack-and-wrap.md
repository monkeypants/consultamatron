---
source_hash: sha256:bc590ab14cea4c62bcd52e99b02a7d579792ce26e37958a102dc43fb6cf9b9a1
---
Compilation procedure for knowledge pack bytecode. `_bytecode/` mirrors each pack item with a compressed prose summary (no frontmatter). Check freshness with `practice pack status --path <dir>` — reports clean/dirty/absent/corrupt per item.

To compile: read each dirty/absent source item, generate a prose summary at ~10-20% of source token count, write to `_bytecode/{item-name}.md`. Preserve domain vocabulary exactly. Maintain structural fidelity (reflect the source's concerns). Compress examples, rationale, code samples, cross-references.

Nested packs: compile bottom-up (child first). Parent's `_bytecode/{child-name}.md` summarises the child pack from its manifest and `_bytecode/` summaries — never descends into child source items.

Quality bar: compression over completeness, vocabulary precision, structural fidelity, progressive disclosure. Verify: `practice pack status` shows CLEAN, `pytest -m doctrine` passes.
