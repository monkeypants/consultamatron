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
layer documents what its reader needs).

### Larman's Law 1: Power-Structure Inertia
**Larman.** Organisations are implicitly optimised to avoid changing
existing power structures.
**Applied:** conformance-testing.md § Why structural, not cultural.

### Larman's Law 2: Terminology Absorption
**Larman.** New terminology is adopted but behaviour remains unchanged.
**Applied:** conformance-testing.md § Why structural, not cultural.

### Larman's Law 3: Pragmatism Defence
**Larman.** The status quo is defended as the only pragmatic option.
**Applied:** conformance-testing.md § Why structural, not cultural.

### Larman's Law 4: Culture Follows Structure
**Larman.** Culture and behaviour follow organisational structure; to
change behaviour, change the structure.
**Applied:** engagement-protocol.md § 6 (structural enforcement over
documentation).

### Feature Teams over Component Teams
**Larman (LeSS).** Each contributor owns the full vertical slice rather
than one horizontal layer. No architecture review board.
**Applied:** conformance-testing.md § Why structural, not cultural.

### Community of Practice over Review Board
**Larman.** Quality patterns shared through example and documentation,
not committee approval.
**Applied:** conformance-testing.md § Why structural, not cultural.

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
**Applied:** engagement-protocol.md § 5 (GateInspector has one method).

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
**Applied:** engagement-protocol.md § 11 (skillsets as plugins).

### Acyclic Dependencies Principle
**Uncle Bob.** No cycles in the package dependency graph.
**Applied:** conformance-testing.md § Component coupling principles
(cross-BC import test).

### Stable Dependencies Principle
**Uncle Bob.** Depend in the direction of stability. Volatile packages
depend on stable packages, never the reverse.
**Applied:** conformance-testing.md § Component coupling principles
(`practice` is stable; BCs depend on it).

### Stable Abstractions Principle
**Uncle Bob.** A component should be as abstract as it is stable.
Concrete implementations belong in volatile packages.
**Applied:** conformance-testing.md § Component coupling principles
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
`engage` skill as executable context map).

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
**Applied:** conformance-testing.md § What conformance does not cover.

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
**Applied:** conformance-testing.md § The problem conformance solves.

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
