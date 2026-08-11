"""Matrix Sensor Prompt Builder.

Constructs structured LLM messages for TDA sensor evaluation, strictly separating
cacheable static system instructions from dynamic per-batch user claims.
"""

from backend_v2.core.template_processor import TemplateProcessor
from backend_v2.models.dtos.dag_models import LinkedAtomGraph
from backend_v2.models.dtos.engine import MatrixEvaluationContext
from backend_v2.models.enums import BlockDataType, PromptBlockCategory
from backend_v2.models.prompt import CompiledPrompt
from backend_v2.models.prompts.matrix_evaluation import MATRIX_SENSOR_SYSTEM_PROMPT
from backend_v2.models.v2_core import I18nText, PromptBlock
from backend_v2.services.orchestrator.prompt_compiler_adapter import PromptCompilerAdapter


class MatrixSensorPromptBuilder:
    """Builder for sensor prompt messages."""

    @staticmethod
    def _create_ephemeral_block(block_id: str, category_id: PromptBlockCategory, ai_desc: str) -> PromptBlock:
        """Helper to create a valid PromptBlock for in-memory compilation."""
        return PromptBlock(
            id=block_id,
            slug=block_id,
            organization_id="system",
            label=I18nText(default_locale="en", translations={"en": block_id}),
            description=I18nText(default_locale="en", translations={"en": block_id}),
            ai_description=ai_desc,
            category_id=category_id,
            type=BlockDataType.INSTRUCTION,
            output_extensions=[],
        )

    @staticmethod
    def build_caching_prefix(
        context_text: str,
        matrix_context: MatrixEvaluationContext | None = None,
    ) -> CompiledPrompt:
        """Builds a strictly static CompiledPrompt for pre-caching.

        Args:
            context_text: The massive source document text.
            matrix_context: Optional matrix evaluation context for global rules.

        Returns:
            A CompiledPrompt with empty dynamic messages, ready for Context Cache upload.
        """
        # 1. Compile 100% Static System Instructions using PromptBlock Assembly
        blocks = [
            MatrixSensorPromptBuilder._create_ephemeral_block(
                block_id="blk_1111111111111111",
                category_id=PromptBlockCategory.SYSTEM_RULE,
                ai_desc=MATRIX_SENSOR_SYSTEM_PROMPT,
            )
        ]

        if matrix_context:
            if matrix_context.matrix_objective:
                blocks.append(
                    MatrixSensorPromptBuilder._create_ephemeral_block(
                        block_id="blk_2222222222222222",
                        category_id=PromptBlockCategory.SYSTEM_RULE,
                        ai_desc=matrix_context.matrix_objective,
                    )
                )
            if matrix_context.theory_grounding:
                blocks.append(
                    MatrixSensorPromptBuilder._create_ephemeral_block(
                        block_id="blk_3333333333333333",
                        category_id=PromptBlockCategory.SYSTEM_RULE,
                        ai_desc=matrix_context.theory_grounding.model_dump_json(),
                    )
                )

        compiler = PromptCompilerAdapter()
        system_content = compiler.compile_static_instructions(blocks, target_locale="en")

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
    ) -> CompiledPrompt:
        """Builds the strictly segregated CompiledPrompt for Matrix Sensor.

        Args:
            context_text: The massive source document text.
            nodes: The batch of LinkedAtomGraph nodes.
            tda_id_to_alias: Mapping of TDA ID to alias.
            matrix_context: Optional matrix evaluation context for global rules.

        Returns:
            A strictly cached CompiledPrompt.
        """
        prefix_prompt = MatrixSensorPromptBuilder.build_caching_prefix(context_text, matrix_context)
        system_content = prefix_prompt.static_messages[0]["content"]
        context_content = prefix_prompt.static_messages[1]["content"]

        # 2. Compile Dynamic User Messages using CDATA encapsulation (No Raw XML f-strings)
        claims_xml: list[str] = []
        matrix_assertions_map = {}
        if matrix_context and matrix_context.matrix_assertions:
            matrix_assertions_map = {assertion.atom_id: assertion for assertion in matrix_context.matrix_assertions}

        for node in nodes:
            tda_id = node.atom.tda_id
            alias = tda_id_to_alias.get(tda_id, tda_id)
            assertion = matrix_assertions_map.get(tda_id)

            if assertion:
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
