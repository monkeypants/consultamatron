---
source_hash: sha256:d9190a5b5f6f3f62b6ed48c39cc5d24d0d069a0065eafc3bc93d4c6545b3c430
---
Conformance testing is the meta-capability enforcing all other capabilities structurally. `pytest -m doctrine` runs before every push, verifying: pipeline coherence (consecutive ordering, connected gate chains, declared consumes), component coupling (no cross-BC imports, stable dependencies), decision-title join, and presenter output validity.

Skillsets supply `conftest.py` with fixtures exposing SKILLSETS, pipeline stages, and workspace paths. Optionally, BCs provide additional domain-specific doctrine tests.

Tests are fast, deterministic, zero-token, zero-network. The two-sided contributor contract: skillsets provide pipeline declarations and testing helpers; the core guarantees discovery, progress tracking, conformance verification, and deliverable rendering.

Language port verification is emerging via shape tests (Tier 0) for pack manifests, typed items, and protocol contracts. Maturity: established.
