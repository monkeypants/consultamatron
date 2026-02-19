Service registration extends the practice CLI with domain-specific commands and services. Skillsets provide an optional `register_services(container)` function in `__init__.py` that receives the DI container and registers BC-specific repositories, use cases, and CLI command groups.

The DI container (`bin/cli/di.py`) wires core protocols during startup, then iterates discovered BC modules calling `register_services()` on each. The function must not import from other BCs (Acyclic Dependencies Principle).

The three code port capabilities together constitute the full plugin contract: pipeline declaration (what the skillset is), deliverable presentation (what it produces), service registration (what it needs).

No conformance test currently verifies registration correctness. Cross-BC import tests and protocol satisfaction tests are planned. Maturity: established.
