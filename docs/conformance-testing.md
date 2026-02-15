# Conformance Testing

Why the test suite is the specification for bounded contexts, and how
that makes skillset contribution safe.

## Two halves of a contract

The practice library defines protocols — Python `Protocol` classes
that specify the type-level interface a bounded context must satisfy.
`EntityStore`, `ProjectPresenter`, `UseCase`. These are compile-time
contracts: does the code have the right shape?

Shape is necessary but not sufficient. A presenter with the right
method signature can still return garbage. A pipeline with the right
types can still have stages that don't chain. A usecase that accepts
the right request DTO can still violate the engagement lifecycle.

Conformance tests are the behavioral half of the contract. They verify
that a bounded context's declarations, entities, pipeline, and
presenter actually compose correctly with the rest of the practice.
The protocols say "you must have this shape." The conformance tests
say "and when we use it, this is what must happen."

Together, protocols and conformance tests are the complete
specification of what a bounded context must be.

## The problem conformance solves

The BYOT (Burn Your Own Tokens) model means community contributors
develop skillsets at their own expense and submit them as pull
requests. The practice maintainer cannot review every line of domain
logic in every contributed bounded context — nor should they need to.
A Wardley Mapping contributor understands map components better than
the maintainer does. A threat modelling contributor understands threat
actors better.

What the maintainer needs to know is: does this bounded context
compose? Will it break the engagement lifecycle? Will the `engage`
skill discover it correctly? Will pipeline progress tracking work?
Will the site renderer produce pages?

These questions are answerable by machine. The conformance test suite
answers them. If a contributed bounded context passes conformance,
it composes correctly with the practice regardless of what its
internal domain logic does. The blast radius of a badly-behaved
skillset is contained to that skillset — no cross-context Python
imports, interaction only through the CLI. See `docs/semantic-waist.md`
for why the CLI boundary provides this isolation.

Conformance testing is what makes unsupervised contribution a
controlled risk rather than an uncontrolled one.

## What conformance verifies

### Pipeline coherence

A skillset's pipeline is the spine of its engagement lifecycle. The
conformance suite verifies structural properties that must hold for
any pipeline, without executing usecases:

- Stages have monotonically increasing `order`
- Gates chain: `stage[n].produces_gate == stage[n+1].prerequisite_gate`
- Stage descriptions are unique within the pipeline
- `slug_pattern` contains `{n}`

These are cheap, fast, deterministic checks. They catch the class of
error where a contributor adds a stage but forgets to connect its
gate to the next stage's prerequisite.

### The decision-title join

This is the most fragile point in the engagement lifecycle.

`GetProjectProgressUseCase` matches recorded decision titles against
`PipelineStage.description` values to determine which stages are
complete. The join is a string equality check. If a skill's wrapper
script records a decision with title "Stage 3: Supply chain agreed"
but the pipeline stage description says "Stage 3: Supply chain
complete," the pipeline stalls silently — the decision exists but
progress doesn't advance.

The conformance suite makes this join explicit and tested. For each
pipeline stage, it records a decision with the stage's description
and verifies that progress advances. This runs per skillset, not
just for the skillsets the practice maintainer happened to test
manually.

### Entity round-trip fidelity

Every entity contributed by a bounded context must survive JSON
serialisation and deserialisation without data loss:

```
model_validate(entity.model_dump(mode="json")) == entity
```

This is a property that holds for all Pydantic models by default,
but custom validators, complex nested types, and enum serialisation
can break it. The conformance suite runs this for every entity type
in every bounded context, using entity builders that the bounded
context provides.

### Presenter contract

If a bounded context contributes a `ProjectPresenter`, the
conformance suite verifies that given a structurally valid synthetic
workspace, the presenter returns a `ProjectContribution` with
non-empty `slug`, `skillset`, and `status`. This catches the class
of error where a presenter works for the author's workspace but
breaks on edge cases (missing optional files, empty directories).

## What a bounded context must provide

The conformance suite discovers bounded contexts and imports their
declarations. Most conformance properties can be verified from the
standard declarations in `__init__.py` and entity types in
`entities.py`. But some properties require domain knowledge that
only the bounded context author has.

Each bounded context provides a `testing.py` module:

```
threat_modelling/
├── __init__.py          # DISPLAY_NAME, SLUG_PATTERN, PIPELINE, COMMANDS
├── entities.py          # ThreatModel, ThreatActor, Mitigation, ...
├── usecases.py          # business rules
├── testing.py           # entity builders, workspace/presenter factories
└── {skill}/
    ├── SKILL.md
    └── scripts/
```

`testing.py` furnishes:

- **Entity builders** — one factory function per entity type, with
  sensible defaults and keyword overrides. The pattern:

  ```python
  def make_threat_actor(**overrides) -> ThreatActor:
      defaults = dict(
          name="nation-state",
          capability="high",
          motivation="espionage",
      )
      return ThreatActor(**(defaults | overrides))
  ```

- **A presenter factory** — if the bounded context has a presenter,
  a function that returns one wired to a given workspace root.

- **A workspace builder** — a function that creates a minimal but
  structurally valid synthetic workspace on disk. The conformance
  suite calls this, then calls the presenter, and verifies the
  result.

The conformance suite imports `testing.py` from each discovered
bounded context. A contributor who provides it gets conformance
verification for free. A contributor who doesn't gets a clear error
naming the missing module.

## What conformance does not cover

Domain-specific business rules inside a bounded context are the
context's own concern. Whether a Wardley Map's chain-to-need
consistency holds, whether a BMC canvas has all nine blocks filled,
whether a threat model covers all identified threat actors — these
are internal invariants. The bounded context should test them in its
own test suite.

Conformance tests verify the *interface* between a bounded context
and the practice. They answer "does this compose?" not "is this
correct?" A bounded context can pass conformance and still produce
wrong answers. But it cannot pass conformance and break the
engagement lifecycle.

## Relationship to the semantic waist

The semantic waist (`docs/semantic-waist.md`) is the narrow data
layer — the CLI routes all bookkeeping through typed, validated
operations. Conformance testing is the narrow behavioral layer —
the test suite verifies all bounded contexts compose through typed,
validated contracts.

The waist ensures data integrity at runtime. Conformance ensures
structural integrity at development time. Both serve the same
purpose: make the contract between components explicit, cheap to
verify, and hard to violate silently.

## The `doctrine` marker

Conformance tests are selected by `pytest -m doctrine`. This is the
pre-push gate. A developer working on any bounded context runs
`pytest -m doctrine` before pushing, and gets a fast (under 5
seconds) answer to "have I broken any practice-wide contract?"

The name connects to two ideas: Wardley's doctrine (universal
principles that apply regardless of context) and clean architecture's
doctrinal compliance (structural rules that all components must
follow). Both senses apply — conformance tests verify principles
that hold for any bounded context regardless of its domain.

## Implementation

Issue #31 tracks the implementation of the conformance test suite.
