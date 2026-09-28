"""Matrix Sensor Prompt Builder.

Constructs structured LLM messages for TDA sensor evaluation, strictly separating
cacheable static system instructions from dynamic per-batch user claims.
"""

import logging

from backend_v2.core.template_processor import TemplateProcessor
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.dtos.dag_models import LinkedAtomGraph
from backend_v2.models.dtos.engine import FlattenedAtom, MatrixEvaluationContext
from backend_v2.models.enums import ExecutionStatus
from backend_v2.models.llm import LLMMessageDTO
from backend_v2.models.prompt import CompiledPrompt
from backend_v2.models.prompts.common import (
    GLOBAL_MANDATES_XML,
    STATIC_LINGUISTIC_PROTOCOL,
    build_linguistic_parameters,
)
from backend_v2.models.prompts.execution import MATRIX_SENSOR_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

__all__ = ["MatrixSensorPromptBuilder"]


class MatrixSensorPromptBuilder:
    """Builder for sensor prompt messages."""

    @staticmethod
    def build_caching_prefix(
        context_text: str,
        matrix_context: MatrixEvaluationContext | None = None,
    ) -> CompiledPrompt:
        """Builds the cacheable prefix containing system instructions and context.

        Args:
            context_text: The source text (e.g. transcript, article).
            matrix_context: Context containing optional framework/evaluation rules.

        Returns:
            CompiledPrompt with static system instructions and source text context.
        """
        # 1. Compile 100% Static System Instructions using Direct TemplateProcessor Assembly
        sections: list[str] = [
            GLOBAL_MANDATES_XML.strip(),
            STATIC_LINGUISTIC_PROTOCOL.strip(),
            MATRIX_SENSOR_SYSTEM_PROMPT.strip(),
        ]

        if matrix_context:
            if matrix_context.matrix_objective and matrix_context.matrix_objective.strip():
                objective_clean = matrix_context.matrix_objective.strip()
                sections.append(
                    TemplateProcessor.render_prompt(t"<matrix_objective>\n{objective_clean}\n</matrix_objective>")
                )

            if matrix_context.theory_grounding and matrix_context.theory_grounding.citation_reference:
                citation_clean = matrix_context.theory_grounding.citation_reference.strip()
                if citation_clean:
                    sections.append(
                        TemplateProcessor.render_prompt(t"<theory_context>\n{citation_clean}\n</theory_context>")
                    )

        system_content = "\n\n".join(sections)
        context_content = TemplateProcessor.render_prompt(t"<context>\n{context_text}\n</context>")

        return CompiledPrompt(
            static_messages=[
                LLMMessageDTO(role="system", content=system_content),
                LLMMessageDTO(role="user", content=context_content),
            ],
            dynamic_messages=[],
        )

    @staticmethod
    def build_compiled_prompt(
        context_text: str,
        nodes: list[LinkedAtomGraph],
        tda_id_to_alias: dict[str, str],
        target_locale: str,
        matrix_context: MatrixEvaluationContext | None = None,
        atom_status_map: dict[str, ExecutionStatus] | None = None,
    ) -> CompiledPrompt:
        """Builds the strictly segregated CompiledPrompt for Matrix Sensor.

        Args:
            context_text: The massive source document text.
            nodes: The batch of LinkedAtomGraph nodes.
            tda_id_to_alias: Mapping of TDA ID to alias.
            target_locale: ISO language code for user-facing output (e.g. 'fi', 'en', 'sv').
            matrix_context: Optional matrix evaluation context for global rules.
            atom_status_map: Optional status map for dependencies.

        Returns:
            A strictly cached CompiledPrompt.

        Raises:
            AppException: Triggered with VALIDATION_FAILED if target_locale is empty,
                nodes are empty, aliases are missing, or an assertion question is empty.
        """
        if not target_locale or not target_locale.strip():
            msg = "target_locale must be a non-empty string."
            logger.error(
                "[MatrixSensorPromptBuilder] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                exc_info=True,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
            raise AppException(
                message=msg,
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        prefix_prompt = MatrixSensorPromptBuilder.build_caching_prefix(context_text, matrix_context)
        system_content = prefix_prompt.static_messages[0].content
        context_content = prefix_prompt.static_messages[1].content

        # 2. Compile Dynamic User Messages using CDATA encapsulation (No Raw XML f-strings)
        claims_xml: list[str] = []
        matrix_assertions_map: dict[str, FlattenedAtom] = {}
        if matrix_context and matrix_context.matrix_assertions:
            matrix_assertions_map = {assertion.atom_id: assertion for assertion in matrix_context.matrix_assertions}

        if not nodes:
            raise AppException(
                message="Cannot build prompt with empty nodes.",
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        for node in nodes:
            tda_id = node.atom.tda_id
            if tda_id not in tda_id_to_alias:
                raise AppException(
                    message=f"Missing alias for tda_id {tda_id}",
                    status_code=400,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )
            alias = tda_id_to_alias[tda_id]
            if matrix_assertions_map:
                if tda_id not in matrix_assertions_map:
                    raise AppException(
                        message=f"Missing matrix assertion for atom '{tda_id}'",
                        status_code=400,
                        details={"error_code": ErrorCodes.VALIDATION_FAILED.value, "tda_id": tda_id},
                    )
                assertion = matrix_assertions_map[tda_id]
            else:
                assertion = None

            if assertion:
                if not assertion.question or not assertion.question.strip():
                    msg = f"Matrix assertion for atom '{tda_id}' has an empty question."
                    logger.error(
                        "[MatrixSensorPromptBuilder] %s: %s",
                        ErrorCodes.VALIDATION_FAILED.name,
                        msg,
                        exc_info=True,
                        extra={"error_code": ErrorCodes.VALIDATION_FAILED.value, "tda_id": tda_id},
                    )
                    raise AppException(
                        message=msg,
                        status_code=400,
                        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                    )

                assertion_parts: list[str] = [
                    TemplateProcessor.render_prompt(t"<question>\n{assertion.question}\n</question>")
                ]

                if assertion.extraction_rule:
                    assertion_parts.append(
                        TemplateProcessor.render_prompt(
                            t"<extraction_rule>\n{assertion.extraction_rule}\n</extraction_rule>"
                        )
                    )

                if assertion.anchor_target:
                    assertion_parts.append(
                        TemplateProcessor.render_prompt(t"<anchor_target>\n{assertion.anchor_target}\n</anchor_target>")
                    )

                if assertion.is_inverse:
                    assertion_parts.append(
                        TemplateProcessor.render_prompt(t"<is_inverse>\n{assertion.is_inverse}\n</is_inverse>")
                    )

                speaker_val = assertion.target_speaker.value
                assertion_parts.append(
                    TemplateProcessor.render_prompt(t"<target_speaker>\n{speaker_val}\n</target_speaker>")
                )

                if assertion.contrastive_example:
                    acc = assertion.contrastive_example.acceptable
                    rej = assertion.contrastive_example.rejected
                    assertion_parts.append(
                        TemplateProcessor.render_prompt(
                            t"<contrastive_grounding>\n"
                            t"<acceptable>\n{acc}\n</acceptable>\n"
                            t"<rejected>\n{rej}\n</rejected>\n"
                            t"</contrastive_grounding>"
                        )
                    )

                if assertion.acceptance_criteria:
                    crit_blocks = [
                        TemplateProcessor.render_prompt(t'<criterion index="{idx + 1}">\n{c.instruction}\n</criterion>')
                        for idx, c in enumerate(assertion.acceptance_criteria)
                    ]
                    crit_str = "\n".join(crit_blocks)
                    assertion_parts.append(
                        TemplateProcessor.render_prompt(
                            t"<acceptance_criteria>\n{crit_str:raw}\n</acceptance_criteria>"
                        )
                    )

                if assertion.anti_patterns:
                    anti_blocks = [
                        TemplateProcessor.render_prompt(
                            t'<anti_pattern index="{idx + 1}">\n{a.pattern}\n</anti_pattern>'
                        )
                        for idx, a in enumerate(assertion.anti_patterns)
                    ]
                    anti_str = "\n".join(anti_blocks)
                    assertion_parts.append(
                        TemplateProcessor.render_prompt(t"<anti_patterns>\n{anti_str:raw}\n</anti_patterns>")
                    )

                if assertion.syntactic_anchors:
                    anchor_blocks = [
                        TemplateProcessor.render_prompt(t"<anchor>\n{a}\n</anchor>")
                        for a in assertion.syntactic_anchors
                    ]
                    anchor_str = "\n".join(anchor_blocks)
                    assertion_parts.append(
                        TemplateProcessor.render_prompt(t"<syntactic_anchors>\n{anchor_str:raw}\n</syntactic_anchors>")
                    )

                content = "\n".join(assertion_parts)
            else:
                claim_val = node.atom.resolved_claim
                content = TemplateProcessor.render_prompt(t"{claim_val}")

            dependencies_xml: list[str] = []
            if node.depends_on:
                for dep in node.depends_on:
                    actual_status = ExecutionStatus.PENDING
                    if atom_status_map and dep.tda_id in atom_status_map:
                        actual_status = atom_status_map[dep.tda_id]

                    dep_alias = tda_id_to_alias[dep.tda_id] if dep.tda_id in tda_id_to_alias else dep.tda_id
                    expected_val = dep.expected_status.value
                    actual_val = actual_status.value
                    reasoning_val = dep.edge_reasoning

                    dep_inner = TemplateProcessor.render_prompt(
                        t"<expected_status>\n{expected_val}\n</expected_status>\n"
                        t"<actual_status>\n{actual_val}\n</actual_status>\n"
                        t"<reasoning>\n{reasoning_val}\n</reasoning>"
                    )
                    dependencies_xml.append(
                        TemplateProcessor.render_prompt(
                            t'<dependency parent_alias="{dep_alias}">\n{dep_inner:raw}\n</dependency>'
                        )
                    )

            if dependencies_xml:
                deps_str = "\n".join(dependencies_xml)
                deps_content = TemplateProcessor.render_prompt(
                    t"<causal_dependencies>\n{deps_str:raw}\n</causal_dependencies>"
                )
                content += f"\n{deps_content}"

            clean_content = content.strip()
            claims_xml.append(
                TemplateProcessor.render_prompt(t'<claim alias="{alias}">\n{clean_content:raw}\n</claim>')
            )

        claims_str = "\n".join(claims_xml)
        exec_params = TemplateProcessor.render_prompt(
            t"<execution_parameters>\n{claims_str:raw}\n</execution_parameters>"
        )
        linguistic_params = build_linguistic_parameters(target_locale=target_locale.strip())
        user_content = f"{linguistic_params}\n\n{exec_params}"

        context_content = TemplateProcessor.render_prompt(t"<context>\n{context_text}\n</context>")

        return CompiledPrompt(
            static_messages=[
                LLMMessageDTO(role="system", content=system_content),
                LLMMessageDTO(role="user", content=context_content),
            ],
            dynamic_messages=[LLMMessageDTO(role="user", content=user_content)],
        )
