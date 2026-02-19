---
type: capability
name: conformance-testing
description: >
  Practice provides the doctrine test framework and markers. Skillsets
  supply conftest.py helpers and testing fixtures that verify pipeline
  coherence, gate contracts, and integration correctness. This
  capability is the structural enforcement mechanism for all other
  capabilities.
direction: driven
mechanism: code_port
adapter_contract: >
  A conftest.py in the BC's test directory providing fixtures that
  expose the BC's SKILLSETS, pipeline stages, and workspace paths.
  Tests marked with @pytest.mark.doctrine that verify: pipeline stages
  are coherent, decision titles match stage descriptions, gate consumes
  fields are declared, presenter returns valid ProjectContribution.
  The BC may also provide shape test helpers for its language port
  adapters.
discovery: filesystem_convention
maturity: established
hidden_decision: >
  What a valid bounded context looks like from the integration
  perspective. The practice layer defines the doctrine test markers
  and common fixtures. The skillset provides the BC-specific fixtures
  and any additional doctrine tests that verify domain-specific
  integration requirements.
information_expert: >
  The practice layer for generic integration tests (pipeline coherence,
  component coupling). The skillset author for domain-specific
  integration tests (gate content validity, presenter output structure).
structural_tests:
  - doctrine_test_markers_exist
semantic_verification: null
---

# Conformance Testing

Conformance testing is the meta-capability — it is the structural
enforcement mechanism for all other capabilities. Python Protocol
classes are the compile-time contracts (shape). Conformance tests are
the behavioural contracts (composition). Together they are the complete
specification of what a bounded context must be.

## What the practice layer provides

The `pytest -m doctrine` gate that runs before every push. Doctrine
tests verify structural properties of BC composition:

- **Pipeline coherence**: stages are consecutively ordered, gate chains
  are connected, consumes fields are declared
- **Component coupling**: no cross-BC imports (Acyclic Dependencies
  Principle), BCs depend on practice layer (Stable Dependencies), practice
  layer is abstract (Stable Abstractions)
- **Decision-title join**: recorded decision titles match pipeline stage
  descriptions
- **Presenter output**: presenters return valid ProjectContribution entities

These tests are fast, deterministic, and cheap. They run in under a
second with no network, no LLM, no file I/O beyond fixture loading.

## What the skillset supplies

BC-specific test fixtures in `conftest.py`: the BC's SKILLSETS list,
workspace path helpers, and any domain-specific test helpers. The
fixtures expose the BC's integration surface to the generic doctrine
tests.

Optionally, the BC provides additional doctrine tests for domain-specific
integration requirements. A WM skillset might test that its presenter
handles the OWM-to-HTML conversion correctly. A BMC skillset might test
that its canvas block assembly produces valid content pages.

## Architectural rationale

Larman's Law 4 (culture follows structure): documenting the integration
protocol is necessary but insufficient. The protocol works when
contributors follow the instructions. It fails when they don't — and
without conformance tests, there is no mechanism to detect the failure.

Conformance tests make the correct path the only path that passes CI.
A contributor runs `pytest -m doctrine` and gets immediate feedback on
whether their pipeline composes with the engagement protocol. The
protocol is invisible to the skillset — tests read gate artifacts and
pipeline definitions, never calling into skillset code.

## The two-sided contributor contract

Skillset authors provide: pipeline declarations, testing helpers, and
gate-producing skills. The core guarantees: discovery, progress
tracking, conformance verification, and deliverable rendering.

This two-sided contract is structural, not cultural. The doctrine tests
are the structural enforcement of the core's side. The pipeline
declarations are the structural enforcement of the skillset's side.
Both are verified by `pytest -m doctrine`.

## Language port verification

Conformance testing for code ports is mature. For language ports, the
verification architecture is emerging (see language-port-testing.md).
Shape tests (Tier 0) for language port adapters will extend the
doctrine test suite — verifying that pack manifests parse, typed items
have frontmatter, and protocol contracts have minimum structural
elements. These are zero-token CI tests that complement the existing
code port verification.

## References

- [Conformance Testing](../conformance-testing.md) — the full treatment
  of doctrine tests, component coupling, and structural enforcement
- [Language Port Testing](../articles/language-port-testing.md) —
  extending verification to language port adapters
