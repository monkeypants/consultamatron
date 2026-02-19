# Docstring Conventions

What information belongs in which docstring, and why.

## The principle

Each docstring serves a specific reader — the person looking at
that artifact right now. A DTO reader is a caller who needs to know
what the operation does. A usecase reader is a maintainer who needs
to understand the business rules. A protocol reader is an
implementor who needs to know what contract to satisfy.

Write for the reader who is actually there. If a docstring tries to
serve two audiences, at least one will lose — the information one
reader needs is noise to the other.

This follows the Information Expert principle: assign the
documentation responsibility to the artifact that has the
information the reader needs.

## Layer by layer

### Request DTOs — "What does this operation do?"

The request DTO is the interface between the usecase and whatever
consumes it (CLI, API, test harness, agent tool). Its docstring
describes the operation from the caller's perspective.

```python
class RegisterProjectRequest(BaseModel):
    """Register a new project, its decision log, and engagement entry.

    Creates the project in the registry, seeds a "Project created"
    decision, and logs an engagement entry.
    """

    client: str = Field(description="Client slug.")
    slug: str = Field(description="Project slug (e.g. maps-1).")
    skillset: str = Field(description="Skillset name (must match a manifest).")
    scope: str = Field(description="Project scope description.")
    notes: str = Field(default="", description="Additional notes.")
```

The class docstring is the operation summary. `Field(description=...)`
is the per-parameter help. Together, the DTO is a complete,
self-describing API contract. The CLI generator reads both to
produce `--help` text mechanically.

**Write for:** Someone constructing a request. They need to know
what the operation does and what each parameter means.

**Include:** What happens when you execute this request. What each
field means. Constraints the caller should know about (e.g. "slug
must be unique within the client").

**Omit:** Implementation details (which repositories are touched,
what coordination happens internally).

### Response DTOs — "What do I get back?"

Response DTOs are less prominent in `--help` output but serve as
documentation for callers who need to interpret the result.

```python
class RegisterProjectResponse(BaseModel):
    """Confirmation of project registration."""

    client: str
    slug: str
    skillset: str
```

**Write for:** Someone reading the response. A brief description
of what the response represents is sufficient. Field-level
descriptions are optional — add them when the meaning isn't obvious
from the field name.

### Usecases — "Why does this exist? What are the invariants?"

The usecase docstring serves developers maintaining the business
logic. It describes coordination, invariants, and the reasoning
behind the implementation.

```python
class RegisterProjectUseCase:
    """Coordinate project creation across three repositories.

    Validates the skillset exists and the slug is unique, then
    creates the project, seeds the decision log with a "Project
    created" entry using the scope as its field set, and records
    an engagement entry. All three writes must succeed together.
    """
```

This is different from the DTO docstring. The DTO says "register a
new project." The usecase says "coordinate across three repositories
with these invariants." Different readers, different needs.

**Write for:** Someone modifying the usecase or debugging a failure.
They need to understand the business rules, the sequence of
operations, and what must hold true.

**Include:** Which repositories are coordinated. Validation rules
and their order. Side effects (e.g. "seeds a decision log entry").
Why the usecase exists as a unit of work.

**Omit:** How to call the usecase (the DTO documents that). CLI
syntax or output formatting.

### Protocols — "What must an implementation guarantee?"

Protocol docstrings serve someone writing a new implementation: a
different storage backend, a test double, a caching decorator.

```python
class ProjectRepository(Protocol):
    """Persistence for project entities.

    Implementations must treat (client, slug) as a unique key.
    list_filtered returns projects matching all provided filters
    (AND semantics). None filters are ignored.
    """

    def save(self, project: Project) -> None: ...
    def get(self, client: str, slug: str) -> Project | None: ...
    def list_filtered(
        self, client: str, *, skillset: str | None, status: ProjectStatus | None
    ) -> list[Project]: ...
```

Method docstrings on protocols describe the contract —
preconditions, postconditions, and what return values mean (e.g.
"returns None if no project matches"). They do not describe how
the method works, because the protocol doesn't know that.

**Write for:** Someone implementing the protocol. They need to know
what the caller expects.

**Include:** Semantic contracts. What None means. How filters
compose. Uniqueness constraints. Thread safety requirements if any.

**Omit:** Implementation mechanisms (file format, SQL schema).
Those belong on the implementation class.

### Implementations — "How does this satisfy the contract?"

Implementation docstrings serve operators, debuggers, and
developers choosing between implementations.

```python
class JsonProjectRepository:
    """File-backed project storage using one JSON file per client.

    Projects are stored in {workspace}/clients/{client}/projects/index.md
    as a YAML-frontmatter document. File locking is not implemented;
    concurrent writes will corrupt.
    """
```

Method docstrings on implementations should document surprises, not
restate the protocol contract. If `save()` does exactly what the
protocol says, it doesn't need a docstring. If it creates parent
directories, uses atomic writes, or has performance characteristics
worth noting, document that.

**Write for:** Someone debugging a storage issue or evaluating
whether this implementation fits their needs.

**Include:** Storage format and location. Concurrency limitations.
Non-obvious side effects (directory creation, file locking).
Performance characteristics if relevant.

**Omit:** The semantic contract (that's on the protocol).

### Entities — "What does this concept mean?"

Entity docstrings serve developers understanding the domain model.

```python
class ProjectStatus(str, Enum):
    """Lifecycle stages of a consulting project.

    Transitions are strictly linear: planning -> elaboration ->
    implementation -> review -> closed. The next() method enforces
    this sequence.
    """
```

**Write for:** Someone learning the domain model. They need to
understand what the concept represents, what invariants it carries,
and how it relates to other entities.

**Include:** Domain meaning. Lifecycle rules. Invariants enforced
by the entity itself. Relationships to other entities where
non-obvious.

**Omit:** Persistence details (how it's stored). Application
details (how it's displayed).

### Framework / infrastructure — "How does the machinery work?"

Framework code (like the CLI command generator) serves developers
who need to use or extend the machinery.

```python
def generate_command(
    name: str,
    request_model: type[BaseModel],
    usecase_attr: str,
    format_output: Callable[[Any], None],
    help_text: str | None = None,
) -> click.Command:
    """Generate a Click command from a Pydantic request model.

    Inspects request_model.model_fields to produce --options.
    The generated command constructs the DTO, retrieves the
    usecase from the DI container via Click's context chain,
    executes, and delegates output formatting to the callback.
    """
```

**Write for:** Someone adding a new command or modifying the
generation machinery.

**Include:** What the function reads and what it produces. What
conventions the input must follow. What the caller is responsible
for (format callbacks, DI wiring).

**Omit:** Domain-specific details. The framework should know
nothing about projects, decisions, or tours.

## Summary

| Layer | Reader | Question it answers |
|---|---|---|
| Request DTO | Caller | What does this operation do? |
| Response DTO | Caller | What do I get back? |
| Usecase | Maintainer | Why does this exist? What are the invariants? |
| Protocol | Implementor | What must I guarantee? |
| Implementation | Operator | How does this work? What are the constraints? |
| Entity | Domain modeller | What does this concept mean? |
| Framework | Extender | How does the machinery work? |

## When not to write a docstring

A docstring that restates the obvious adds noise. If a method's
name, signature, and type hints fully communicate its purpose,
a docstring adds nothing:

```python
# No docstring needed — the name and types say everything.
def get(self, client: str, slug: str) -> Project | None: ...

# Docstring needed — the name doesn't explain the semantics.
def list_filtered(self, client: str, *, skillset: str | None,
                  status: ProjectStatus | None) -> list[Project]:
    """Return projects matching all non-None filters (AND semantics)."""
```

The test is: would someone reading just the signature misunderstand
what this does? If yes, add a docstring. If no, don't.
