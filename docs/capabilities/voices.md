---
type: capability
name: voices
description: >
  Practice would provide operator pedagogy repackaging — transforming
  analytical output through alternate communication styles calibrated
  to operator cognitive style. Skillsets would supply voice profiles as
  semantic pack items. Currently prompt-pattern only.
direction: driven
mechanism: undefined
adapter_contract: >
  Not yet defined. The expected shape when promoted from prompt pattern:
  voice profile items with type: voice frontmatter in a voices/ knowledge
  pack. Each profile describes a communication style, cognitive outcome,
  strengths, limitations, and suitable-for-concepts metadata. The voice
  layer receives completed analysis as input and produces repackaged
  explanation as output — a pure transform with no side effects on
  analytical artifacts.
discovery: not_defined
maturity: nascent
hidden_decision: >
  What communication styles are effective for a domain's concepts. A
  physics-analogy style (Feynman) works for evolution theory. A deadpan
  procedural style (Garden) works for complex synthesis. The practice
  layer would provide the repackaging mechanism; the skillset would
  know which voices serve its domain.
information_expert: >
  The skillset author for voice selection (which communication styles
  serve the domain's concepts). The operator for voice preference
  (which style their brain absorbs best). The practice layer for
  invocation mechanics (when to offer repackaging, how to execute it).
structural_tests: []
semantic_verification: null
---

# Voices

Voices are alternate communication styles for analytical output. The
analytical content is the core domain (the diagnosis). The voice is an
output adapter (the bedside manner). The same analysis delivered through
different cognitive pathways for different operators.

## Current state: prompt pattern

The voices concept currently works as a prompt pattern. The operator
says "explain that like Feynman" and the agent applies the communication
style from its training data. No protocol, no pack, no infrastructure.
This works for well-known figures whose communication style the model
has strong priors on.

## Promotion trigger

Promote to a protocol when the prompt pattern demonstrably fails:
- Voice characterisation drifts across sessions
- The operator wants consistent voice profiles the system remembers
- Preference persistence becomes a practical need
- Domain-specific voices (not in training data) are required

## Expected architecture when promoted

The voices protocol would be a separate bounded context from the
pantheon protocol (Evans, Round 2 deliberation). A luminary has a
framework of ideas. A voice has a way of communicating. Different
domain models, different contracts:

| | Pantheon | Voices |
|---|---|---|
| Entity | Luminary | Voice |
| Contract | Contribution, invocation trigger | Communication style, cognitive outcome |
| Use case | Jedi council (analytical synthesis) | Operator pedagogy (delivery repackaging) |
| Relationship to analysis | Produces the analysis | Repackages the analysis |

The voice layer is a pure transform — Protected Variations (Larman)
requires absolute insulation of analysis from delivery. The gate
artifact is always the analytical artifact, never the voice-repackaged
version.

## The two-stage persona pipeline

When both analysis and voices capabilities are active, the operator
gets a two-stage pipeline: luminaries analyse (their frameworks applied
to the problem), then a voice explains (the synthesis adapted to the
operator's brain). This is a legitimate Prompt Chaining Pattern —
each stage has a clear input/output contract and a distinct purpose.

## References

- [Voices Protocol](../articles/voices-protocol.md) — jedi council
  deliberation on the voices concept, with live demonstrations
- [Wetware Efficiency](../wetware-efficiency.md) — operator cognition,
  the graduation gradient, multiple delivery channels
