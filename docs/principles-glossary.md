# Principles Glossary

Canonical index of named design principles applied in Consultamatron.
Each entry: attribution, kernel, and where it is applied in the docs.

---

## Larman (GRASP / LeSS)

### Protected Variations
**Larman (GRASP).** Identify points of predicted variation and create
stable interfaces around them.
**Applied:** engagement-protocol.md § 5 (GateInspector protocol).

### Low Coupling
**Larman (GRASP).** Minimise dependencies between elements so that
changes in one do not cascade.
**Applied:** engagement-protocol.md § 5 (engagement use cases depend
only on protocols and entities).

### Information Expert
**Larman (GRASP).** Assign responsibility to the class that has the
information needed to fulfil it.
**Applied:** docstring-conventions.md § The principle (each docstring
layer documents what its reader needs); integration-surface.md §
The hidden decision / information expert pair (who fills each side
of a capability boundary).

### Larman's Law 1: Power-Structure Inertia
**Larman.** Organisations are implicitly optimised to avoid changing
existing power structures.
**Applied:** dev/conformance-testing.md § Why structural, not cultural.

### Larman's Law 2: Terminology Absorption
**Larman.** New terminology is adopted but behaviour remains unchanged.
**Applied:** dev/conformance-testing.md § Why structural, not cultural.

### Larman's Law 3: Pragmatism Defence
**Larman.** The status quo is defended as the only pragmatic option.
**Applied:** dev/conformance-testing.md § Why structural, not cultural.

### Larman's Law 4: Culture Follows Structure
**Larman.** Culture and behaviour follow organisational structure; to
change behaviour, change the structure.
**Applied:** engagement-protocol.md § 6 (structural enforcement over
documentation).

### Feature Teams over Component Teams
**Larman (LeSS).** Each contributor owns the full vertical slice rather
than one horizontal layer. No architecture review board.
**Applied:** dev/conformance-testing.md § Why structural, not cultural.

### Community of Practice over Review Board
**Larman.** Quality patterns shared through example and documentation,
not committee approval.
**Applied:** dev/conformance-testing.md § Why structural, not cultural.

---

## Uncle Bob (Clean Architecture / SOLID / Component Principles)

### Clean Architecture Dependency Rule
**Uncle Bob.** Source code dependencies must point only inward, toward
higher-level policies.
**Applied:** engagement-protocol.md § 3; semantic-waist.md § What the
waist is made of.

### Screaming Architecture
**Uncle Bob.** The directory structure should declare the application's
purpose, not its framework.
**Applied:** engagement-protocol.md § 3 (use cases as table of
contents).

### Use Cases as Central Concept
**Uncle Bob / Jacobson.** Use cases are the organising unit of
application architecture.
**Applied:** semantic-waist.md § What the waist is made of;
engagement-protocol.md § 3.

### Interface Segregation Principle
**Uncle Bob (SOLID).** No client should be forced to depend on methods
it does not use.
**Applied:** engagement-protocol.md § 5 (GateInspector has one method);
integration-surface.md § Why facets, not a monolithic contract (each
capability is a separate port, not one giant skillset interface).

### Dependency Inversion Principle
**Uncle Bob (SOLID).** High-level modules depend on abstractions, not
low-level implementations.
**Applied:** engagement-protocol.md § 5 (use cases depend on
GateInspector protocol, not filesystem).

### Open/Closed Principle
**Uncle Bob (SOLID).** Open for extension, closed for modification.
**Applied:** deliverable-architecture.md § Adding a new skillset
(presenter plugins require no core changes).

### Plugin Architecture
**Uncle Bob / Fowler.** Core defines ports; extensions satisfy them
without modifying the core.
**Applied:** engagement-protocol.md § 11 (skillsets as plugins);
integration-surface.md § The pattern (twelve capabilities as typed
ports that skillsets satisfy).

### Acyclic Dependencies Principle
**Uncle Bob.** No cycles in the package dependency graph.
**Applied:** dev/conformance-testing.md § Component coupling principles
(cross-BC import test).

### Stable Dependencies Principle
**Uncle Bob.** Depend in the direction of stability. Volatile packages
depend on stable packages, never the reverse.
**Applied:** dev/conformance-testing.md § Component coupling principles
(`practice` is stable; BCs depend on it).

### Stable Abstractions Principle
**Uncle Bob.** A component should be as abstract as it is stable.
Concrete implementations belong in volatile packages.
**Applied:** dev/conformance-testing.md § Component coupling principles
(`practice` is abstract; BCs are concrete).

### LLM as Framework Detail
**Uncle Bob.** The LLM belongs in the outermost ring. Core logic must
not depend on which model executes a skill.
**Applied:** engagement-protocol.md § 3 (Clean Architecture applied).

---

## Fowler (DDD / Integration Patterns)

### Consumer-Driven Contracts
**Fowler.** The consumer declares what it needs from a service; the
producer is obligated to satisfy those declarations.
**Applied:** engagement-protocol.md § 7 (gate `consumes` field).

### Tolerant Reader
**Fowler.** Consumers should depend on as little of the contract as
possible, ignoring fields they do not need.
**Applied:** engagement-protocol.md § 7 (narrow `consumes`
declarations).

### Shared Kernel
**Fowler / Evans (DDD).** A small, shared subset of the domain model
that multiple bounded contexts depend on. Minimise this surface.
**Applied:** semantic-waist.md § DDD vocabulary for the waist
(`resources/` directory).

### Published Language
**Fowler / Evans (DDD).** A well-documented data format that serves as
the contract between contexts.
**Applied:** semantic-waist.md § DDD vocabulary for the waist (gate
artifact schemas, `resources/index.md` format).

### Anti-Corruption Layer
**Fowler / Evans (DDD).** A translation layer that converts a foreign
model into the local context's terms.
**Applied:** semantic-waist.md § DDD vocabulary for the waist
(per-skillset research skills translate neutral research into
domain-specific vocabulary).

### Context Map
**Fowler / Evans (DDD).** A strategic overview of bounded context
relationships and integration patterns.
**Applied:** semantic-waist.md § DDD vocabulary for the waist (the
`engage` skill as executable context map);
context-mapping-the-integration-surface.md (full context map of the
practice/skillset boundary).

### Conformist
**Evans (DDD).** A downstream context accepts the upstream model without
translation, using the upstream types directly.
**Applied:** context-mapping-the-integration-surface.md § Skillsets are
Conformists with influence (skillsets populate PipelineStage and
ProjectContribution directly).

### Customer-Supplier
**Evans (DDD).** Upstream context plans with downstream needs in mind;
downstream has influence but not control over the shared model.
**Applied:** context-mapping-the-integration-surface.md § Skillsets are
Conformists with influence (practice layer evolves schemas considering
skillset needs; influence channel is the PR process).

### Open Host Service
**Evans (DDD).** A context exposes a general-purpose protocol that any
consumer can use without bilateral negotiation.
**Applied:** context-mapping-the-integration-surface.md § The practice
layer is an Open Host Service (semantic pack convention, discovery
mechanisms, capability contracts).

### Separate Ways
**Evans (DDD).** Two contexts have no integration and operate
independently.
**Applied:** context-mapping-the-integration-surface.md § Separate Ways
is structural, not accidental (skillsets have no inter-dependencies;
enforced by `doctrine_no_cross_bc_imports`).

### Partnership
**Evans (DDD).** Two contexts succeed or fail together and co-evolve
their integration.
**Applied:** context-mapping-the-integration-surface.md § Partnership
exists at the human-agent boundary (propose-negotiate-agree loop;
gate artifacts require bilateral agreement).

### Gate Artifacts as Deterministic Backbone
**Fowler.** The `.agreed` suffix marks the boundary between
nondeterministic LLM proposals and deterministic committed state.
**Applied:** semantic-waist.md § The design double diamond.

### Orchestration vs Choreography
**Fowler.** Within an engagement, explicitly plan and sequence
(orchestration). Across projects, suggest but do not enforce
dependencies (choreography).
**Applied:** engagement-protocol.md § 11 (How a skillset plugs in).

### Pipeline Idempotency
**Fowler.** Stateless transformations that read gates and propose new
gates. Running a skill twice on the same input should produce the same
proposal. State lives in gate artifacts, not skill execution.
**Applied:** prompt-engineering.md § Operational patterns.

### Value Objects vs Entities
**Fowler / Evans.** Value objects are identity-less, immutable, compared
by value. Use them for derived state that should not be persisted.
**Applied:** engagement-protocol.md § 8 (EngagementDashboard,
ProjectPipelinePosition).

### State Derivation not State Storage
**Fowler.** Derive engagement state from existing artifacts rather than
storing it in a separate database. Gate files are the canonical state.
**Applied:** engagement-protocol.md § 8.

---

## Parnas (Information Hiding / Modular Decomposition)

### Information Hiding
**Parnas.** Each module hides a design decision that is likely to change.
The module interface is stable; the hidden decision varies.
**Applied:** integration-surface.md § The hidden decision / information
expert pair (each capability encapsulates one design decision that varies
independently across skillsets).

### Hard Hiding (Code Enforcement)
**Parnas / Consultamatron.** The hidden decision is enforced by code —
Python Protocol classes, type checking, conformance tests. Violation is
detectable at import time or CI. Zero tokens.
**Applied:** integration-surface.md § Two mechanisms (code ports enforce
hard hiding).

### Soft Hiding (Convention Enforcement)
**Parnas / Consultamatron.** The hidden decision is documented as a
convention but enforced through language-level evaluation. Violation
requires token-burning verification to detect.
**Applied:** integration-surface.md § Two mechanisms (language ports
enforce soft hiding); articles/language-port-testing.md (the three-tier
verification strategy for soft hiding).

---

## Cockburn (Hexagonal / Crystal / Heart of Agile)

### Hexagonal Architecture (Ports and Adapters)
**Cockburn.** Application logic communicates with the outside world
through ports; adapters translate between the port and external
technology.
**Applied:** engagement-protocol.md § 4.

### Walking Skeleton
**Cockburn.** The thinnest possible end-to-end slice that proves the
architecture works.
**Applied:** engagement-protocol.md § 4, § 10.

### Driver and Driven Ports
**Cockburn.** Driver ports are how the outside invokes the application;
driven ports are how the application invokes external services.
**Applied:** engagement-protocol.md § 4 (CLI as driver, GateInspector
as driven).

### Fully Dressed Use Case
**Cockburn.** Use case format with preconditions, trigger, main success
scenario, and extensions. "Extensions are where the real design lives."
**Applied:** engagement-protocol.md § 2 (engagement execution use case).

### Crystal Methodology Tuning
**Cockburn.** Different projects need different process weights. The
Cockburn Scale classifies by criticality × size.
**Applied:** engagement-protocol.md § 6 (engagement classification
driving gate evidence requirements).

### Heart of Agile Mapping
**Cockburn.** Four pillars: Collaborate, Deliver, Reflect, Improve.
All four are structurally present in Consultamatron.
**Applied:** engagement-protocol.md § 6 (propose-negotiate-agree =
Collaborate, gates = Deliver, engagement log = Reflect, skillset
engineering = Improve).

---

## Anthropic (Skills Engineering / Agent Architecture)

### Freedom Levels
**Anthropic.** Calibrate agent latitude (high/medium/low) per skill
based on task fragility.
**Applied:** prompt-engineering.md § Semantic bytecode;
engagement-protocol.md § 9.

### Progressive Disclosure
**Anthropic.** Load metadata at startup, instructions on activation,
resources on reference. Minimise context cost.
**Applied:** prompt-engineering.md § Information architecture;
open-standards.md § Progressive disclosure.

### Agent Skills Standard
**Anthropic.** Filesystem-based packaging of procedural knowledge for
AI agent consumption.
**Applied:** open-standards.md (entire document).

### Grade Outputs, not Process
**Anthropic.** Evaluate what a component produced, not how it got there.
Partial credit where possible.
**Applied:** dev/conformance-testing.md § What conformance does not cover.

### Context Rot
**Anthropic / transformer architecture.** As context windows fill,
accuracy degrades. N tokens maintain N² attention relationships.
Countermeasures: progressive disclosure, compaction, bounded subagent
contexts.
**Applied:** prompt-engineering.md § Context management.

### Context Engineering
**Anthropic.** Optimise the full information environment, not just a
single prompt. Find the smallest set of high-signal tokens that maximise
the likelihood of the desired outcome.
**Applied:** prompt-engineering.md § Context management.

### Embedding Scaling Rules in Prompts
**Anthropic.** Agents cannot self-judge appropriate effort. Tell them
explicitly how much work a task warrants.
**Applied:** prompt-engineering.md § Context management.

### Description Field as API Contract
**Anthropic.** The SKILL.md description determines when the skill
activates. All triggering logic goes in the description, not the body.
**Applied:** prompt-engineering.md § Information architecture.

### External Artifacts as Cross-Session Memory
**Anthropic.** Decision logs, gate files, and engagement logs are the
agent's context reconstruction mechanism. Each session rebuilds from
artifacts, not conversation history.
**Applied:** semantic-waist.md § What the waist captures.

### Prompt Chaining Pattern
**Anthropic.** Sequential pipeline where each step's output feeds the
next. Gate artifacts are the data flowing between stages.
**Applied:** prompt-engineering.md § Operational patterns.

### Evaluator-Optimizer Pattern
**Anthropic.** One agent generates, another evaluates, loop until
quality threshold. Maps to propose-negotiate-agree with the human as
evaluator.
**Applied:** prompt-engineering.md § Operational patterns.

---

## Other / Cross-Cutting

### Semantic Bytecode
**Consultamatron.** A prompt is a program — a compressed encoding of
intent, context, and constraints that an LLM executes.
**Applied:** prompt-engineering.md § Semantic bytecode.

### Token Economics (3-Cost Model)
**Consultamatron.** Financial cost, attention cost, and displacement
cost compound in the context window.
**Applied:** prompt-engineering.md § Token economics.

### Design Double Diamond
**Design Council / Consultamatron.** Alternating diverge/converge
phases. The waist is the narrow point between phases.
**Applied:** semantic-waist.md § The design double diamond.

### Propose-Negotiate-Agree Loop
**Consultamatron.** Agent proposes, operator negotiates, gate artifact
written only on explicit agreement.
**Applied:** CLAUDE.md § Operator-in-the-loop;
engagement-protocol.md § 2.

### Gate Protocol (.agreed suffix)
**Consultamatron.** The `.agreed.md` / `.agreed.owm` suffix means the
operator has explicitly confirmed the artifact.
**Applied:** CLAUDE.md § Gates; semantic-waist.md § The design double
diamond.

### BYOT Contributor Model
**Consultamatron.** Burn Your Own Tokens — contributors develop
skillsets at their own expense and submit as pull requests.
**Applied:** dev/conformance-testing.md § The problem conformance solves.

### L0-L2 Progressive Compression
**Consultamatron.** L0 = human-readable prose, L1 = structured summary,
L2 = semantic bytecode. The waist captures L2; prose artifacts carry
L0/L1.
**Applied:** engagement-protocol.md § 9; prompt-engineering.md §
Semantic bytecode.

### Contributor Contract (Two-Sided)
**Consultamatron.** Skillset authors provide pipeline declarations and
testing helpers; the core guarantees discovery, progress tracking, and
conformance verification.
**Applied:** engagement-protocol.md § 11.

### Wetware Economics (3-Cost Model)
**Consultamatron.** Cognitive load, attention fatigue, and background
knowledge debt compound in the operator's cognitive budget — the
operator-side parallel to token economics.
**Applied:** wetware-efficiency.md § The cost model for wetware.

### Operator as Sensor / Actuator / Insight Generator
**Consultamatron.** The operator fills three irreplaceable roles in the
dyad: reading socio-economic signals (sensor), taking real-world action
(actuator), and synthesising judgment across information sources the
model cannot access (insight generator). All three improve with
understanding.
**Applied:** wetware-efficiency.md § Three roles in the dyad.

### Pedagogy as Compounding Investment
**Consultamatron.** The operator learns across engagements; the LLM does
not. Every unit of understanding built in the operator is a permanent
improvement to dyad capability. Teaching through the work — making
reasoning visible in proposals — is the mechanism.
**Applied:** wetware-efficiency.md § Pedagogy as compounding investment.

### Rubber-Stamp Failure Mode
**Consultamatron.** An operator who does not understand a proposal cannot
negotiate it, only accept or reject wholesale. This collapses the
propose-negotiate-agree quality gate to a single-agent system with human
latency.
**Applied:** wetware-efficiency.md § Comprehension enables negotiation.

### Background Knowledge Debt
**Consultamatron.** An operator lacking analytical vocabulary must spend
cognitive effort on translation before evaluation. This debt compounds
at every encounter. Paying it down — building fluency — reduces
per-interaction cost permanently.
**Applied:** wetware-efficiency.md § The cost model for wetware.

### Capability vs Dependency
**Consultamatron.** A system that produces output the operator does not
understand creates dependency. A system that produces output the operator
progressively understands creates capability. Capability building
improves the dyad's own performance by improving its collaborator.
**Applied:** wetware-efficiency.md § The long game.

### Graduation Gradient
**Consultamatron.** Calibrate pedagogical investment to the operator's
current fluency. New operators need reasoning chains and vocabulary
reinforcement. Experienced operators need conclusions and evidence.
Detect fluency from negotiation resolution.
**Applied:** wetware-efficiency.md § The long game.

### Skillset Capability
**Consultamatron.** One facet of the integration protocol — a port the
practice layer defines and the adapter contract a skillset satisfies.
Twelve capabilities decompose the integration surface by the Parnas
criterion (each hides one independently varying design decision).
**Applied:** integration-surface.md (entire document);
capabilities/index.md (the catalogue).

### Consultamatron Integration Protocol (CIP)
**Consultamatron.** The collection of all contracts at the
practice/skillset boundary. Each Skillset Capability is one facet of
the CIP. The protocol composes from independent facets rather than
being a monolithic interface.
**Applied:** integration-surface.md § The pattern;
context-mapping-the-integration-surface.md (DDD analysis of the CIP).

### Code Port / Language Port
**Consultamatron.** The two enforcement mechanisms for capabilities.
Code ports use Python Protocols (zero tokens, CI-enforced). Language
ports use filesystem conventions (token-burning verification, engineer-
triggered). The mechanism is determined by whether the contract is
evaluable by code alone.
**Applied:** integration-surface.md § Two mechanisms;
articles/language-port-testing.md (verification strategy for language
ports).

### Capability Maturity Model
**Consultamatron.** Three levels: nascent (documented, no enforcement),
established (structural tests, partial coverage), mature (full
structural tests, semantic verification defined). Each capability
progresses independently.
**Applied:** integration-surface.md § Maturity; capabilities/ pack
frontmatter (maturity field on each capability).
