"""Modular LLM synthesis task builders for Quorum report generation.

Decomposed from worker monolith to satisfy God Code Prevention limits (<500 lines).
"""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from typing import Any

from backend_v2.database.repository import UnifiedWorkflowRepository
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.llm.client import LLMClient
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.dtos.synthesis import (
    ExecutiveSummarySectionResult,
    MatrixExplanationContextDTO,
    MatrixExplanationContextList,
    MatrixExplanationsResult,
    MatrixSectionSynthesesResult,
    XaiHighlightsResult,
)
from backend_v2.models.enums import (
    CognitiveTier,
    PresetView,
)
from backend_v2.models.prompts import (
    EXECUTIVE_SUMMARY_SECTION_ID,
    EXECUTIVE_SUMMARY_SECTION_RULES_PREFIX,
    ROW_EXPLANATION_SYSTEM_PROMPT,
    SECTION_SYNTHESIS_DIRECTIVE_BLOCK,
    STATIC_LINGUISTIC_PROTOCOL,
    SYNTHESIS_SECTION_RULES_PREFIX,
    SYNTHESIS_XAI_CURATION,
    build_linguistic_parameters,
)
from backend_v2.workers.variance_synthesis import (
    VarianceExplanationResult as VarianceExplanationResult,
)
from backend_v2.workers.variance_synthesis import (
    build_variance_metrics_and_task as build_variance_metrics_and_task,
)

__all__ = [
    "VarianceExplanationResult",
    "build_variance_metrics_and_task",
    "create_executive_summary_task",
    "create_matrix_sections_tasks",
    "create_row_explanations_task",
    "create_xai_highlights_task",
]

logger = logging.getLogger(__name__)


async def create_executive_summary_task(
    client: LLMClient,
    sys_prompt: str,
    base_dynamic_parts: list[str],
    distilled_inputs: str,
    matrix_context: str,
    active_profile_dto: OutputProfile | None,
    sem_runner: Callable[[Awaitable[Any]], Awaitable[Any]],
) -> Any | None:
    """Build and execute the executive summary structured LLM task."""
    if active_profile_dto is not None and not active_profile_dto.requires_executive_synthesis:
        return None

    exec_directive: str | None = None
    if active_profile_dto:
        if (
            not active_profile_dto.executive_summary_directive
            or not active_profile_dto.executive_summary_directive.strip()
        ):
            logger.warning(
                "[synthesis_tasks] OutputProfile '%s' is missing executive_summary_directive. "
                "Skipping Executive Summary synthesis.",
                active_profile_dto.id,
            )
            return None
        exec_directive = active_profile_dto.executive_summary_directive.strip()

    if not exec_directive:
        logger.warning("[synthesis_tasks] No executive_summary_directive configured. Skipping Executive Summary.")
        return None

    exec_dynamic_parts = list(base_dynamic_parts)
    if active_profile_dto and active_profile_dto.synthesis_length_constraint:
        exec_dynamic_parts.append(f"<section_budget>{active_profile_dto.synthesis_length_constraint}</section_budget>")
    exec_section_rule = (
        f"{EXECUTIVE_SUMMARY_SECTION_RULES_PREFIX}\n"
        f'<section_instruction id="{EXECUTIVE_SUMMARY_SECTION_ID}" title="Executive Summary">\n'
        f"{exec_directive}\n"
        "</section_instruction>\n"
    )
    exec_dynamic_parts.append(exec_section_rule)
    exec_dynamic_context = "\n\n".join(exec_dynamic_parts)

    exec_messages: list[dict[str, Any]] = [
        {"role": "system", "content": sys_prompt},
        {
            "role": "user",
            "content": (
                f"<dynamic_context>\n{exec_dynamic_context}\n</dynamic_context>"
                f"\n\nDATA TO SYNTHESIZE:\n{distilled_inputs}{matrix_context}"
            ),
        },
    ]
    return await sem_runner(
        client.run_structured_task(
            messages=exec_messages,
            response_model=ExecutiveSummarySectionResult,
            mock_identity="ExecutiveSummaryTask",
        )
    )


async def create_matrix_sections_tasks(
    client: LLMClient,
    sys_prompt: str,
    base_dynamic_parts: list[str],
    distilled_inputs: str,
    matrix_context: str,
    active_profile_dto: OutputProfile | None,
    distilled_data: dict[str, Any],
    sem_runner: Callable[[Awaitable[Any]], Awaitable[Any]],
) -> list[tuple[str, Any]]:
    """Build and execute matrix synthesis group structured tasks."""
    if not active_profile_dto or not active_profile_dto.requires_group_synthesis:
        return []

    language = distilled_data["language"] if "language" in distilled_data else "en"
    title_map: dict[str, str] = distilled_data["title_map"] if "title_map" in distilled_data else {}
    tasks_results: list[tuple[str, Any]] = []

    for grp in active_profile_dto.matrix_synthesis_groups:
        grp_id = grp.id
        grp_title = grp.title.resolve(language) if grp.title else grp_id

        directive_content = None
        match grp.view_type:
            case PresetView.METRICS_1D | "1d_metrics":
                directive_content = active_profile_dto.matrix_1d_synthesis_directive
            case PresetView.COMPARE_2D | "2d_compare":
                directive_content = active_profile_dto.matrix_2d_synthesis_directive
            case PresetView.MATRIX_3D | "3d_matrix":
                directive_content = active_profile_dto.matrix_3d_synthesis_directive
            case PresetView.TEXT_ONLY | "text_only":
                directive_content = active_profile_dto.matrix_text_synthesis_directive
            case _:
                directive_content = None

        if not directive_content or not directive_content.strip():
            logger.warning(
                "[synthesis_tasks] OutputProfile '%s' is missing matrix synthesis directive for "
                "view_type '%s' (group '%s').",
                active_profile_dto.id,
                grp.view_type,
                grp_id,
            )
            continue
        directive_content = directive_content.strip()

        target_titles = []
        if grp.target_blocks:
            for tb in grp.target_blocks:
                if tb.lower() in title_map:
                    target_titles.append(title_map[tb.lower()])
        target_str = f' targets="{", ".join(target_titles)}"' if target_titles else ""

        grp_dynamic_parts = list(base_dynamic_parts)
        if active_profile_dto.matrix_graph_length_constraint:
            grp_dynamic_parts.append(
                f"<section_budget>{active_profile_dto.matrix_graph_length_constraint}</section_budget>"
            )
        grp_section_rule = (
            f'{SYNTHESIS_SECTION_RULES_PREFIX}\n<section_instruction id="{grp_id}" title="{grp_title}"{target_str}>\n'
            f"{directive_content}\n"
            f"</section_instruction>\n\n{SECTION_SYNTHESIS_DIRECTIVE_BLOCK}"
        )
        grp_dynamic_parts.append(grp_section_rule)
        grp_dynamic_context = "\n\n".join(grp_dynamic_parts)

        grp_messages: list[dict[str, Any]] = [
            {"role": "system", "content": sys_prompt},
            {
                "role": "user",
                "content": (
                    f"<dynamic_context>\n{grp_dynamic_context}\n</dynamic_context>"
                    f"\n\nDATA TO SYNTHESIZE:\n{distilled_inputs}{matrix_context}"
                ),
            },
        ]
        res = await sem_runner(
            client.run_structured_task(
                messages=grp_messages,
                response_model=MatrixSectionSynthesesResult,
                mock_identity=f"MatrixSectionTask_{grp_id}",
            )
        )
        tasks_results.append((grp_id, res))

    return tasks_results


async def create_xai_highlights_task(
    client: LLMClient,
    sys_prompt: str,
    base_dynamic_parts: list[str],
    distilled_inputs: str,
    matrix_context: str,
    active_profile_dto: OutputProfile | None,
    sem_runner: Callable[[Awaitable[Any]], Awaitable[Any]],
) -> Any | None:
    """Build and execute the XAI highlights structured task."""
    if not active_profile_dto or not (
        active_profile_dto.visible_block_extensions or active_profile_dto.visible_workflow_extensions
    ):
        return None

    max_ext = active_profile_dto.max_extension_items
    if max_ext is None:
        raise AppException(
            message="Fail-Fast: max_extension_items is mandatory if extensions are visible.",
            status_code=400,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )
    wf_exts: list[Any] = []
    if active_profile_dto.visible_workflow_extensions:
        wf_exts.extend(active_profile_dto.visible_workflow_extensions)
    if active_profile_dto.visible_block_extensions:
        wf_exts.extend(active_profile_dto.visible_block_extensions)
    wf_exts = list(dict.fromkeys(wf_exts))
    req_exts = ", ".join(str(e) for e in wf_exts) if wf_exts else "none"

    if not active_profile_dto.xai_synthesis_directive or not active_profile_dto.xai_synthesis_directive.strip():
        logger.warning(
            "[synthesis_tasks] OutputProfile '%s' is missing xai_synthesis_directive. Skipping XAI highlights.",
            active_profile_dto.id,
        )
        return None

    xai_directive_str = active_profile_dto.xai_synthesis_directive.strip()
    curation_prompt = SYNTHESIS_XAI_CURATION.replace("<max_extension_items>", str(max_ext)).replace(
        "<requested_extensions>", req_exts
    )
    xai_cur = f"{xai_directive_str}\n\n{curation_prompt}"

    xai_dynamic_parts = list(base_dynamic_parts)
    if active_profile_dto.xai_length_constraint:
        xai_dynamic_parts.append(f"<section_budget>{active_profile_dto.xai_length_constraint}</section_budget>")
    xai_dynamic_parts.append(xai_cur)
    xai_dynamic_context = "\n\n".join(xai_dynamic_parts)

    xai_messages: list[dict[str, Any]] = [
        {"role": "system", "content": sys_prompt},
        {
            "role": "user",
            "content": (
                f"<dynamic_context>\n{xai_dynamic_context}\n</dynamic_context>"
                f"\n\nDATA TO SYNTHESIZE:\n{distilled_inputs}{matrix_context}"
            ),
        },
    ]
    return await sem_runner(
        client.run_structured_task(
            messages=xai_messages,
            response_model=XaiHighlightsResult,
            mock_identity="XaiHighlightsTask",
        )
    )


async def create_row_explanations_task(
    repo: UnifiedWorkflowRepository,
    matrices_to_explain: list[MatrixExplanationContextDTO],
    active_profile_dto: OutputProfile | None,
    accept_language: str,
    execution: ExecutionRecord,
    workflow_registry_id: str | None,
    sem_runner: Callable[[Awaitable[Any]], Awaitable[Any]],
) -> Any | None:
    """Build and execute row explanations structured task using FAST cognitive tier."""
    if not matrices_to_explain or (active_profile_dto is not None and not active_profile_dto.requires_row_explanations):
        return None

    row_provider_override = execution.metadata.provider_override if execution.metadata else None
    row_reg_id = execution.metadata.model_registry_id if execution.metadata else None
    if not row_reg_id:
        row_reg_id = workflow_registry_id

    client = await LLMClient.from_tier(
        CognitiveTier.FAST,
        repository=repo,
        provider=row_provider_override,
        registry_id=row_reg_id,
    )
    row_sys_prompt = f"{ROW_EXPLANATION_SYSTEM_PROMPT}\n\n{STATIC_LINGUISTIC_PROTOCOL}"
    row_lang_params = build_linguistic_parameters(source_language="Unknown", target_locale=accept_language)

    row_directive_str = None
    if active_profile_dto:
        if active_profile_dto.row_explanation_directive and active_profile_dto.row_explanation_directive.strip():
            row_directive_str = active_profile_dto.row_explanation_directive.strip()
        else:
            logger.warning(
                "[synthesis_tasks] OutputProfile '%s' is missing row_explanation_directive. Skipping row explanations.",
                active_profile_dto.id,
            )
    else:
        logger.warning("[synthesis_tasks] No active OutputProfile for row explanation synthesis.")

    if not row_directive_str:
        return None

    row_dynamic_parts = [row_lang_params]
    if active_profile_dto and active_profile_dto.tone_instruction:
        tone = active_profile_dto.tone_instruction.strip()
        if tone:
            row_dynamic_parts.append(f"<tone_instruction>{tone}</tone_instruction>")
    row_dynamic_parts.append(row_directive_str)
    if active_profile_dto and active_profile_dto.row_explanation_length_constraint:
        row_dynamic_parts.append(
            f"<section_budget>{active_profile_dto.row_explanation_length_constraint}</section_budget>"
        )
    row_dynamic_ctx = "\n\n".join(row_dynamic_parts)

    matrices_json = (
        MatrixExplanationContextList.dump_json(matrices_to_explain, indent=2, exclude_none=True).decode("utf-8")
        if matrices_to_explain
        else ""
    )
    row_user_content = (
        f"<dynamic_context>\n{row_dynamic_ctx}\n</dynamic_context>\n\nMATRICES TO EXPLAIN:\n{matrices_json}"
    )
    row_messages: list[dict[str, Any]] = [
        {"role": "system", "content": row_sys_prompt},
        {
            "role": "user",
            "content": row_user_content,
        },
    ]
    return await sem_runner(
        client.run_structured_task(
            messages=row_messages,
            response_model=MatrixExplanationsResult,
            mock_identity="row_explainer",
        )
    )
