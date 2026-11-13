"""PostgreSQL 19 SQL constants, hydration, upsert, and fetch stage for prompt_blocks and steps."""

from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from pydantic_core import to_json

from backend_v2.database.postgres.entity_adapter.coercion_and_constants import (
    _coerce_uuid_or_str,
    _decode_jsonb_column,
    _encode_optional_jsonb,
    _format_optional_uuid7,
    _format_org_uuid7,
    _parse_optional_uuid7,
    _parse_org_uuid7,
    execute_entity_delete,
    execute_entity_upsert,
    resolve_effective_timeout,
    translate_postgres_exception,
    validate_hydrated_row,
)
from backend_v2.database.postgres.pool import AsyncPgConnectionProtocol, AsyncPgRecordProtocol
from backend_v2.exceptions import AppException
from backend_v2.models.core_base import format_prefixed_uuid7, parse_prefixed_uuid7
from backend_v2.models.domain.prompt_blocks import (
    AnyPromptBlock,
    MatrixPromptBlock,
    PersonaPromptBlock,
    PromptBlockAdapter,
    ProtocolPromptBlock,
    SystemRulePromptBlock,
)
from backend_v2.models.domain.step import Step
from backend_v2.models.enums import EntityPrefix, PromptBlockCategory

__all__ = [
    "_DELETE_PROMPT_BLOCK_SQL",
    "_DELETE_STEP_CRITERIA_BLOCKS_SQL",
    "_DELETE_STEP_SQL",
    "_GET_PROMPT_BLOCK_SQL",
    "_GET_STEP_SQL",
    "_INSERT_STEP_CRITERIA_BLOCKS_SQL",
    "_LIST_PROMPT_BLOCKS_SQL",
    "_LIST_STEPS_SQL",
    "_UPSERT_PROMPT_BLOCK_SQL",
    "_UPSERT_STEP_SQL",
    "delete_prompt_block_row",
    "delete_step_row",
    "get_prompt_block_row",
    "get_step_row",
    "hydrate_prompt_block_row",
    "hydrate_step_row",
    "list_prompt_block_rows",
    "list_step_rows",
    "upsert_prompt_block_row",
    "upsert_step_row",
]

_UPSERT_PROMPT_BLOCK_SQL: str = """INSERT INTO prompt_blocks (id, slug, organization_id, label, description,
    output_extensions, theory_grounding, category_id, type, is_evaluative, allow_decimals, allow_contextual_override,
    is_lightweight_protocol, target_input_key, ai_description, scales, rows, columns, computed_min, computed_max,
    instruction_text, role_enforcement, tone_directives, protocol_instructions)
VALUES ($1::uuid, $2, $3::uuid, $4::jsonb, $5::jsonb, $6::jsonb, $7::jsonb, $8, $9, $10, $11, $12, $13, $14, $15,
    $16::jsonb, $17::jsonb, $18::jsonb, $19, $20, $21, $22, $23::jsonb, $24)
ON CONFLICT (id) DO UPDATE SET slug = EXCLUDED.slug, organization_id = EXCLUDED.organization_id, label = EXCLUDED.label,
    description = EXCLUDED.description, output_extensions = EXCLUDED.output_extensions,
    theory_grounding = EXCLUDED.theory_grounding, category_id = EXCLUDED.category_id, type = EXCLUDED.type,
    is_evaluative = EXCLUDED.is_evaluative, allow_decimals = EXCLUDED.allow_decimals,
    allow_contextual_override = EXCLUDED.allow_contextual_override,
    is_lightweight_protocol = EXCLUDED.is_lightweight_protocol, target_input_key = EXCLUDED.target_input_key,
    ai_description = EXCLUDED.ai_description, scales = EXCLUDED.scales, rows = EXCLUDED.rows,
    columns = EXCLUDED.columns, computed_min = EXCLUDED.computed_min, computed_max = EXCLUDED.computed_max,
    instruction_text = EXCLUDED.instruction_text, role_enforcement = EXCLUDED.role_enforcement,
    tone_directives = EXCLUDED.tone_directives, protocol_instructions = EXCLUDED.protocol_instructions"""

_GET_PROMPT_BLOCK_SQL: str = """SELECT id, slug, organization_id, label, description, output_extensions,
       theory_grounding, category_id, type, is_evaluative, allow_decimals, allow_contextual_override,
       is_lightweight_protocol, target_input_key, ai_description, scales, rows, columns, computed_min,
       computed_max, instruction_text, role_enforcement, tone_directives, protocol_instructions
FROM prompt_blocks WHERE id = $1::uuid"""

_LIST_PROMPT_BLOCKS_SQL: str = """SELECT id, slug, organization_id, label, description, output_extensions,
       theory_grounding, category_id, type, is_evaluative, allow_decimals, allow_contextual_override,
       is_lightweight_protocol, target_input_key, ai_description, scales, rows, columns, computed_min,
       computed_max, instruction_text, role_enforcement, tone_directives, protocol_instructions FROM prompt_blocks"""

_UPSERT_STEP_SQL: str = """INSERT INTO steps (id, slug, organization_id, name, description, type, hook, role_block_id,
    extraction_protocol_block_id, execution_persona_block_id, pre_hooks, post_hooks, safety,
    allowed_mcp_tools, mcp_tool_params, cognitive_tier, expected_inputs, is_system_core, engine_type, zone)
VALUES ($1::uuid, $2, $3::uuid, $4::jsonb, $5::jsonb, $6, $7, $8::uuid, $9::uuid, $10::uuid,
    $11::jsonb, $12::jsonb, $13, $14::jsonb, $15::jsonb, $16, $17::jsonb, $18, $19, $20)
ON CONFLICT (id) DO UPDATE SET slug = EXCLUDED.slug, organization_id = EXCLUDED.organization_id, name = EXCLUDED.name,
    description = EXCLUDED.description, type = EXCLUDED.type, hook = EXCLUDED.hook,
    role_block_id = EXCLUDED.role_block_id, extraction_protocol_block_id = EXCLUDED.extraction_protocol_block_id,
    execution_persona_block_id = EXCLUDED.execution_persona_block_id,
    pre_hooks = EXCLUDED.pre_hooks, post_hooks = EXCLUDED.post_hooks, safety = EXCLUDED.safety,
    allowed_mcp_tools = EXCLUDED.allowed_mcp_tools, mcp_tool_params = EXCLUDED.mcp_tool_params,
    cognitive_tier = EXCLUDED.cognitive_tier, expected_inputs = EXCLUDED.expected_inputs,
    is_system_core = EXCLUDED.is_system_core, engine_type = EXCLUDED.engine_type, zone = EXCLUDED.zone"""

_DELETE_STEP_CRITERIA_BLOCKS_SQL: str = "DELETE FROM step_criteria_blocks WHERE step_id = $1::uuid"

_INSERT_STEP_CRITERIA_BLOCKS_SQL: str = """INSERT INTO step_criteria_blocks (step_id, prompt_block_id, position)
SELECT $1::uuid, blk_id, pos
FROM UNNEST($2::uuid[], $3::int[]) AS u(blk_id, pos)"""

_STEP_CRITERIA_PROJECTION: str = (
    "COALESCE((SELECT array_agg(scb.prompt_block_id ORDER BY scb.position ASC) "
    "FROM step_criteria_blocks scb WHERE scb.step_id = steps.id), ARRAY[]::uuid[]) AS criteria_block_ids"
)

_GET_STEP_SQL: str = f"""SELECT id, slug, organization_id, name, description, type, hook, role_block_id,
       extraction_protocol_block_id, execution_persona_block_id, {_STEP_CRITERIA_PROJECTION}, pre_hooks, post_hooks,
       safety, allowed_mcp_tools, mcp_tool_params, cognitive_tier, expected_inputs, is_system_core,
       engine_type, zone FROM steps WHERE id = $1::uuid"""

_LIST_STEPS_SQL: str = f"""SELECT id, slug, organization_id, name, description, type, hook, role_block_id,
       extraction_protocol_block_id, execution_persona_block_id, {_STEP_CRITERIA_PROJECTION}, pre_hooks, post_hooks,
       safety, allowed_mcp_tools, mcp_tool_params, cognitive_tier, expected_inputs, is_system_core,
       engine_type, zone FROM steps"""


async def _fetch_row(
    conn: AsyncPgConnectionProtocol,
    timeout: float | None,
    sql: str,
    entity_uuid: object,
    entity_id: str,
    *,
    table_name: str = "prompt_blocks",
) -> AsyncPgRecordProtocol | None:
    """Execute fetchrow with timeout and translate driver errors to AppException.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds, or None to resolve from settings.
        sql: Parameterized SELECT SQL statement.
        entity_uuid: Parsed 16-byte UUID primary key parameter.
        entity_id: Canonical Opaque Stripe ID of the target entity for error reporting.
        table_name: Canonical PostgreSQL table name for structured diagnostics.

    Returns:
        Database record if found, or None.

    Raises:
        AppException: With STORAGE_ACCESS_FAILED if the database query fails.
    """
    effective_timeout = resolve_effective_timeout(timeout)
    try:
        return await conn.fetchrow(sql, entity_uuid, timeout=effective_timeout)
    except AppException:
        raise
    except Exception as exc:
        raise translate_postgres_exception(
            exc,
            operation="SELECT",
            table_name=table_name,
            entity_id=entity_id,
        ) from exc


def hydrate_prompt_block_row(row: AsyncPgRecordProtocol) -> AnyPromptBlock:
    """Hydrate a polymorphic AnyPromptBlock from a database row via PromptBlockAdapter.

    Args:
        row: Database record from the prompt_blocks table.

    Returns:
        Validated MatrixPromptBlock, PersonaPromptBlock, ProtocolPromptBlock, or SystemRulePromptBlock.

    Raises:
        AppException: With VALIDATION_FAILED if UUID formatting or variant schema validation fails.
    """
    blk_id = format_prefixed_uuid7(_coerce_uuid_or_str(row["id"]), EntityPrefix.PROMPT_BLOCK)
    org_id = _format_org_uuid7(row["organization_id"])
    cat = str(row["category_id"])
    if cat == PromptBlockCategory.MATRIX.value:
        return validate_hydrated_row(
            PromptBlockAdapter,
            {
                "id": blk_id,
                "slug": row["slug"],
                "organization_id": org_id,
                "label": _decode_jsonb_column(row["label"]),
                "description": _decode_jsonb_column(row["description"]),
                "output_extensions": _decode_jsonb_column(row["output_extensions"]),
                "theory_grounding": _decode_jsonb_column(row["theory_grounding"]),
                "category_id": cat,
                "type": row["type"],
                "is_evaluative": row["is_evaluative"],
                "allow_decimals": row["allow_decimals"],
                "allow_contextual_override": row["allow_contextual_override"],
                "is_lightweight_protocol": row["is_lightweight_protocol"],
                "target_input_key": row["target_input_key"],
                "ai_description": row["ai_description"],
                "scales": _decode_jsonb_column(row["scales"]),
                "rows": _decode_jsonb_column(row["rows"]),
                "columns": _decode_jsonb_column(row["columns"]),
                "computed_min": row["computed_min"],
                "computed_max": row["computed_max"],
            },
            table_name="prompt_blocks",
            entity_id=blk_id,
        )
    if cat in (PromptBlockCategory.EXECUTION_PERSONA.value, PromptBlockCategory.AGENT_ROLE.value):
        return validate_hydrated_row(
            PromptBlockAdapter,
            {
                "id": blk_id,
                "slug": row["slug"],
                "organization_id": org_id,
                "label": _decode_jsonb_column(row["label"]),
                "description": _decode_jsonb_column(row["description"]),
                "output_extensions": _decode_jsonb_column(row["output_extensions"]),
                "theory_grounding": _decode_jsonb_column(row["theory_grounding"]),
                "category_id": cat,
                "type": row["type"],
                "is_evaluative": row["is_evaluative"],
                "allow_decimals": row["allow_decimals"],
                "is_lightweight_protocol": row["is_lightweight_protocol"],
                "role_enforcement": row["role_enforcement"],
                "tone_directives": _decode_jsonb_column(row["tone_directives"]),
            },
            table_name="prompt_blocks",
            entity_id=blk_id,
        )
    if cat == PromptBlockCategory.PROTOCOL.value:
        return validate_hydrated_row(
            PromptBlockAdapter,
            {
                "id": blk_id,
                "slug": row["slug"],
                "organization_id": org_id,
                "label": _decode_jsonb_column(row["label"]),
                "description": _decode_jsonb_column(row["description"]),
                "output_extensions": _decode_jsonb_column(row["output_extensions"]),
                "theory_grounding": _decode_jsonb_column(row["theory_grounding"]),
                "category_id": cat,
                "type": row["type"],
                "is_evaluative": row["is_evaluative"],
                "allow_decimals": row["allow_decimals"],
                "is_lightweight_protocol": row["is_lightweight_protocol"],
                "protocol_instructions": row["protocol_instructions"],
            },
            table_name="prompt_blocks",
            entity_id=blk_id,
        )
    if cat in (PromptBlockCategory.SYSTEM_RULE.value, PromptBlockCategory.RUNTIME_VARIABLES.value):
        return validate_hydrated_row(
            PromptBlockAdapter,
            {
                "id": blk_id,
                "slug": row["slug"],
                "organization_id": org_id,
                "label": _decode_jsonb_column(row["label"]),
                "description": _decode_jsonb_column(row["description"]),
                "output_extensions": _decode_jsonb_column(row["output_extensions"]),
                "theory_grounding": _decode_jsonb_column(row["theory_grounding"]),
                "category_id": cat,
                "type": row["type"],
                "is_evaluative": row["is_evaluative"],
                "allow_decimals": row["allow_decimals"],
                "is_lightweight_protocol": row["is_lightweight_protocol"],
                "instruction_text": row["instruction_text"],
            },
            table_name="prompt_blocks",
            entity_id=blk_id,
        )
    return validate_hydrated_row(
        PromptBlockAdapter,
        {
            "id": blk_id,
            "slug": row["slug"],
            "organization_id": org_id,
            "category_id": cat,
            "type": row["type"],
        },
        table_name="prompt_blocks",
        entity_id=blk_id,
    )


async def upsert_prompt_block_row(conn: AsyncPgConnectionProtocol, timeout: float, block: AnyPromptBlock) -> str:
    """Persist a polymorphic AnyPromptBlock into prompt_blocks.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        block: Validated concrete PromptBlock domain model.

    Returns:
        Canonical blk_<hex> prompt block identifier.

    Raises:
        AppException: With VALIDATION_FAILED on invalid ID or STORAGE_ACCESS_FAILED if persistence fails.
    """
    dumped = block.model_dump(mode="json")
    allow_ctx_override = False
    target_input_key = ai_description = scales_json = rows_json = columns_json = None
    computed_min = computed_max = None
    instruction_text = role_enforcement = tone_directives_json = protocol_instructions = None
    if isinstance(block, MatrixPromptBlock):
        allow_ctx_override = block.allow_contextual_override
        target_input_key = block.target_input_key
        ai_description = block.ai_description
        scales_json = _encode_optional_jsonb(dumped["scales"])
        rows_json = _encode_optional_jsonb(dumped["rows"])
        columns_json = _encode_optional_jsonb(dumped["columns"])
        computed_min = block.computed_min
        computed_max = block.computed_max
    elif isinstance(block, PersonaPromptBlock):
        role_enforcement = block.role_enforcement
        tone_directives_json = _encode_optional_jsonb(dumped["tone_directives"])
    elif isinstance(block, ProtocolPromptBlock):
        protocol_instructions = block.protocol_instructions
    elif isinstance(block, SystemRulePromptBlock):
        instruction_text = block.instruction_text
    return await execute_entity_upsert(
        conn,
        timeout,
        _UPSERT_PROMPT_BLOCK_SQL,
        parse_prefixed_uuid7(block.id, EntityPrefix.PROMPT_BLOCK),
        block.slug,
        _parse_org_uuid7(block.organization_id),
        to_json(dumped["label"]).decode("utf-8"),
        to_json(dumped["description"]).decode("utf-8"),
        to_json(dumped["output_extensions"]).decode("utf-8"),
        _encode_optional_jsonb(dumped["theory_grounding"]),
        str(block.category_id),
        str(block.type),
        block.is_evaluative,
        block.allow_decimals,
        allow_ctx_override,
        block.is_lightweight_protocol,
        target_input_key,
        ai_description,
        scales_json,
        rows_json,
        columns_json,
        computed_min,
        computed_max,
        instruction_text,
        role_enforcement,
        tone_directives_json,
        protocol_instructions,
        entity_id=block.id,
        entity_label="prompt_block",
    )


async def get_prompt_block_row(conn: AsyncPgConnectionProtocol, timeout: float, block_id: str) -> AnyPromptBlock | None:
    """Fetch an AnyPromptBlock by ID.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        block_id: Canonical blk_<hex> prompt block identifier.

    Returns:
        Hydrated AnyPromptBlock instance if found, or None.

    Raises:
        AppException: With VALIDATION_FAILED on invalid ID or STORAGE_ACCESS_FAILED on query error.
    """
    block_uuid = parse_prefixed_uuid7(block_id, EntityPrefix.PROMPT_BLOCK)
    row = await _fetch_row(conn, timeout, _GET_PROMPT_BLOCK_SQL, block_uuid, block_id)
    if row is None:
        return None
    return hydrate_prompt_block_row(row)


def _decode_criteria_block_ids(raw: object) -> object:
    """Decode ordered criteria_block_ids from a PostgreSQL uuid[] array or JSON payload.

    Args:
        raw: Raw database column payload (Sequence[UUID], Sequence[str], or JSON string/bytes).

    Returns:
        Ordered list of formatted blk_<hex32> strings, or the raw payload for Pydantic fail-fast rejection.
    """
    decoded = _decode_jsonb_column(raw)
    if not isinstance(decoded, Sequence) or isinstance(decoded, (str, bytes, bytearray)):
        return decoded
    formatted_ids: list[str] = []
    for item in decoded:
        if isinstance(item, UUID):
            formatted_ids.append(format_prefixed_uuid7(item, EntityPrefix.PROMPT_BLOCK))
        elif isinstance(item, str) and "_" in item:
            parsed_uuid = parse_prefixed_uuid7(item, EntityPrefix.PROMPT_BLOCK)
            formatted_ids.append(format_prefixed_uuid7(parsed_uuid, EntityPrefix.PROMPT_BLOCK))
        else:
            formatted_ids.append(format_prefixed_uuid7(_coerce_uuid_or_str(item), EntityPrefix.PROMPT_BLOCK))
    return formatted_ids


def hydrate_step_row(row: AsyncPgRecordProtocol) -> Step:
    """Hydrate a Step from a database row.

    Args:
        row: Database record from the steps table.

    Returns:
        Validated Step domain model.

    Raises:
        AppException: With VALIDATION_FAILED if UUID formatting or Step schema validation fails.
    """
    blk_p = EntityPrefix.PROMPT_BLOCK
    stp_id = format_prefixed_uuid7(_coerce_uuid_or_str(row["id"]), EntityPrefix.STEP)
    return validate_hydrated_row(
        Step,
        {
            "id": stp_id,
            "slug": row["slug"],
            "organization_id": _format_org_uuid7(row["organization_id"], default_system=True),
            "name": _decode_jsonb_column(row["name"]),
            "description": _decode_jsonb_column(row["description"]),
            "type": row["type"],
            "hook": row["hook"],
            "role_block_id": _format_optional_uuid7(row["role_block_id"], blk_p),
            "extraction_protocol_block_id": _format_optional_uuid7(row["extraction_protocol_block_id"], blk_p),
            "execution_persona_block_id": _format_optional_uuid7(row["execution_persona_block_id"], blk_p),
            "criteria_block_ids": _decode_criteria_block_ids(row["criteria_block_ids"]),
            "pre_hooks": _decode_jsonb_column(row["pre_hooks"]),
            "post_hooks": _decode_jsonb_column(row["post_hooks"]),
            "safety": row["safety"],
            "allowed_mcp_tools": _decode_jsonb_column(row["allowed_mcp_tools"]),
            "mcp_tool_params": _decode_jsonb_column(row["mcp_tool_params"]),
            "cognitive_tier": row["cognitive_tier"],
            "expected_inputs": _decode_jsonb_column(row["expected_inputs"]),
            "is_system_core": row["is_system_core"],
            "engine_type": row["engine_type"],
            "zone": row["zone"],
        },
        table_name="steps",
        entity_id=stp_id,
    )


async def upsert_step_row(conn: AsyncPgConnectionProtocol, timeout: float, step: Step) -> str:
    """Persist a Step into steps and synchronize ordered step_criteria_blocks via UNNEST.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        step: Validated Step domain model.

    Returns:
        Canonical stp_<hex> step identifier.

    Raises:
        AppException: With VALIDATION_FAILED on invalid ID or STORAGE_ACCESS_FAILED if persistence fails.
    """
    step_uuid = parse_prefixed_uuid7(step.id, EntityPrefix.STEP)
    seen_blk_uuids: set[UUID] = set()
    criteria_uuids: list[UUID] = []
    criteria_positions: list[int] = []
    for blk_id in step.criteria_block_ids:
        blk_uuid = parse_prefixed_uuid7(blk_id, EntityPrefix.PROMPT_BLOCK)
        if blk_uuid not in seen_blk_uuids:
            seen_blk_uuids.add(blk_uuid)
            criteria_positions.append(len(criteria_uuids))
            criteria_uuids.append(blk_uuid)

    dumped = step.model_dump(mode="json")
    tier_str: str | None = None
    if step.cognitive_tier is not None:
        tier_str = str(step.cognitive_tier)
    await execute_entity_upsert(
        conn,
        timeout,
        _UPSERT_STEP_SQL,
        step_uuid,
        step.slug,
        _parse_org_uuid7(step.organization_id),
        to_json(dumped["name"]).decode("utf-8"),
        _encode_optional_jsonb(dumped["description"]),
        str(step.type),
        step.hook,
        _parse_optional_uuid7(step.role_block_id, EntityPrefix.PROMPT_BLOCK),
        _parse_optional_uuid7(step.extraction_protocol_block_id, EntityPrefix.PROMPT_BLOCK),
        _parse_optional_uuid7(step.execution_persona_block_id, EntityPrefix.PROMPT_BLOCK),
        to_json(dumped["pre_hooks"]).decode("utf-8"),
        to_json(dumped["post_hooks"]).decode("utf-8"),
        step.safety,
        to_json(dumped["allowed_mcp_tools"]).decode("utf-8"),
        to_json(dumped["mcp_tool_params"]).decode("utf-8"),
        tier_str,
        to_json(dumped["expected_inputs"]).decode("utf-8"),
        step.is_system_core,
        str(step.engine_type),
        str(step.zone),
        entity_id=step.id,
        entity_label="step",
    )

    effective_timeout = resolve_effective_timeout(timeout)
    try:
        await conn.execute(_DELETE_STEP_CRITERIA_BLOCKS_SQL, step_uuid, timeout=effective_timeout)
        if criteria_uuids:
            await conn.execute(
                _INSERT_STEP_CRITERIA_BLOCKS_SQL,
                step_uuid,
                criteria_uuids,
                criteria_positions,
                timeout=effective_timeout,
            )
    except AppException:
        raise
    except Exception as exc:
        raise translate_postgres_exception(
            exc,
            operation="UPSERT",
            table_name="step_criteria_blocks",
            entity_id=step.id,
        ) from exc

    return step.id


async def get_step_row(conn: AsyncPgConnectionProtocol, timeout: float, step_id: str) -> Step | None:
    """Fetch a Step by ID.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        step_id: Canonical stp_<hex> step identifier.

    Returns:
        Hydrated Step instance if found, or None.

    Raises:
        AppException: With VALIDATION_FAILED on invalid ID or STORAGE_ACCESS_FAILED on query error.
    """
    step_uuid = parse_prefixed_uuid7(step_id, EntityPrefix.STEP)
    row = await _fetch_row(conn, timeout, _GET_STEP_SQL, step_uuid, step_id, table_name="steps")
    if row is None:
        return None
    return hydrate_step_row(row)


_DELETE_PROMPT_BLOCK_SQL: str = "DELETE FROM prompt_blocks WHERE id = $1::uuid"
_DELETE_STEP_SQL: str = "DELETE FROM steps WHERE id = $1::uuid"


async def list_prompt_block_rows(conn: AsyncPgConnectionProtocol, timeout: float) -> list[AnyPromptBlock]:
    """List all polymorphic AnyPromptBlock rows from prompt_blocks.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.

    Returns:
        List of hydrated AnyPromptBlock domain models.

    Raises:
        AppException: With VALIDATION_FAILED on corrupt row or STORAGE_ACCESS_FAILED on query error.
    """
    effective_timeout = resolve_effective_timeout(timeout)
    try:
        rows = await conn.fetch(_LIST_PROMPT_BLOCKS_SQL, timeout=effective_timeout)
    except AppException:
        raise
    except Exception as exc:
        raise translate_postgres_exception(
            exc,
            operation="SELECT",
            table_name="prompt_blocks",
            entity_id="*",
        ) from exc
    return [hydrate_prompt_block_row(row) for row in rows]


async def delete_prompt_block_row(
    conn: AsyncPgConnectionProtocol,
    timeout: float,
    block_id: str,
) -> bool:
    """Delete a PromptBlock row by primary key from prompt_blocks.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        block_id: Canonical blk_<hex32> prompt block identifier.

    Returns:
        True if a matching row was deleted, False otherwise.

    Raises:
        AppException: With VALIDATION_FAILED, DELETE_BLOCKED_BY_USAGE, or STORAGE_ACCESS_FAILED.
    """
    block_uuid = parse_prefixed_uuid7(block_id, EntityPrefix.PROMPT_BLOCK)
    return await execute_entity_delete(
        conn,
        timeout,
        _DELETE_PROMPT_BLOCK_SQL,
        block_uuid,
        entity_id=block_id,
        table="prompt_blocks",
    )


async def list_step_rows(conn: AsyncPgConnectionProtocol, timeout: float) -> list[Step]:
    """List all Step rows from steps.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.

    Returns:
        List of hydrated Step domain models.

    Raises:
        AppException: With VALIDATION_FAILED on corrupt row or STORAGE_ACCESS_FAILED on query error.
    """
    effective_timeout = resolve_effective_timeout(timeout)
    try:
        rows = await conn.fetch(_LIST_STEPS_SQL, timeout=effective_timeout)
    except AppException:
        raise
    except Exception as exc:
        raise translate_postgres_exception(
            exc,
            operation="SELECT",
            table_name="steps",
            entity_id="*",
        ) from exc
    return [hydrate_step_row(row) for row in rows]


async def delete_step_row(
    conn: AsyncPgConnectionProtocol,
    timeout: float,
    step_id: str,
) -> bool:
    """Delete a Step row by primary key from steps.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        step_id: Canonical stp_<hex32> step identifier.

    Returns:
        True if a matching row was deleted, False otherwise.

    Raises:
        AppException: With VALIDATION_FAILED, DELETE_BLOCKED_BY_USAGE, or STORAGE_ACCESS_FAILED.
    """
    step_uuid = parse_prefixed_uuid7(step_id, EntityPrefix.STEP)
    return await execute_entity_delete(
        conn,
        timeout,
        _DELETE_STEP_SQL,
        step_uuid,
        entity_id=step_id,
        table="steps",
    )
