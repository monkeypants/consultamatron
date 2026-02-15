# CLI Command Generation

How `generate_command()` translates Pydantic request DTOs into Click
commands, and how to add new commands.

## How it works

`bin/cli/introspect.py` inspects `request_model.model_fields` and
produces a `click.Command` with options derived from field metadata.
The generated callback constructs the DTO, retrieves the usecase from
the DI container, executes it, and delegates output to a format
callback.

Every CLI command uses this mechanism. There are no hand-written Click
option decorators.

## Adding a new command

### 1. Define the request and response DTOs

In `bin/cli/dtos.py` (or in your bounded context's DTO module):

```python
class DoThingRequest(BaseModel):
    """Do the thing for a client."""

    client: str = Field(description="Client slug.")
    name: str = Field(description="Thing name.")

class DoThingResponse(BaseModel):
    client: str
    name: str
```

The class docstring becomes the command's `--help` text.
Every field needs `Field(description=...)` — the description becomes
the `--help` text for that option.

See `docs/docstring-conventions.md` for what belongs in each layer's
docstring.

### 2. Write the usecase

In your usecases module, implement the `UseCase` protocol:

```python
class DoThingUseCase:
    """Coordinate the thing across repositories.

    Validates preconditions, then writes to projects and decisions.
    """

    def __init__(self, projects: ProjectRepository) -> None:
        self._projects = projects

    def execute(self, request: DoThingRequest) -> DoThingResponse:
        ...
```

The usecase docstring describes invariants, coordination, and
validation for maintainers — not the operation summary (that's on
the DTO).

### 3. Wire into the DI container

In `bin/cli/di.py`, add the usecase as an attribute on `Container`.

### 4. Register the command

In `bin/cli/main.py` (or your bounded context's CLI module):

```python
def _format_do_thing(resp: Any) -> None:
    click.echo(f"Did '{resp.name}' for '{resp.client}'")

some_group.add_command(
    generate_command(
        name="do-thing",
        request_model=DoThingRequest,
        usecase_attr="do_thing_usecase",
        format_output=_format_do_thing,
    )
)
```

### 5. Write parity tests

In `tests/test_cli.py`, test through the CLI runner:
- Happy path (exit code 0, expected output)
- Missing required option (exit code != 0)
- Error path if applicable (exit code 1, error message)
- Default values for optional fields

## Field type conventions

### Simple string (required)

```python
name: str = Field(description="The name.")
```

Produces `--name VALUE [required]`.

### Simple string (optional with default)

```python
notes: str = Field(default="", description="Additional notes.")
```

Produces `--notes VALUE` (optional, defaults to empty string).

### Optional (None default)

```python
skillset: str | None = Field(default=None, description="Filter by skillset.")
```

Produces `--skillset VALUE` (optional, defaults to None).

### Enum choices

```python
status: str = Field(
    description="New status.",
    json_schema_extra={"choices": ProjectStatus},
)
```

Produces `--status {planning,elaboration,...}`. The enum class is
passed in `json_schema_extra["choices"]`; the generator extracts
member values and builds a `click.Choice`. The field type stays `str`
— the usecase is responsible for converting to the enum.

A list or tuple of strings also works:

```python
json_schema_extra={"choices": ["a", "b", "c"]}
```

### CLI name override

```python
project_slug: str = Field(
    description="Project slug.",
    json_schema_extra={"cli_name": "project"},
)
```

Produces `--project VALUE` instead of `--project-slug VALUE`. The
generator remaps the Click parameter name back to the DTO field name
in the callback. Use this when the CLI convention differs from the
domain model name.

### Repeatable key-value pairs (dict)

```python
fields: dict[str, str] = Field(
    default_factory=dict,
    description="Key=Value pair (repeatable).",
    json_schema_extra={"cli_name": "field"},
)
```

Produces `--field K=V` (repeatable). Each invocation of `--field`
adds one entry. The generator detects `dict[str, str]` annotation,
sets `multiple=True`, and parses `Key=Value` strings. Omitting the
option produces an empty dict.

### JSON list of models

```python
stops: list[TourStop] = Field(description="JSON array of tour stops.")
```

Produces `--stops '<json string>'`. The generator detects
`list[SomeBaseModel]`, accepts a JSON string, parses it, and
validates each item against the model class.

## What the generator does NOT handle

- **Positional arguments.** All fields become `--options`.
- **File/path types.** Fields are treated as strings.
- **Nested non-list complex types.** Only `dict[str, str]` and
  `list[BaseModel]` have special handling.
- **Response formatting.** Each command has a manual format callback.
  Output formatting is where human judgement matters — the generator
  doesn't attempt it.
