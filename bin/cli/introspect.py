"""Command generation from usecase and DTO introspection.

Reads Pydantic model fields from request DTOs and produces Click
commands mechanically. Each DTO field becomes a CLI --option with
type, required/optional, and help text derived from field metadata.

This module is the proof-of-concept for #46. The pattern generalises
to bounded-context command registries (#29).
"""

from __future__ import annotations

import enum
from typing import Any, Callable

import click
from pydantic import BaseModel
from pydantic.fields import FieldInfo

from bin.cli.exceptions import DomainError


def _click_type(field_info: FieldInfo) -> click.ParamType | None:
    """Derive a Click parameter type from Pydantic field metadata.

    Returns click.Choice for fields annotated with choices in
    json_schema_extra, or None to use Click's default string type.
    """
    extra = field_info.json_schema_extra
    if isinstance(extra, dict):
        choices = extra.get("choices")
        if choices is not None:
            if isinstance(choices, type) and issubclass(choices, enum.Enum):
                return click.Choice([m.value for m in choices])
            if isinstance(choices, (list, tuple)):
                return click.Choice(list(choices))
    return None


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

    Parameters
    ----------
    name:
        Click command name (e.g. "register").
    request_model:
        Pydantic model class for the request DTO.
    usecase_attr:
        Attribute name on the DI Container.
    format_output:
        Callback receiving the response for terminal output.
    help_text:
        Command --help text. Pass ``UseCase.__doc__`` to derive
        help from the usecase docstring.
    """
    params: list[click.Parameter] = []

    for field_name, field_info in request_model.model_fields.items():
        required = field_info.is_required()
        option_name = f"--{field_name.replace('_', '-')}"

        kwargs: dict[str, Any] = {
            "required": required,
            "help": field_info.description or "",
        }

        if not required:
            kwargs["default"] = field_info.default

        param_type = _click_type(field_info)
        if param_type is not None:
            kwargs["type"] = param_type

        params.append(click.Option([option_name], **kwargs))

    def callback(**kwargs: Any) -> None:
        di = click.get_current_context().obj
        usecase = getattr(di, usecase_attr)
        try:
            resp = usecase.execute(request_model(**kwargs))
        except DomainError as e:
            raise click.ClickException(str(e))
        format_output(resp)

    return click.Command(
        name=name,
        params=params,
        callback=callback,
        help=help_text,
    )
