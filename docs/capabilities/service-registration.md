---
type: capability
name: service-registration
description: >
  Practice provides a DI container and CLI command routing. Skillsets
  register domain-specific services, use cases, and CLI commands via
  a register_services() function in __init__.py.
direction: driven
mechanism: code_port
adapter_contract: >
  An optional register_services(container) function in __init__.py that
  receives the DI container and registers BC-specific repositories,
  use cases, and CLI command groups. The function must not import from
  other bounded contexts. Services are registered as attributes on the
  container object.
discovery: di_scan
maturity: established
hidden_decision: >
  What domain-specific services a skillset needs (tour repositories,
  domain use cases, custom CLI commands). The practice layer provides
  the container and routing; the skillset decides what to put in it.
information_expert: >
  The skillset author. They know what repositories, use cases, and
  commands the skillset requires beyond the generic engagement
  lifecycle machinery.
structural_tests: []
semantic_verification: null
---

# Service Registration

Service registration extends the practice CLI with domain-specific
commands and services without modifying the core.

## What the practice layer provides

A DI container (`bin/cli/di.py`) that wires all core protocols to
implementations during startup. After core wiring, the container
iterates discovered BC modules and calls `register_services()` on
each one that declares it.

The CLI command routing extends similarly: BC-specific command groups
are registered through the container and appear under the `practice`
command namespace.

## What the skillset supplies

An optional `register_services(container)` function. The function
receives the container and may register:

- BC-specific repository implementations (e.g. `JsonTourManifestRepository`)
- BC-specific use cases (e.g. `RegisterTourUseCase`)
- BC-specific CLI command groups

The function must not import from other bounded contexts — the
Acyclic Dependencies Principle (Uncle Bob) applies. Each BC's services
depend on practice layer protocols and their own domain model, never on
another BC's internals.

## Architectural rationale

Service registration is the extension mechanism for the plugin
architecture. The three code port capabilities (pipeline declaration,
deliverable presentation, service registration) together constitute
the full plugin contract: what the skillset *is* (pipeline), what it
*produces* (presenter), and what it *needs* (services).

Maturity is established rather than mature because no conformance test
currently verifies service registration correctness. The cross-BC import
test (planned) would catch dependency rule violations. A test verifying
that registered services satisfy their declared protocols would complete
the verification.

## References

- [Conformance Testing](../conformance-testing.md) — cross-BC import
  test, component coupling principles
- [Engagement Protocol](../articles/engagement-protocol.md) §11 —
  the contributor contract
