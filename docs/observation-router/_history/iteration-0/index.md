---
name: iteration-0-origin
purpose: >
  Compressed output of the conversation that discovered the
  observation-and-routing pattern. Contains the jedi council
  deliberation (compressed), operator refinements, and the general
  pattern specification that emerged.
---

# Iteration 0 — Origin

Session that began with client workspace architecture questions and
arrived at a general pattern for observation capture and routing across
the consulting practice.

## Conversation arc

1. Operator noticed client workspaces share structural characteristics
   with skillsets — both have knowledge packs produced by research
   activities.
2. Identified that shared kernels follow the pack convention at every
   hierarchy level. Documented this in `docs/integration-surface.md`
   (new section: "Shared kernels follow the pack convention") and
   cross-referenced in `docs/context-mapping-the-integration-surface.md`.
   Bytecodes compiled.
3. Operator articulated the desire to accumulate bespoke client
   expertise — build a "digital twin," develop use cases, execute
   during engagements, and route improvements back into skillsets.
4. Analysis identified three routing destinations for engagement
   learnings: client workspace, skillset source, practice layer.
5. Jedi council deliberation (7 luminaries) on client expertise
   accumulation and knowledge routing.
6. Council synthesis + operator negotiation produced the general
   observation-and-routing pattern.
7. Operator identified knowledge-iteration (pack-wrap-and-stack) as
   the methodology for developing the specification.

## Jedi council deliberation — compressed

**Council**: Evans, Weinberg, Cunningham, Parnas, Larman, Brooks, Anthropic
**Problem**: How should the practice accumulate client expertise and route
engagement learnings?

**Positions (one-line each):**
- **Evans**: Client workspace is a bounded context with its own aggregate
  root (ClientProfile), ubiquitous language (stakeholders, preferences,
  constraints), and Customer-Supplier relationship to methodology
  skillsets. Learnings are domain events needing explicit routing.
- **Weinberg**: Build a "client file" (knowledge pack of qualitative
  observations), not a formal entity model. Observations with dates,
  not typed properties with invariants. Client knowledge degrades
  gracefully when stale.
- **Cunningham**: Wiki-nature growth — sections grow where attention goes.
  CRC cards for routing: Client Knowledge Steward, Methodology
  Improvement Router, Practice Improvement Router. Client knowledge
  debt as a named concept.
- **Parnas**: Three kinds of knowledge change independently (client,
  methodology, engagement) — they're already in different modules.
  What's missing is the interface between them. Client knowledge module
  is a knowledge pack, not an entity model. Hides client-specific
  structure behind the existing pack convention.
- **Larman**: Review skill is the Information Expert for learning
  classification. Separate classification (judgment) from dispatch
  (mechanical). Protected Variations for routing destinations.
  Structure must make routing the path of least resistance.
- **Brooks**: Match model resolution to decision resolution. Current
  decisions are coarse — a knowledge pack of observations suffices.
  Strategic DDD yes (bounded context, published language), tactical
  DDD not yet (no entity model until invariant enforcement is needed).
- **Anthropic**: Client knowledge is a runtime knowledge pack, same
  convention as design-time packs. Routing is post-review mechanical
  dispatch driven by classification tags. Client workspace participates
  in existing integration surface capabilities — no new infrastructure.

**Consensus:**
- Knowledge pack, not entity model (for now)
- Learning routing is the critical missing capability
- Client workspace IS a bounded context (revises the context-mapping article)
- Customer-Supplier relationship to methodology skillsets
- Review classifies, routing dispatches — separate concerns

**Divergence:**
- Model resolution: Evans wants typed entities, Weinberg/Parnas/Brooks
  want prose observations. Resolution: start with pack, promote to
  entities when invariant enforcement is needed.
- Pipeline: Evans/Larman see stages, Weinberg/Brooks/Parnas resist.
  Resolution: no pipeline — use rs-assess quality assessment pattern
  instead.
- Classification ownership: all agree review skill classifies, but
  should it also dispatch? Resolution: separate — review classifies,
  routing use case dispatches.

## Operator refinements (post-council)

**Observation/routing split.** The split between "make observation"
(high freedom — judgment about what's interesting) and "route
observation" (low freedom — classify and dispatch mechanically) is the
key architectural insight.

**Pipeline AND opportunistic coexist.** The engagement review is a
deliberate, comprehensive reflection point (all relevant topics
considered). But observations can also be made at any gatepoint if
something important surfaces. Review catches what opportunistic
observation missed; opportunistic observation captures context-rich
signal that review would have to re-derive.

**Bag of tricks per inflection point.** Each inflection point type has
its own set of "interesting types of observations to make." These bags
grow independently with practice experience.

**Pack-and-wrap reflection is local.** When compiling bytecode, the
agent deeply reads content — a natural moment to notice things about
that content. But the routing is different: observations are about
the pack itself (structural issues, stale claims, missing
cross-references). The right action is local (select summarisation
strategy, flag for author) rather than cross-pollinating other packs.

**Pedagogic gradient descent is an instance.** The evidence-of-
understanding architecture (from `docs/pedagogic-gradient-descent/`)
is the observation-and-routing pattern applied specifically to operator
knowledge. The negotiate loop is an inflection point, the reflection
strategy is pedagogic, the observations go to the operator evidence
tree.

**The general mechanism.** Identify the point of reflection → identify
the right questions to ask → ask them → route the answers.

## The general pattern

**Inflection point → Reflection strategy → Observations → Classification → Routing**

| Inflection point | Strategy | Observation domain | Routing |
|---|---|---|---|
| Engagement review | Deliberate, comprehensive | Client, methodology, practice, operator | Cross-context (4 destinations) |
| Gatepoint | Opportunistic, lightweight | Whatever surfaced during negotiation | Cross-context (same 4 destinations) |
| Pack-and-wrap | Content-focused | The item being compiled | Local (summarisation strategy selection) |
| Negotiate loop | Pedagogic | Operator understanding of concepts | Operator evidence tree |

**Four observation domains:**
- **Client** — stakeholder needs, internal politics, preferences, constraints → client knowledge pack
- **Methodology** — what works, what doesn't, approach improvements → skillset source (personal/partnership/commons)
- **Practice** — engagement process effectiveness, platform improvements → practice docs
- **Operator** — understanding of concepts, fluency signals → operator evidence tree

**Each inflection point has its own bag of tricks** — types of observations
worth making and questions worth asking at that moment. The bags grow
independently with practice experience.

**Every inflection point is a moment where the agent has rich context
that is about to be lost.** The reflection strategy's job is to extract
durable value from that transient context before it evaporates.

## Agreed summarisation strategies (for this compression)

- Preserve: general pattern, inflection point taxonomy, four observation
  domains, observation/routing split, council synthesis, operator refinements
- Compress: individual luminary arguments to one-line positions, initial
  shared kernel conversation to completed-output summary, explanatory
  analysis to key claims
- Drop: file navigation, false starts, meta-discussion, superseded recaps
- Organisation: stack under `docs/observation-router/_history/iteration-0/`

## What moves to the accumulator (next iteration)

Candidate accumulator items to extract:
- The general pattern (inflection point → reflection → observation → classification → routing)
- The inflection point taxonomy (with per-type bags of tricks)
- The observation domain taxonomy (with routing destinations)
- The observation/routing architectural split (high freedom / low freedom)
- Software change specification (what needs to change in review, gatepoint handling, pack-and-wrap)
