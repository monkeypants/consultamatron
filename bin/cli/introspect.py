"""Command generation from usecase and DTO introspection.

Reads Pydantic model fields from request DTOs and produces Click
commands mechanically. Each DTO field becomes a CLI --option with
type, required/optional, and help text derived from field metadata.

See docs/cli-command-generation.md for the full convention reference.
"""

from __future__ import annotations

import enum
import json
import typing
from typing import Any, Callable

import click
from pydantic import BaseModel
from pydantic.fields import FieldInfo

from practice.exceptions import DomainError


def _extra_dict(field_info: FieldInfo) -> dict[str, Any]:
    """Return json_schema_extra as a dict, or empty dict."""
    extra = field_info.json_schema_extra
    return extra if isinstance(extra, dict) else {}


def _click_type(field_info: FieldInfo) -> click.ParamType | None:
    """Derive a Click parameter type from Pydantic field metadata.

    Returns click.Choice for fields annotated with choices in
    json_schema_extra, or None to use Click's default string type.
    """
    extra = _extra_dict(field_info)
    choices = extra.get("choices")
    if choices is not None:
        if isinstance(choices, type) and issubclass(choices, enum.Enum):
            return click.Choice([m.value for m in choices])
        if isinstance(choices, (list, tuple)):
            return click.Choice(list(choices))
    return None


def _is_dict_str_str(annotation: Any) -> bool:
    """True if annotation is dict[str, str]."""
    origin = typing.get_origin(annotation)
    if origin is dict:
        args = typing.get_args(annotation)
        return len(args) == 2 and args[0] is str and args[1] is str
    return False


def _get_list_item_model(annotation: Any) -> type[BaseModel] | None:
    """If annotation is list[SomeBaseModel], return the item model."""
    origin = typing.get_origin(annotation)
    if origin is list:
        args = typing.get_args(annotation)
        if args and isinstance(args[0], type) and issubclass(args[0], BaseModel):
            return args[0]
    return None


def _parse_key_value_pairs(raw: tuple[str, ...]) -> dict[str, str]:
    """Parse Key=Value strings from repeatable --option values."""
    result: dict[str, str] = {}
    for item in raw:
        key, sep, value = item.partition("=")
        if not sep:
            raise click.BadParameter(f"Field must be Key=Value, got: {item}")
        result[key] = value
    return result


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
        Override for --help text. Defaults to request_model's
        class docstring when not provided.
    """
    params: list[click.Parameter] = []
    # Maps Click param name -> DTO field name when they differ.
    name_map: dict[str, str] = {}
    # DTO field names whose values need Key=Value parsing.
    dict_fields: set[str] = set()
    # DTO field name -> Pydantic model class for JSON list fields.
    list_model_fields: dict[str, type[BaseModel]] = {}

    for field_name, field_info in request_model.model_fields.items():
        required = field_info.is_required()
        extra = _extra_dict(field_info)

        cli_name = extra.get("cli_name", field_name)
        option_name = f"--{cli_name.replace('_', '-')}"

        if cli_name != field_name:
            click_param = cli_name.replace("-", "_")
            name_map[click_param] = field_name

        kwargs: dict[str, Any] = {
            "help": field_info.description or "",
        }

        annotation = field_info.annotation

        if _is_dict_str_str(annotation):
            kwargs["multiple"] = True
            kwargs["required"] = False
            dict_fields.add(field_name)
        elif (item_model := _get_list_item_model(annotation)) is not None:
            kwargs["required"] = required
            list_model_fields[field_name] = item_model
        else:
            kwargs["required"] = required
            if not required:
                kwargs["default"] = field_info.default
            param_type = _click_type(field_info)
            if param_type is not None:
                kwargs["type"] = param_type

        params.append(click.Option([option_name], **kwargs))

    def callback(**kwargs: Any) -> None:
        di = click.get_current_context().obj
        usecase = getattr(di, usecase_attr)

        # Remap CLI param names to DTO field names.
        for click_param, dto_field in name_map.items():
            if click_param in kwargs:
                kwargs[dto_field] = kwargs.pop(click_param)

        # Transform dict fields from tuple of "Key=Value" strings.
        for dto_field in dict_fields:
            kwargs[dto_field] = _parse_key_value_pairs(kwargs[dto_field])

        # Transform list[BaseModel] fields from JSON strings.
        for dto_field, item_model in list_model_fields.items():
            raw = kwargs[dto_field]
            try:
                data = json.loads(raw)
            except json.JSONDecodeError as e:
                opt = dto_field.replace("_", "-")
                raise click.BadParameter(f"Invalid JSON for --{opt}: {e}") from e
            kwargs[dto_field] = [item_model(**item) for item in data]

        try:
            resp = usecase.execute(request_model(**kwargs))
        except DomainError as e:
            raise click.ClickException(str(e))
        format_output(resp)

    return click.Command(
        name=name,
        params=params,
        callback=callback,
        help=help_text or request_model.__doc__,
    )
