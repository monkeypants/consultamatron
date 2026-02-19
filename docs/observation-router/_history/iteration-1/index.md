---
name: iteration-1-extraction-and-security
purpose: >
  Compressed output of iteration 1. Extracted accumulator items from
  iteration-0, refined the model through operator negotiation (needs-driven
  observation, routing security), ran two deliberations (testing strategy,
  destination eligibility).
---

# Iteration 1 — Extraction and Security Model

Extracted accumulator items from iteration-0 compressed material.
Operator refinement during extraction fundamentally changed the
observation model and established the security posture for routing.

## Conversation arc

1. Read iteration-0 history and knowledge-iteration methodology.
2. Extracted five candidate accumulator items from compressed material.
3. Operator refined negotiate loop: multi-scope, not just pedagogic.
   Any inflection point with rich context should serve all domains,
   not just the one it's nominally about.
4. Operator introduced needs-driven observation model: destinations
   declare information needs (like actor-goals for sensory apparatus),
   CLI aggregates needs into a brief, skills apply the brief to
   transient context. Replaces the vague "bag of tricks" concept.
   Classification collapses — observations made in response to
   declared needs already carry their destination.
5. Observation needs protocol captured: inheritance model (type-level
   generic needs extended by instance-level specifics), CLI
   aggregation use case, needs declarations live with their owners.
6. Beck-Larman deliberation on testing the aggregation use case.
7. Operator identified destination eligibility as the hardest
   problem — not aggregation, not observation, but scoping.
8. Full jedi council on destination eligibility (7 luminaries).
   Council consensus: start permissive, tighten later.
9. Operator corrected the council: routing is information transfer,
   not noise. Ineligible destinations are data leaks — catastrophic,
   trust-destroying. Deny-all, allow-some.
10. Routing security model captured with three destination classes.

## Operator refinements

**Needs-driven observation.** The earlier model was observe-then-
classify-then-route. The operator reframed: destinations are expert
on their own information needs. The observation process gathers
requirements first, then analyses context. "What's relevant?" is
answered by "what do the consumers need?" The needs brief functions
like actor-goals for sensory apparatus — each destination is an
actor with goals for what it needs to learn.

**Negotiate loop is multi-scope.** The iterate-0 formulation limited
negotiate loop observations to operator understanding (pedagogic).
The operator pointed out: the agent has deep loaded context during
negotiation — limiting observations to one domain wastes the
opportunity. All four domains are available at negotiate loops.

**Needs compress naturally.** The "large table of needs" is an
imaginary problem. The same skillset across engagements collapses
to one set of needs. The same client across engagements collapses
to one. Distinct needs deduplicate.

**Routing security, not noise.** The council optimised for
observation quality (noise in the brief). The operator identified
the real risk: information leakage. Routing observations to
ineligible destinations could be catastrophic — trust destroyed,
system discontinued. The correct default is deny-all.

**Dark channel for commons.** Commons skillsets cannot receive
direct observation routing — provenance would be traceable. Commons
improvements flow through the private MCP channel (GitHub #23)
where the operator controls disclosure.

## Beck-Larman testing deliberation — compressed

**Problem:** How to test the `practice observation-needs` use case.

**Key conclusions:**
- Test the aggregator, not the observation. Observation quality is
  operator judgment — not machine-testable.
- Aggregator contract: `aggregate(destinations) → brief`. Clean,
  testable.
- Five-test pyramid: (1) need declaration at type level, (2) need
  declaration at instance level, (3) single-destination aggregation,
  (4) multi-destination aggregation, (5) CLI integration.
- Test through the use case interface, not file format. Protected
  Variations on the brief format.
- Start with needs as literal strings. Let tests drive when richer
  structure is needed.
- "Identify relevant destinations" was initially collapsed into test
  setup by Beck — but the operator later identified it as the
  hardest problem.

## Eligibility council — compressed

**Council:** Evans, Larman, Parnas, Weinberg, Brooks, Beck, Cunningham
**Problem:** Which destinations are eligible to contribute observation
needs and receive observations?

**Positions (one-line each):**
- **Evans:** Engagement is the aggregate defining transactional
  boundary for context participation. Client workspace persists
  across engagements, always in scope.
- **Larman:** Information Expert — each node knows its eligible
  children. Controller pattern for CLI. Protected Variations on
  eligibility algorithm.
- **Parnas:** Each hierarchy level is a module exposing a narrow
  export interface. Aggregator walks the tree asking each node.
- **Weinberg:** Cost asymmetry — missed observations lose knowledge
  permanently, noise merely wastes attention. Start permissive.
- **Brooks:** Don't design filters for a pipeline that doesn't
  exist. Build first, filter when noise is measured.
- **Beck:** Simplest thing: no eligibility rules. Include everything.
  YAGNI on scoping rules.
- **Cunningham:** Enumerate, don't filter. Wiki-nature — grow
  inclusively, curate over time. Observation debt as named concept.

**Council consensus:** Start permissive, tree walk with per-node
export policy, tighten when evidence warrants.

**Operator correction:** Council got the risk model wrong. Routing
is information transfer, not observation quality. Deny-all,
allow-some. Three destination classes with different security
postures (personal: greedy; engagement-scoped: allow per config;
commons: dark channel only).

## Accumulator items produced

Six items in the pack after this iteration:
1. `general-pattern.md` — four-stage needs-driven pattern
2. `inflection-point-taxonomy.md` — four types, three cross-context
3. `observation-needs-protocol.md` — destinations declare needs,
   inheritance, CLI aggregation
4. `observation-routing-split.md` — high/low freedom separation
5. `routing-security-model.md` — deny-all, three destination classes
6. `software-changes.md` — platform change specification sketch

## Agreed summarisation strategies (for this compression)

- Preserve: operator refinements (needs-driven, negotiate scope,
  security correction, dark channel), Beck-Larman test conclusions,
  council synthesis + operator correction
- Compress: individual council positions to one-line, Beck-Larman
  conversation to key conclusions
- Drop: superseded formulations (five-stage, bag of tricks, passive
  domain buckets), meta-discussion, file creation mechanics
- Organisation: single document under `_history/iteration-1/`
