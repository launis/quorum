"""Matrix Sensor Prompt Builder.

Constructs structured LLM messages for TDA sensor evaluation, strictly separating
cacheable static system instructions from dynamic per-batch user claims.
"""

import logging

from backend_v2.core.template_processor import TemplateProcessor
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.dtos.dag_models import LinkedAtomGraph
from backend_v2.models.dtos.engine import MatrixEvaluationContext
from backend_v2.models.enums import ExecutionStatus
from backend_v2.models.prompt import CompiledPrompt
from backend_v2.models.prompts.global_mandates import GLOBAL_MANDATES_XML
from backend_v2.models.prompts.matrix_evaluation import MATRIX_SENSOR_SYSTEM_PROMPT

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
            MATRIX_SENSOR_SYSTEM_PROMPT.strip(),
        ]

        if matrix_context:
            if matrix_context.matrix_objective and matrix_context.matrix_objective.strip():
                objective_clean = matrix_context.matrix_objective.strip()
                sections.append(
                    TemplateProcessor.safe_interpolate(
                        "<matrix_objective>\n{o}\n</matrix_objective>",
                        o=objective_clean,
                    )
                )

            if matrix_context.theory_grounding and matrix_context.theory_grounding.citation_reference:
                citation_clean = matrix_context.theory_grounding.citation_reference.strip()
                if citation_clean:
                    sections.append(
                        TemplateProcessor.safe_interpolate(
                            "<theory_context>\n{c}\n</theory_context>",
                            c=citation_clean,
                        )
                    )

        system_content = "\n\n".join(sections)
        context_content = TemplateProcessor.safe_interpolate("<context>\n{c}\n</context>", c=context_text)

        return CompiledPrompt(
            static_messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": context_content},
            ],
            dynamic_messages=[],
        )

    @staticmethod
    def build_compiled_prompt(
        context_text: str,
        nodes: list[LinkedAtomGraph],
        tda_id_to_alias: dict[str, str],
        matrix_context: MatrixEvaluationContext | None = None,
        atom_status_map: dict[str, ExecutionStatus] | None = None,
    ) -> CompiledPrompt:
        """Builds the strictly segregated CompiledPrompt for Matrix Sensor.

        Args:
            context_text: The massive source document text.
            nodes: The batch of LinkedAtomGraph nodes.
            tda_id_to_alias: Mapping of TDA ID to alias.
            matrix_context: Optional matrix evaluation context for global rules.
            atom_status_map: Optional status map for dependencies.

        Returns:
            A strictly cached CompiledPrompt.

        Raises:
            AppException: Triggered with VALIDATION_FAILED if nodes are empty, aliases are missing,
                or an assertion question is empty.
        """
        prefix_prompt = MatrixSensorPromptBuilder.build_caching_prefix(context_text, matrix_context)
        system_content = prefix_prompt.static_messages[0]["content"]
        context_content = prefix_prompt.static_messages[1]["content"]

        # 2. Compile Dynamic User Messages using CDATA encapsulation (No Raw XML f-strings)
        claims_xml: list[str] = []
        matrix_assertions_map = {}
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
            assertion = matrix_assertions_map.get(tda_id)

            if assertion:
                if not assertion.question or not assertion.question.strip():
                    msg = f"Matrix assertion for atom '{tda_id}' has an empty question."
                    logger.error(
                        "[MatrixSensorPromptBuilder] %s: %s",
                        ErrorCodes.VALIDATION_FAILED.name,
                        msg,
                        extra={"error_code": ErrorCodes.VALIDATION_FAILED.value, "tda_id": tda_id},
                    )
                    raise AppException(
                        message=msg,
                        status_code=400,
                        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                    )

                q_cdata = TemplateProcessor.encapsulate_payload(assertion.question)
                content = f"<question>\n{q_cdata}\n</question>\n"

                if assertion.extraction_rule:
                    r_cdata = TemplateProcessor.encapsulate_payload(assertion.extraction_rule)
                    content += f"<extraction_rule>\n{r_cdata}\n</extraction_rule>\n"

                if assertion.anchor_target:
                    a_cdata = TemplateProcessor.encapsulate_payload(assertion.anchor_target)
                    content += f"<anchor_target>\n{a_cdata}\n</anchor_target>\n"

                if assertion.is_inverse:
                    i_cdata = TemplateProcessor.encapsulate_payload(str(assertion.is_inverse))
                    content += f"<is_inverse>\n{i_cdata}\n</is_inverse>\n"
            else:
                claim_cdata = TemplateProcessor.encapsulate_payload(node.atom.resolved_claim)
                content = f"{claim_cdata}\n"

            dependencies_xml = []
            if node.depends_on:
                for dep in node.depends_on:
                    actual_status = ExecutionStatus.PENDING
                    if atom_status_map and dep.tda_id in atom_status_map:
                        actual_status = atom_status_map[dep.tda_id]

                    dep_alias = tda_id_to_alias[dep.tda_id] if dep.tda_id in tda_id_to_alias else dep.tda_id

                    status_cdata = TemplateProcessor.encapsulate_payload(actual_status.value)
                    expected_cdata = TemplateProcessor.encapsulate_payload(dep.expected_status.value)
                    reasoning_cdata = TemplateProcessor.encapsulate_payload(dep.edge_reasoning)

                    dep_content = (
                        f"<expected_status>\n{expected_cdata}\n</expected_status>\n"
                        f"<actual_status>\n{status_cdata}\n</actual_status>\n"
                        f"<reasoning>\n{reasoning_cdata}\n</reasoning>\n"
                    )
                    dependencies_xml.append(
                        f'<dependency parent_alias="{dep_alias}">\n{dep_content.strip()}\n</dependency>'
                    )

            if dependencies_xml:
                deps_str = "\n".join(dependencies_xml)
                deps_content = TemplateProcessor.safe_interpolate(
                    "<causal_dependencies>\n{c}\n</causal_dependencies>", c=deps_str
                )
                content += f"\n{deps_content}"

            claims_xml.append(f'<claim alias="{alias}">\n{content.strip()}\n</claim>')

        claims_str = "\n".join(claims_xml)
        user_content = TemplateProcessor.safe_interpolate(
            "<execution_parameters>\n{c}\n</execution_parameters>", c=claims_str
        )

        # 3. Assemble CompiledPrompt properly (Context text in static user message!)
        context_content = TemplateProcessor.safe_interpolate("<context>\n{c}\n</context>", c=context_text)

        return CompiledPrompt(
            static_messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": context_content},
            ],
            dynamic_messages=[{"role": "user", "content": user_content}],
        )
