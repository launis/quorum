from __future__ import annotations

"""Schema Factory for generating dynamic Pydantic schemas for LLM Structured Outputs.

Extracts and centralizes all dynamic Pydantic model creation logic from the
monolithic PromptCompiler, following SRP (Rule 88).
"""

import logging
import re
from collections.abc import Callable, Mapping, Sequence
from typing import TYPE_CHECKING, Any, Literal, cast

from pydantic import BaseModel, ConfigDict, Field, create_model

from backend_v2.core.registry import StrippedBaseTDAExtraction, get_schema_strategy
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.prompt_blocks import PromptBlock
from backend_v2.models.domain.system_config import AllowedMCPTool
from backend_v2.models.dtos.atom_result import AtomResultDTO
from backend_v2.models.dtos.mcp import (
    MCPFunctionDefinitionDTO,
    MCPToolDeclarationDTO,
    MCPToolDescriptorDTO,
    MCPToolInputSchemaDTO,
    MCPToolSchemaPropertyDTO,
)
from backend_v2.models.dtos.step_output import StepOutputDTO
from backend_v2.models.enums import JSONSchemaPropertyType

__all__ = ["DynamicFieldDefinition", "SchemaFactory", "StrippedBaseTDAExtraction"]

logger = logging.getLogger(__name__)

type DynamicFieldDefinition = tuple[Any, Any]
_SAFE_MODEL_NAME_SANITIZER = re.compile(r"[^a-zA-Z0-9_]")


class SchemaFactory:
    """Centralizes dynamic Pydantic V2 schema generation for LLM Structured Outputs.

    Encapsulates all create_model() operations previously embedded in the
    monolithic PromptCompiler, enforcing Single Responsibility Principle.

    Attributes:
        _resolve_i18n: Injected callable for resolving I18n text objects to locale strings.
    """

    def __init__(self, resolve_i18n_fn: Callable[..., str]) -> None:
        """Initialize SchemaFactory with an I18n resolution callable.

        Args:
            resolve_i18n_fn: Callable that resolves I18n objects to strings given a locale.
        """
        self._resolve_i18n = resolve_i18n_fn
        self._schema_cache: dict[str, type[BaseModel]] = {}

    def build_dynamic_schema(
        self,
        schema_name: str,
        criteria: list[PromptBlock],
        has_shuffled_atoms: bool = False,
        target_locale: str = "en",
        *,
        strictness_level: int,
        source_document_ids: list[str] | None = None,
        allowed_atom_ids: list[str] | None = None,
        allowed_dynamic_keys: list[str] | None = None,
        max_evaluations: int | None = None,
        expected_sdui_type: str = "grid",
        dag_results: Sequence[StepOutputDTO] | Mapping[str, AtomResultDTO] | None = None,
    ) -> type[BaseModel]:
        """Build a dynamic Pydantic V2 model for LLM Structured Outputs.

        Args:
            schema_name: Name for the generated Pydantic model class.
            criteria: List of PromptBlock definitions driving schema fields.
            has_shuffled_atoms: Whether to include shuffled atom evaluation fields.
            target_locale: Target language code for label resolution.
            strictness_level: Strictness level to control field leniency.
            source_document_ids: Dynamic literals corresponding to available documents.
            allowed_atom_ids: Optional list of specific atom IDs to allow.
            allowed_dynamic_keys: Optional list of dynamic keys allowed.
            max_evaluations: Maximum number of evaluations allowed.
            expected_sdui_type: The SDUI type string from the StepRule.
            dag_results: Optional sequence or mapping of upstream DAG step outputs.

        Returns:
            A dynamically generated Pydantic model class.

        Raises:
            AppException: If dynamic schema compilation fails.
            ConfigurationError: If a PromptBlock is structurally invalid.
        """
        criteria_ids = "_".join(sorted(str(c.id) for c in criteria if c.id))
        doc_ids_str = ""
        if source_document_ids is not None:
            doc_ids_str = "_".join(sorted(source_document_ids))

        atom_ids_str = ""
        if allowed_atom_ids is not None:
            atom_ids_str = "_".join(sorted(allowed_atom_ids))

        dynamic_keys_str = ""
        if allowed_dynamic_keys is not None:
            dynamic_keys_str = "_".join(sorted(allowed_dynamic_keys))
        cache_key = f"{schema_name}_{criteria_ids}_{has_shuffled_atoms}_{target_locale}_{strictness_level}_{doc_ids_str}_{atom_ids_str}_{dynamic_keys_str}"

        if cache_key in self._schema_cache:
            return self._schema_cache[cache_key]

        strategy_cls = get_schema_strategy(expected_sdui_type)
        strategy = strategy_cls(resolve_i18n=self._resolve_i18n)

        model_class = strategy.build_schema(
            schema_name=schema_name,
            criteria=criteria,
            has_shuffled_atoms=has_shuffled_atoms,
            target_locale=target_locale,
            strictness_level=strictness_level,
            source_document_ids=source_document_ids,
            allowed_atom_ids=allowed_atom_ids,
            allowed_dynamic_keys=allowed_dynamic_keys,
            max_evaluations=max_evaluations,
            dag_results=dag_results,
        )

        self._schema_cache[cache_key] = model_class
        return model_class

    def build_chunk_response_schema(self, schema_name: str, item_schema: type[BaseModel]) -> type[BaseModel]:
        """Build dynamic Pydantic V2 schema for chunked Map-Reduce execution.

        Nests a target Payload schema inside a structurally strict chunk-array list.

        Args:
            schema_name: Name for the generated Pydantic model class.
            item_schema: The inner Pydantic model defining each record's payload.

        Returns:
            A dynamically generated Pydantic model class for chunk responses.
        """
        ChunkRecordModel = create_model(
            f"{schema_name}Record",
            __config__=ConfigDict(extra="forbid", strict=True, frozen=True),
            original_id=(
                str,
                Field(..., description="The original system identifier of the source record."),
            ),
            payload=(
                item_schema,
                Field(..., description="The validated item payload matching the target data schema."),
            ),
        )

        records_tuple: Any = (
            list[Any],
            Field(
                ...,
                description="List of records contained in this execution chunk.",
            ),
        )
        if not TYPE_CHECKING:
            records_tuple = (list[ChunkRecordModel], records_tuple[1])

        DynamicModel = create_model(
            schema_name,
            __config__=ConfigDict(extra="forbid", strict=True, frozen=True),
            chunk_id=(
                str,
                Field(..., description="The unique system identifier of the current execution chunk."),
            ),
            records=records_tuple,
        )

        return DynamicModel

    @classmethod
    def _resolve_mcp_property_type(
        cls,
        model_prefix: str,
        prop_name: str,
        prop: MCPToolSchemaPropertyDTO,
    ) -> Any:
        """Translate a single MCPToolSchemaPropertyDTO node into a Python runtime type annotation.

        Args:
            model_prefix: Sanitized prefix for nested model generation.
            prop_name: Name of the property being resolved.
            prop: Recursive property schema DTO.

        Returns:
            Runtime type annotation suitable for pydantic.create_model.

        Raises:
            AppException: If an object property is missing required keys in its properties map.
        """
        if prop.enum_values is not None and len(prop.enum_values) > 0:
            enum_tuple = tuple(prop.enum_values)
            return Literal.__getitem__(enum_tuple)

        if prop.any_of is not None and len(prop.any_of) > 0:
            resolved_union: Any = None
            for idx, sub_prop in enumerate(prop.any_of):
                sub_type = cls._resolve_mcp_property_type(
                    f"{model_prefix}_{prop_name}_Sub{idx}",
                    prop_name,
                    sub_prop,
                )
                if resolved_union is None:
                    resolved_union = sub_type
                else:
                    resolved_union = resolved_union | sub_type
            return resolved_union

        match prop.type:
            case JSONSchemaPropertyType.STRING:
                return str
            case JSONSchemaPropertyType.INTEGER:
                return int
            case JSONSchemaPropertyType.NUMBER:
                return float
            case JSONSchemaPropertyType.BOOLEAN:
                return bool
            case JSONSchemaPropertyType.NULL:
                return type(None)
            case None:
                return str | None
            case JSONSchemaPropertyType.ARRAY:
                if prop.items is not None:
                    item_type = cls._resolve_mcp_property_type(
                        f"{model_prefix}_{prop_name}_Item",
                        "item",
                        prop.items,
                    )
                    if not TYPE_CHECKING:
                        return list[item_type]
                return list[str]
            case JSONSchemaPropertyType.OBJECT:
                if prop.properties is None:
                    logger.error(
                        "[SchemaFactory] %s: Object property '%s' in model '%s' is missing 'properties' definition.",
                        ErrorCodes.VALIDATION_FAILED.name,
                        prop_name,
                        model_prefix,
                        extra={
                            "error_code": ErrorCodes.VALIDATION_FAILED.name,
                            "model_prefix": model_prefix,
                            "property_name": prop_name,
                        },
                    )
                    raise AppException(
                        message=(
                            f"Object property '{prop_name}' in model '{model_prefix}' is missing 'properties' definition."
                        ),
                        status_code=422,
                        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                    )
                return cls._build_mcp_object_model(
                    model_name=f"{model_prefix}_{prop_name}",
                    properties=prop.properties,
                    required_keys=prop.required,
                )

    @classmethod
    def _build_mcp_object_model(
        cls,
        model_name: str,
        properties: Mapping[str, MCPToolSchemaPropertyDTO],
        required_keys: Sequence[str] | None,
    ) -> type[BaseModel]:
        """Build a strict frozen Pydantic V2 model from a mapping of MCPToolSchemaPropertyDTO nodes.

        Args:
            model_name: Sanitized class name for the generated Pydantic model.
            properties: Mapping of parameter names to property schema DTOs.
            required_keys: Optional sequence of parameter names that are required.

        Returns:
            Dynamically compiled Pydantic V2 BaseModel subclass.

        Raises:
            AppException: If a required key is absent from the properties map (ErrorCodes.VALIDATION_FAILED).
        """
        required_set: set[str] = set()
        if required_keys is not None:
            required_set = set(required_keys)
        missing_required = sorted(required_set - set(properties.keys()))
        if missing_required:
            logger.error(
                "[SchemaFactory] %s: Required MCP schema keys %s are absent from properties for model '%s'.",
                ErrorCodes.VALIDATION_FAILED.name,
                missing_required,
                model_name,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.name, "model_name": model_name},
            )
            raise AppException(
                message=(
                    f"Required MCP schema keys {missing_required} are absent from properties for model '{model_name}'."
                ),
                status_code=422,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        field_definitions: dict[str, DynamicFieldDefinition] = {}
        for prop_name, prop_dto in properties.items():
            resolved_type = cls._resolve_mcp_property_type(model_name, prop_name, prop_dto)
            if prop_name in required_set:
                field_definitions[prop_name] = (
                    resolved_type,
                    Field(..., description=prop_dto.description),
                )
            else:
                optional_type: Any = resolved_type | None
                field_definitions[prop_name] = (
                    optional_type,
                    Field(default=None, description=prop_dto.description),
                )

        unpacked_fields: Any = field_definitions
        created_model = create_model(
            model_name,
            __config__=ConfigDict(strict=True, extra="forbid", frozen=True),
            **unpacked_fields,
        )
        return cast(type[BaseModel], created_model)

    @classmethod
    def create_mcp_tool_argument_model(
        cls,
        namespaced_alias: str,
        input_schema: MCPToolInputSchemaDTO,
    ) -> type[BaseModel]:
        """Compile a strict runtime Pydantic V2 argument validation model from an MCPToolInputSchemaDTO.

        Args:
            namespaced_alias: Full namespaced tool alias ('{gateway_slug}__{tool_id}').
            input_schema: Strict recursive JSON Schema DTO for the tool's input parameters.

        Returns:
            Dynamically generated Pydantic V2 BaseModel enforcing strict=True, extra='forbid', frozen=True.

        Raises:
            AppException: If namespaced_alias is empty or input_schema has invalid required keys
                (ErrorCodes.VALIDATION_FAILED).
        """
        clean_alias = namespaced_alias.strip()
        if not clean_alias:
            logger.error(
                "[SchemaFactory] %s: Cannot compile MCP tool argument model for empty namespaced_alias.",
                ErrorCodes.VALIDATION_FAILED.name,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.name},
            )
            raise AppException(
                message="Cannot compile MCP tool argument model for empty namespaced_alias.",
                status_code=422,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        safe_suffix = _SAFE_MODEL_NAME_SANITIZER.sub("_", clean_alias)
        model_name = f"MCPArgs_{safe_suffix}"
        return cls._build_mcp_object_model(
            model_name=model_name,
            properties=input_schema.properties,
            required_keys=input_schema.required,
        )

    @classmethod
    def build_mcp_tool_declaration(
        cls,
        namespaced_alias: str,
        tool: AllowedMCPTool | MCPToolDescriptorDTO,
    ) -> MCPToolDeclarationDTO:
        """Build an OpenAI-compatible MCPToolDeclarationDTO for an allowed or hydrated MCP tool.

        Args:
            namespaced_alias: Full namespaced tool alias ('{gateway_slug}__{tool_id}').
            tool: AllowedMCPTool domain configuration or hydrated MCPToolDescriptorDTO.

        Returns:
            Strongly typed MCPToolDeclarationDTO ready for LLM provider serialization.

        Raises:
            AppException: If namespaced_alias is empty (ErrorCodes.VALIDATION_FAILED).
        """
        clean_alias = namespaced_alias.strip()
        if not clean_alias:
            logger.error(
                "[SchemaFactory] %s: Cannot build MCP tool declaration for empty namespaced_alias.",
                ErrorCodes.VALIDATION_FAILED.name,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.name},
            )
            raise AppException(
                message="Cannot build MCP tool declaration for empty namespaced_alias.",
                status_code=422,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        return MCPToolDeclarationDTO(
            type="function",
            function=MCPFunctionDefinitionDTO(
                name=clean_alias,
                description=tool.description,
                parameters=tool.input_schema,
                strict=True,
            ),
        )
