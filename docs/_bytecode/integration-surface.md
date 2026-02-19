---
source_hash: sha256:870fd4e496dce6947a2c9d281756d0e2a5246bd8da277199c53bbed49f772f89
---
The integration surface is the collection of contracts at the practice/skillset boundary — twelve independent Skillset Capabilities composing the Consultamatron Integration Protocol. Faceted decomposition by the Parnas criterion: each capability encapsulates one independently varying design decision.

Two enforcement mechanisms: code ports (Python Protocol classes, zero tokens, CI-enforced — pipeline declaration, gate inspection, deliverable presentation, service registration, conformance testing) and language ports (filesystem conventions, token-burning verification — knowledge packs, knowledge protocols, research strategies, analysis, pedagogic metadata). Two capabilities (iteration evidence, voices) have no mechanism yet.

Each capability has: name, description, direction (all currently driven), mechanism, adapter_contract, discovery (DI scan / filesystem convention / pack manifest / not defined), maturity (nascent → established → mature), hidden_decision (Parnas), information_expert (Larman), structural_tests, semantic_verification.

Shared kernels follow the pack convention at every hierarchy level: `docs/` (practice), `{skillset}/docs/` (skillset), `clients/{org}/resources/` (client), `{engagement}/resources/` (engagement). Pattern: a parent context's knowledge pack directory is the shared kernel for its children — produced by research-like activity, follows semantic pack convention, immutable after agreement. `doctrine_pack_shape` tests transitively verify shared kernel structure. Friction diagnostic: if siblings need different formats from shared data, the kernel is too large — narrow it and add per-context ACLs (research skills).

The Capability entity frontmatter in `docs/capabilities/` is simultaneously documentation and a structured evaluation surface for rs-assess. Not a framework — skillsets declare data and supply files, not inherit base classes.
