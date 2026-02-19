# The Engagement Protocol

Why the engagement lifecycle cannot be a skillset pipeline, and how to
replace it with a use case layer that derives state from gate artifacts.

## 1. The antipattern: engagement as skillset

The consulting bounded context models the entire engagement lifecycle as
a three-stage pipeline:

```
org-research → engage → review
```

This makes it structurally identical to a Wardley Mapping or BMC pipeline.
But the engagement lifecycle is not a pipeline. It is the *host* of
pipelines. An engagement contains multiple projects, each driven through
its own skillset pipeline. The engagement protocol's job is to
orchestrate those projects — track which are complete, which are blocked,
and what should happen next.

Modelling this as a pipeline creates a category error with three
observable consequences:

**No cross-project visibility.** The `project progress` command shows
per-project pipeline position, but nothing aggregates across projects
within an engagement. The operator must manually query each project and
mentally reconstruct the overall state. This is the question that goes
unanswered: "where am I?"

**No sequencing advice.** Given an engagement with several projects at
various stages, the system cannot recommend what to do next. The
operator carries the execution plan in memory. When context is lost
between sessions, so is the plan. This is the second unanswered question:
"what should I do?"

**Structural conflation.** org-research and review are standalone
activities — they do not belong to a specific project, they bracket the
engagement as a whole. Encoding them as pipeline stages of a "consulting"
skillset gives them the wrong identity. They are engagement protocol
actions, not project pipeline stages. The consulting "pipeline" does not
chain through gates the way real pipelines do — `resources/index.md` is
produced by research, consumed by every project, and is not a gate in the
pipeline sense.

The result is an engagement lifecycle that exists in documentation
(CLAUDE.md's "check client workspace, read engagement log, execute
projects through pipelines, run review") but has no structural mechanism
behind it. The system depends on the operator and agent remembering the
protocol, not on the protocol enforcing itself.

## 2. The three protocols

Consultamatron operates at three nested protocol levels. Understanding
their separation clarifies what belongs where.

### The engagement protocol (outer loop)

Orchestrates the engagement lifecycle: create engagements, configure
source access, register projects, track cross-project progress, recommend
next actions, and trigger review when all projects complete. This is the
use case layer that currently does not exist as an execution model.

### The skillset protocol (middle loop)

Drives individual projects through their pipeline stages. This is what
`PipelineStage` and `GetProjectProgressUseCase` already implement.
Each stage has a prerequisite gate, a skill to execute, and a gate it
produces. Progress is tracked via the decision-title join
(see `docs/conformance-testing.md`).

### The skills engineering protocol (inner loop)

The propose-negotiate-agree loop between agent and operator within a
single skill execution. This is documented in CLAUDE.md and enforced by
skill design conventions.

The antipattern collapses the outer and middle loops into a single
pipeline. The fix is to separate them: the engagement protocol becomes
a use case layer; the skillset protocol remains as-is; the skills
engineering protocol is untouched.

### The engagement execution use case (Cockburn fully dressed)

Cockburn's fully dressed use case format makes the engagement protocol's
real design visible. The happy path is trivial — the extensions are where
the architecture lives.

**Preconditions:** Client workspace exists. At least one engagement with
registered projects.

**Trigger:** Operator asks "where am I?" or "what should I do?"

**Main success scenario:**
1. System derives pipeline position for all projects (gate inspection)
2. System identifies the earliest incomplete project
3. System verifies the prerequisite gate exists
4. System recommends the next skill to execute
5. Agent executes the skill through the propose-negotiate-agree loop
6. Skill produces a gate artifact on operator agreement
7. Repeat from step 1

**Extensions:**
- *1a. Gate inspection fails (filesystem error):* Report the error and
  the affected project. Do not guess state.
- *3a. Prerequisite gate missing:* Report the project as blocked. Name
  the missing gate and which earlier skill produces it.
- *5a. Operator negotiates (disagrees with proposal):* Agent revises.
  Loop until agreement or operator abandons.
- *5b. Operator abandons skill execution:* No gate artifact written.
  Pipeline position unchanged. System can recommend the same skill
  next time.
- *6a. Gate artifact already exists (re-execution):* Do not overwrite.
  Report that the gate exists and the stage is already complete.
- *7a. All terminal gates exist:* Recommend "run review."

"Extensions are where the real design lives" — the negotiate loop (5a),
the gate immutability invariant (6a), and the blocked-project detection
(3a) are the architecturally significant paths.

## 3. Clean Architecture applied

Uncle Bob's Clean Architecture provides the structural vocabulary for
this separation.

### The dependency rule

Dependencies point inward. The engagement protocol (use case layer)
depends on domain entities. Infrastructure (filesystem gate checking,
CLI rendering) depends on the use case layer. Neither the use cases nor
the entities know about the CLI, the filesystem, or any specific
bounded context.

```
┌─────────────────────────────────────────────────────────┐
│  CLI / Infrastructure                                    │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Use Cases (engagement protocol)                   │  │
│  │  ┌─────────────────────────────────────────────┐  │  │
│  │  │  Entities (domain objects, value objects)     │  │  │
│  │  └─────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

This is the existing pattern (`src/practice/` → entities and protocols;
`commons/*/usecases.py` → use cases; `bin/cli/` → infrastructure).
The engagement protocol follows the same structure.

### Use cases as table of contents

Uncle Bob describes use cases as the screaming architecture — looking
at the use case directory should tell you what the system does. The
current use case list (InitializeWorkspace, RegisterProject,
RecordDecision, GetProjectProgress, ...) tells you the system does
bookkeeping. It does not tell you the system orchestrates engagements.

Adding `GetEngagementStatusUseCase` and `GetNextActionUseCase` makes
the engagement protocol visible in the architecture. The system now
screams "I track engagement status and recommend next actions" in
addition to "I do bookkeeping."

### LLM as framework detail

The LLM belongs in the outermost ring. Core logic — what constitutes a
valid engagement, what gates a pipeline must produce, how pipeline
progress is derived — must not depend on which LLM executes the skill.
If you swapped Claude for GPT, no entity, use case, or protocol should
change. The entities define the domain. The use cases define the rules.
The LLM is an infrastructure detail that executes skill instructions,
no different architecturally from the filesystem that stores gate
artifacts.

This is the dependency rule applied to the most exotic dependency in
the system. The temptation is to treat the LLM as special — to embed
model-specific assumptions in business logic. The Clean Architecture
response is to treat it as what it is: an adapter behind a port.

### Screaming architecture

The bounded context directories should tell you what the system is about.
`commons/consulting/` screams "consulting lifecycle." When the engagement
protocol use cases live there alongside the existing bookkeeping use
cases, the architecture declares its purpose.

## 4. Hexagonal Architecture applied

Cockburn's Hexagonal Architecture (ports and adapters) provides the
structural pattern for the engagement protocol's dependencies.

### The operator as a port

The engagement protocol has one driver port: the operator (via CLI).
The operator asks "where am I?" (status) and "what should I do?" (next).
These are the two commands the protocol exposes.

### Driver and driven ports

**Driver port:** The CLI commands (`practice engagement status`,
`practice engagement next`) invoke use cases. This is the left side
of the hexagon — the primary actors.

**Driven ports:** The use cases need to inspect gate artifacts to
determine pipeline progress. But the use case should not know that gates
are files on disk. They might be database rows, API responses, or test
fixtures. The `GateInspector` protocol is the driven port:

```python
class GateInspector(Protocol):
    def exists(self, client: str, engagement: str,
               project: str, gate_path: str) -> bool: ...
```

The filesystem implementation (`FilesystemGateInspector`) checks whether
a file exists at the expected path. Test implementations return
predetermined answers. The use case is oblivious to the distinction.

This is the right side of the hexagon — secondary actors that the
application drives through ports.

### The walking skeleton

Cockburn advocates building a walking skeleton first: the thinnest
possible end-to-end slice that proves the architecture works. For the
engagement protocol, the walking skeleton is `practice engagement status`:

1. CLI parses `--client X --engagement Y`
2. Use case reads engagement, projects, pipeline definitions
3. Use case calls `GateInspector` for each gate
4. Use case returns `EngagementDashboard`
5. CLI formats and prints

This single command exercises the driver port, the use case, the driven
port, and the infrastructure adapter. If it works, the architecture
works. Everything else is additional use cases and richer output.

## 5. GRASP and SOLID applied

### Protected Variations (Larman)

The `GateInspector` protocol protects the engagement status use case
from variations in how gate artifacts are stored. Today, gates are files.
Tomorrow, they might be entries in a manifest. The use case is stable
across this variation because the protocol absorbs it.

This is the same pattern used throughout the practice library:
`SkillsetRepository`, `ProjectPresenter`, `SiteRenderer` — all
protocol-based ports that protect use cases from infrastructure
variation.

### Low Coupling (Larman)

The engagement protocol use cases depend only on:
- Domain entities (`Engagement`, `Project`, `Skillset`, `PipelineStage`)
- Repository protocols (`EngagementRepository`, `ProjectRepository`,
  `SkillsetRepository`)
- The `GateInspector` protocol

They do not depend on the filesystem, the CLI framework, or any specific
bounded context's internals. A change to how wardley-mapping stores its
gate artifacts does not affect the engagement protocol.

### Interface Segregation Principle (Uncle Bob)

`GateInspector` has exactly one method: `exists()`. It does not also
read gate content, validate gate format, or list all gates. The
engagement protocol needs to know if a gate exists — nothing more.
The interface is as narrow as the need.

### Dependency Inversion Principle (Uncle Bob)

High-level modules (engagement protocol use cases) do not depend on
low-level modules (filesystem operations). Both depend on abstractions
(the `GateInspector` protocol). This is the dependency rule expressed as
a SOLID principle.

## 6. Structural enforcement

### Larman's Law 4: culture follows structure

Documenting the engagement protocol in CLAUDE.md is necessary but
insufficient. The protocol works when the operator and agent follow the
instructions. It fails when they don't — and there is no mechanism to
detect the failure.

This is Law 4 in action: telling people to follow a process works until
it doesn't. The fix is structural enforcement — make the correct path
the only path, or at minimum make the incorrect path detectable.

### Doctrine tests as definition of done

The conformance test suite (see `docs/conformance-testing.md`) is the
structural enforcement mechanism for bounded context composition. The
engagement protocol extends this: new doctrine tests verify that
engagement use cases compose correctly with gate artifacts and pipeline
definitions.

The `pytest -m doctrine` gate already runs before every push. Adding
engagement protocol conformance properties to this gate makes the
protocol structurally enforced. If the gate artifacts don't exist where
the protocol expects them, the doctrine tests catch it.

### Cross-BC import test

Uncle Bob's dependency rule says no bounded context may import from
another. This is currently a cultural rule — developers know not to do
it. Adding a doctrine test that scans all BC Python files for cross-BC
imports makes it structural. A violation fails CI, not code review.

This is Law 4 applied to the dependency rule: don't document that
imports must not cross BC boundaries. Verify it.

### Crystal methodology tuning

Cockburn's Crystal methodology family classifies projects by
criticality × size and prescribes different process weights for each
classification. A quick strategic sketch (Comfort level — loss of
comfort on failure) needs fewer pipeline stages, lighter gate evidence,
and less formal review than a full digital transformation (Essential
Money level — significant financial loss on failure).

Consultamatron currently treats all engagements with equal process
weight. Future direction: formal engagement classification at the
`engage` skill, driving skill selection and gate evidence requirements.
A Comfort-level engagement might skip atlas generation and use
abbreviated gates. An Essential Money-level engagement might require
cross-validated research, multi-perspective tours, and formal review
sign-off.

### Heart of Agile mapping

Cockburn's Heart of Agile distills agility to four verbs: Collaborate,
Deliver, Reflect, Improve. All four are structurally present in
Consultamatron:

- **Collaborate** = the propose-negotiate-agree loop. Every skill
  execution is a structured collaboration between agent and operator.
- **Deliver** = gate artifacts. Each agreed gate is a delivered
  increment of consulting value.
- **Reflect** = the engagement log and the `review` skill. The
  engagement log is a running audit trail; the review skill produces
  a structured retrospective.
- **Improve** = the skillset engineering pipeline (`rs-assess`,
  `rs-plan`, `rs-iterate`). The practice improves its own tools
  through the same structured pipeline approach it uses for client
  work.

## 7. Consumer-driven contracts for gates

### Fowler's consumer-driven contracts

A gate artifact is a contract between the skill that produces it and the
skill that consumes it. Currently, this contract is implicit — the
consumer reads the file and hopes it contains what it needs. If the
producer changes the file format, the consumer breaks silently.

Consumer-driven contracts (Fowler) invert this: the consumer declares
what it needs from the gate, and the producer is obligated to satisfy
those declarations. In Consultamatron, this means each pipeline stage
declares what sections or fields it reads from its prerequisite gate.

### The Tolerant Reader

Fowler's Tolerant Reader pattern complements CDC: consumers should
depend on as little of the gate as possible. A stage that needs only
the "components" section of a supply chain document should not break
if the "methodology" section changes.

The `consumes` field on `PipelineStage` enables this. Each stage
declares the minimum set of sections or fields it reads from the
prerequisite gate. This makes the contract explicit, testable, and
narrow.

```python
class PipelineStage(BaseModel):
    order: int
    skill: str
    prerequisite_gate: str
    produces_gate: str
    description: str
    consumes: list[str] = []  # what this stage reads from prerequisite
```

A doctrine test verifies that every stage with a prerequisite gate
declares at least one `consumes` entry. This catches the class of error
where a contributor adds a stage but does not document its contract with
the previous stage.

## 8. The narrow semantic waist extended

The semantic waist (see `docs/semantic-waist.md`) captures lifecycle
data — that projects exist, that decisions were made, that stages
completed. The engagement protocol extends this waist to capture
*engagement-level* state.

### State derivation, not state storage

The engagement protocol does not store engagement state in a new
database. It derives state from existing artifacts:

- **Pipeline position** is derived from gate artifact existence. If
  `evolve/map.agreed.owm` exists, the evolve stage is complete. No
  decision log query needed — the file *is* the proof.
- **Engagement status** is the aggregate of all project positions.
  If all terminal gates exist, the engagement is complete.
- **Next action** follows from the sequencing rules applied to the
  derived positions.

This is the waist principle applied to the outer loop: concentrate
the diffuse state (which files exist across multiple project directories)
into structured data (the `EngagementDashboard` value object) through
a deterministic, zero-token operation.

### Value objects, not entities

The engagement protocol's domain objects are value objects, not entities.
`ProjectPipelinePosition`, `EngagementDashboard`, and `NextAction` are
computed on demand from existing data — they have no identity, no
lifecycle, no persistence. They are the crystallised output of a state
derivation, useful for rendering and decision-making, discarded after
use.

This is deliberate. Adding persistent engagement state would create a
second source of truth that could drift from the gate artifacts. The
gate files are the canonical state. The value objects are views over
that state.

## 9. Semantic bytecode in skills

### Freedom levels for skills

The prompt engineering framework (see `docs/prompt-engineering.md`)
describes the inbound/outbound directional model. The engagement
protocol adds a calibration dimension: how much freedom should the
agent have when executing a skill?

Each skill declares a `freedom` level in its SKILL.md frontmatter:

- **high** — The agent has broad latitude. Research skills, creative
  synthesis, narrative generation. The skill provides goals and
  constraints but does not micromanage the approach.
- **medium** — The agent has structured latitude. Analysis skills
  where the methodology is defined but interpretation is required.
  The skill provides a framework and the agent fills it.
- **low** — The agent follows a precise procedure. Recording skills,
  gate production, structural output. The skill provides step-by-step
  instructions and the agent executes them.

This is Anthropic's skills engineering insight applied to consulting:
calibrate the prompt engineering style to the task fragility. A research
skill benefits from agent creativity; a gate-writing skill needs agent
precision.

### L0-L2 for work products and skill assets

The semantic bytecode concept applies at two levels:

**Work products** (gate artifacts, research documents, analysis outputs)
use progressive compression: human-readable prose at L0, structured
summaries at L1, semantic bytecode at L2. The waist captures L2 data;
the prose artifacts carry L0 and L1.

**Skill assets** (SKILL.md files, methodology references) are already
engineered as semantic bytecode for inbound consumption. The freedom
level determines how tightly the bytecode constrains the agent's
execution.

## 10. The walking skeleton

Cockburn's walking skeleton is not a prototype — it is the first
increment that proves the architecture works end-to-end. For the
engagement protocol, the skeleton has two commands:

### `practice engagement status`

Given a client and engagement, derive the position of every project
in the engagement:

```
$ practice engagement status --client holloway --engagement strat-1
holloway / strat-1 (active)

  maps-1 (wardley-mapping): stage 4/5 (evolve)
    [x] Stage 1: Project brief agreed
    [x] Stage 2: User needs agreed
    [x] Stage 3: Supply chain agreed
    [x] Stage 4: Evolution map agreed
    [ ] Stage 5: Strategy map agreed

  canvas-1 (business-model-canvas): stage 2/3 (bmc-segments)
    [x] Stage 1: Project brief agreed
    [ ] Stage 2: Customer segments agreed
    [ ] Stage 3: Business Model Canvas agreed
```

This exercises the full vertical slice: CLI → use case →
GateInspector → filesystem.

### `practice engagement next`

Given a client and engagement, apply sequencing rules and recommend
the next action:

```
$ practice engagement next --client holloway --engagement strat-1
Next: run wm-strategy for maps-1
  Reason: prerequisite evolve/map.agreed.owm exists
```

The sequencing rules are simple and deterministic:
1. Find projects with incomplete pipelines, ordered by creation date
2. For the earliest incomplete project, find the first stage whose
   gate does not exist
3. Check the prerequisite gate exists; if not, the project is blocked
4. Return the skill name, project slug, and reason

When all terminal gates exist: "All projects complete — run review."
When a prerequisite is missing: "Blocked: prerequisite missing for
[project]."

## 11. How a skillset plugs in

The engagement protocol treats skillsets as plugins. A skillset author
does not need to understand the engagement protocol to contribute a
skillset. The protocol discovers and drives skillsets through their
declared pipelines.

### The contributor contract

A skillset provides:
1. `SKILLSETS` list in `__init__.py` with pipeline stages
2. Each stage declares `prerequisite_gate` and `produces_gate`
3. Each stage declares `consumes` (what it reads from the prerequisite)
4. Skills follow the propose-negotiate-agree loop
5. Skills produce gate artifacts at the expected paths

### What the core guarantees

The engagement protocol guarantees:
1. `practice engagement status` shows the project's position
2. `practice engagement next` recommends the correct next skill
3. Gate existence checks are delegated through `GateInspector`
4. Cross-project sequencing respects creation order
5. Conformance tests verify pipeline composition

A skillset author runs `pytest -m doctrine` and gets immediate feedback
on whether their pipeline composes with the engagement protocol. The
protocol is invisible to the skillset — it reads gate artifacts and
pipeline definitions, never calling into skillset code.

This is the plugin architecture that Clean Architecture and Hexagonal
Architecture converge on: the core defines ports, plugins satisfy them,
and the core drives the plugins without depending on them.

### Orchestration within, choreography across

The engagement layer explicitly plans and sequences project execution —
this is orchestration. The `engagement next` command applies deterministic
rules to recommend the next skill. The engagement plan records which
projects exist and in what order they were created.

Cross-project references are suggestions, not dependencies — this is
choreography. The `engage` skill may say "a Wardley Map could inform BMC
Key Resources," but this does not create a hard gate dependency. The BMC
project can proceed without the Wardley Map. Cross-project insights flow
through the shared research kernel (`resources/`), not through gate
artifact dependencies.

This distinction matters for execution flexibility. Orchestration within
an engagement ensures each project progresses through its own pipeline
correctly. Choreography across projects means the engagement is not
blocked by artificial cross-project dependencies — the operator decides
when and whether to incorporate cross-project insights.

### What gets removed

The consulting skillset pipeline (org-research → engage → review) is
deleted. It was modelling the engagement protocol as a pipeline — the
antipattern this article describes. org-research and review remain as
standalone skills, invocable via slash commands but no longer gated
pipeline stages.

Profiles (named collections of skillsets) are also removed. They were
a decorative grouping mechanism with no behavioral significance — the
engagement already controls which skillsets are available through its
source allowlist.

The result is a structurally simpler system: skillsets have pipelines,
engagements orchestrate skillsets, and nothing pretends to be something
it is not.
