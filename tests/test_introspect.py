"""Tests for CLI command generation from DTO introspection.

Verifies that generate_command() correctly translates Pydantic
model metadata into Click commands — required/optional options,
defaults, enum choices, help text, and error handling.

These tests exercise the introspection machinery in isolation,
independent of which specific commands have been converted.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

import click
from click.testing import CliRunner
from pydantic import BaseModel, Field

from bin.cli.exceptions import DomainError
from bin.cli.introspect import generate_command

import json


# ---------------------------------------------------------------------------
# Test models — small, purpose-built, not domain entities
# ---------------------------------------------------------------------------


class Color(str, Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"


class AllRequiredRequest(BaseModel):
    name: str = Field(description="The name.")
    value: str = Field(description="The value.")


class WithOptionalRequest(BaseModel):
    name: str = Field(description="The name.")
    color: str | None = Field(
        default=None,
        description="Optional color.",
        json_schema_extra={"choices": Color},
    )
    notes: str = Field(default="", description="Optional notes.")


class SimpleResponse(BaseModel):
    result: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class FakeUseCase:
    """Minimal usecase stub that records calls."""

    def __init__(self, response=None, error=None):
        self.response = response or SimpleResponse(result="ok")
        self.error = error
        self.last_request = None

    def execute(self, request: Any) -> Any:
        self.last_request = request
        if self.error:
            raise self.error
        return self.response


def _build_cli(
    usecase: FakeUseCase,
    request_model: type[BaseModel],
    help_text: str | None = None,
) -> click.Group:
    """Build a Click group with a generated command wired to a fake."""

    class FakeContainer:
        test_usecase = usecase

    def format_output(resp: Any) -> None:
        click.echo(f"result={resp.result}")

    @click.group()
    @click.pass_context
    def cli(ctx: click.Context) -> None:
        ctx.obj = FakeContainer()

    cli.add_command(
        generate_command(
            name="cmd",
            request_model=request_model,
            usecase_attr="test_usecase",
            format_output=format_output,
            help_text=help_text,
        )
    )
    return cli


def _run(cli: click.Group, args: list[str]) -> click.testing.Result:
    return CliRunner().invoke(cli, ["cmd"] + args)


# ---------------------------------------------------------------------------
# Required vs optional
# ---------------------------------------------------------------------------


class TestRequiredOptions:
    def test_all_required_present_succeeds(self):
        uc = FakeUseCase()
        cli = _build_cli(uc, AllRequiredRequest)
        result = _run(cli, ["--name", "foo", "--value", "bar"])
        assert result.exit_code == 0
        assert "result=ok" in result.output

    def test_missing_required_rejected(self):
        uc = FakeUseCase()
        cli = _build_cli(uc, AllRequiredRequest)
        result = _run(cli, ["--name", "foo"])
        assert result.exit_code != 0
        assert uc.last_request is None

    def test_request_receives_correct_values(self):
        uc = FakeUseCase()
        cli = _build_cli(uc, AllRequiredRequest)
        _run(cli, ["--name", "hello", "--value", "world"])
        assert uc.last_request.name == "hello"
        assert uc.last_request.value == "world"


class TestOptionalDefaults:
    def test_none_default_applied(self):
        uc = FakeUseCase()
        cli = _build_cli(uc, WithOptionalRequest)
        _run(cli, ["--name", "foo"])
        assert uc.last_request.color is None

    def test_empty_string_default_applied(self):
        uc = FakeUseCase()
        cli = _build_cli(uc, WithOptionalRequest)
        _run(cli, ["--name", "foo"])
        assert uc.last_request.notes == ""

    def test_optional_can_be_provided(self):
        uc = FakeUseCase()
        cli = _build_cli(uc, WithOptionalRequest)
        _run(cli, ["--name", "foo", "--notes", "important"])
        assert uc.last_request.notes == "important"


# ---------------------------------------------------------------------------
# Enum choices via json_schema_extra
# ---------------------------------------------------------------------------


class TestEnumChoices:
    def test_valid_value_accepted(self):
        uc = FakeUseCase()
        cli = _build_cli(uc, WithOptionalRequest)
        result = _run(cli, ["--name", "foo", "--color", "red"])
        assert result.exit_code == 0
        assert uc.last_request.color == "red"

    def test_invalid_value_rejected_before_usecase(self):
        uc = FakeUseCase()
        cli = _build_cli(uc, WithOptionalRequest)
        result = _run(cli, ["--name", "foo", "--color", "purple"])
        assert result.exit_code != 0
        assert uc.last_request is None

    def test_all_enum_members_accepted(self):
        uc = FakeUseCase()
        cli = _build_cli(uc, WithOptionalRequest)
        for color in Color:
            result = _run(cli, ["--name", "x", "--color", color.value])
            assert result.exit_code == 0, f"Rejected valid color: {color.value}"


# ---------------------------------------------------------------------------
# Help text
# ---------------------------------------------------------------------------


class TestHelpText:
    def test_command_help_from_argument(self):
        uc = FakeUseCase()
        cli = _build_cli(uc, AllRequiredRequest, help_text="Do the thing.")
        result = CliRunner().invoke(cli, ["cmd", "--help"])
        assert "Do the thing." in result.output

    def test_field_descriptions_in_help(self):
        uc = FakeUseCase()
        cli = _build_cli(uc, AllRequiredRequest)
        result = CliRunner().invoke(cli, ["cmd", "--help"])
        assert "The name." in result.output
        assert "The value." in result.output

    def test_required_fields_shown_as_required(self):
        uc = FakeUseCase()
        cli = _build_cli(uc, AllRequiredRequest)
        result = CliRunner().invoke(cli, ["cmd", "--help"])
        assert "[required]" in result.output


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


class TestErrorHandling:
    def test_domain_error_becomes_exit_code_1(self):
        uc = FakeUseCase(error=DomainError("Workspace already exists"))
        cli = _build_cli(uc, AllRequiredRequest)
        result = _run(cli, ["--name", "foo", "--value", "bar"])
        assert result.exit_code == 1
        assert "Workspace already exists" in result.output

    def test_not_found_error_surfaces(self):
        from bin.cli.exceptions import NotFoundError

        uc = FakeUseCase(error=NotFoundError("Project not found: x/y"))
        cli = _build_cli(uc, AllRequiredRequest)
        result = _run(cli, ["--name", "foo", "--value", "bar"])
        assert result.exit_code == 1
        assert "Project not found: x/y" in result.output


# ---------------------------------------------------------------------------
# Option naming
# ---------------------------------------------------------------------------


class TestOptionNaming:
    """Underscores in field names become hyphens in CLI options."""

    def test_underscore_becomes_hyphen(self):
        class UnderscoreRequest(BaseModel):
            project_slug: str = Field(description="The slug.")

        uc = FakeUseCase()
        cli = _build_cli(uc, UnderscoreRequest)
        result = _run(cli, ["--project-slug", "maps-1"])
        assert result.exit_code == 0
        assert uc.last_request.project_slug == "maps-1"

    def test_cli_name_overrides_option(self):
        class AliasedRequest(BaseModel):
            project_slug: str = Field(
                description="The slug.",
                json_schema_extra={"cli_name": "project"},
            )

        uc = FakeUseCase()
        cli = _build_cli(uc, AliasedRequest)
        result = _run(cli, ["--project", "maps-1"])
        assert result.exit_code == 0
        assert uc.last_request.project_slug == "maps-1"

    def test_cli_name_original_option_rejected(self):
        class AliasedRequest(BaseModel):
            project_slug: str = Field(
                description="The slug.",
                json_schema_extra={"cli_name": "project"},
            )

        uc = FakeUseCase()
        cli = _build_cli(uc, AliasedRequest)
        result = _run(cli, ["--project-slug", "maps-1"])
        assert result.exit_code != 0
        assert uc.last_request is None


# ---------------------------------------------------------------------------
# Dict fields (repeatable Key=Value options)
# ---------------------------------------------------------------------------


class DictFieldRequest(BaseModel):
    name: str = Field(description="Name.")
    tags: dict[str, str] = Field(
        default_factory=dict,
        description="Key=Value tags.",
        json_schema_extra={"cli_name": "tag"},
    )


class TestDictFields:
    def test_repeatable_key_value_pairs(self):
        uc = FakeUseCase()
        cli = _build_cli(uc, DictFieldRequest)
        result = _run(cli, ["--name", "foo", "--tag", "A=1", "--tag", "B=2"])
        assert result.exit_code == 0
        assert uc.last_request.tags == {"A": "1", "B": "2"}

    def test_omitted_dict_defaults_to_empty(self):
        uc = FakeUseCase()
        cli = _build_cli(uc, DictFieldRequest)
        result = _run(cli, ["--name", "foo"])
        assert result.exit_code == 0
        assert uc.last_request.tags == {}

    def test_bad_key_value_rejected(self):
        uc = FakeUseCase()
        cli = _build_cli(uc, DictFieldRequest)
        result = _run(cli, ["--name", "foo", "--tag", "no-equals-sign"])
        assert result.exit_code != 0
        assert uc.last_request is None


# ---------------------------------------------------------------------------
# List[BaseModel] fields (JSON string options)
# ---------------------------------------------------------------------------


class Item(BaseModel):
    order: str
    label: str


class ListFieldRequest(BaseModel):
    name: str = Field(description="Name.")
    items: list[Item] = Field(description="JSON array of items.")


class TestListModelFields:
    def test_valid_json_parsed(self):
        uc = FakeUseCase()
        cli = _build_cli(uc, ListFieldRequest)
        data = json.dumps([{"order": "1", "label": "first"}])
        result = _run(cli, ["--name", "foo", "--items", data])
        assert result.exit_code == 0
        assert len(uc.last_request.items) == 1
        assert uc.last_request.items[0].label == "first"

    def test_invalid_json_rejected(self):
        uc = FakeUseCase()
        cli = _build_cli(uc, ListFieldRequest)
        result = _run(cli, ["--name", "foo", "--items", "not json"])
        assert result.exit_code != 0
        assert "Invalid" in result.output
        assert "JSON" in result.output

    def test_multiple_items(self):
        uc = FakeUseCase()
        cli = _build_cli(uc, ListFieldRequest)
        data = json.dumps(
            [
                {"order": "1", "label": "a"},
                {"order": "2", "label": "b"},
            ]
        )
        result = _run(cli, ["--name", "foo", "--items", data])
        assert result.exit_code == 0
        assert len(uc.last_request.items) == 2
