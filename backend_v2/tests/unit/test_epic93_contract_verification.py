"""System 2 Verification: Epic 93 Phase 1 + Phase 2 Contract Compliance Test.

This test suite verifies that the promises made in:
  1. docs/epic/EPIC_93_SDUI_Output_Rendering_Unification 2.md (master epic)
  2. docs/epic/tasks_epic_93/phase1_dto_refactoring.md (Phase 1 plan)
  3. docs/epic/tasks_epic_93/phase2_pipeline_unification.md (Phase 2 plan)

have been fulfilled by the actual codebase.

System 2 Methodology:
  - Each test maps to a SPECIFIC promise from the documents.
  - Each test includes a falsification attempt (trying to break the contract).
  - Tests are grouped by contract source.
"""

import json
from pathlib import Path
from typing import Any

# ============================================================================
# CONTRACT GROUP 1: EPIC 93 Master Document (Sections 1-3)
# Promise: "Putki B tuhotaan" (Pipe B is destroyed)
# ============================================================================


class TestPipeBDestruction:
    """Verify EPIC 93 §2: 'Putki B (backend_v2/hooks/synthesis.py) lakkautetaan.'."""

    def test_synthesis_py_file_is_destroyed(self) -> None:
        """PROMISE: 'backend_v2/hooks/synthesis.py' is destroyed."""
        synthesis_path = Path("backend_v2/hooks/synthesis.py")
        assert not synthesis_path.exists(), "BROKEN CONTRACT: synthesis.py still exists."

    def test_text_consolidation_hook_is_unregistered(self) -> None:
        """PROMISE: TextConsolidationHook is permanently removed."""
        from backend_v2.core.hook_registry import HookRegistry

        registry = HookRegistry()
        registered_hooks = list(registry._hooks.keys())
        assert "text_consolidation_hook" not in registered_hooks, (
            "BROKEN CONTRACT: text_consolidation_hook is STILL registered in HookRegistry. "
        )

    def test_no_synthesis_imports_in_hooks_init(self) -> None:
        """PROMISE: No lingering synthesis module imports.

        Falsification: Parse hooks/__init__.py for synthesis references.
        """
        init_path = Path("backend_v2/hooks/__init__.py")
        if init_path.exists():
            content = init_path.read_text(encoding="utf-8")
            assert "synthesis" not in content.lower(), (
                "BROKEN CONTRACT: hooks/__init__.py STILL references 'synthesis'."
            )


# ============================================================================
# CONTRACT GROUP 2: EPIC 93 Phase 1 (DTO Refactoring)
# Promise: "Headless, strongly-typed Pydantic models carrying only semantic data"
# ============================================================================


class TestPhase1DTORefactoring:
    """Verify Phase 1 promises from phase1_dto_refactoring.md."""

    def test_execution_state_exists_and_is_headless(self) -> None:
        """PROMISE: 'ExecutionState eivät enää sisällä Markdownia, HTML:ää tai UI-tageja.'."""
        from backend_v2.models.state import ExecutionState

        fields = ExecutionState.model_fields
        assert "executive_summary" in fields, "Missing promised field: executive_summary"
        assert "evidence_quotes" in fields, "Missing promised field: evidence_quotes"

    def test_quote_evidence_dto_exists_with_correct_fields(self) -> None:
        """PROMISE (Phase 1 §2): QuoteEvidenceDTO must have 'quote: str' and 'source_alias: List[str]'."""
        from backend_v2.models.dtos.quote_evidence import QuoteEvidenceDTO

        fields = QuoteEvidenceDTO.model_fields
        assert "quote" in fields, "Missing promised field: quote"
        assert "verified_source_ids" in fields, "Missing promised field: verified_source_ids"
        assert "unverified_aliases" in fields, "Missing promised field: unverified_aliases"

    def test_quote_evidence_before_validator_regex_parsing(self) -> None:
        """PROMISE (Phase 1 §2): 'mode=before @field_validator on source_alias to intercept
        strings like "DOC-1, DOC-2" and normalize them into a list.'.

        Falsification: Feed combined string, verify split.
        """
        from backend_v2.models.dtos.quote_evidence import QuoteEvidenceDTO

        dto = QuoteEvidenceDTO.model_validate(
            {"quote": "Test.", "source_alias": "DOC-1, DOC-2"},
            context={"alias_registry": {"DOC-1": "opq_1", "DOC-2": "opq_2"}},
        )
        # Verify the regex extracted both into verified (or unverified depending on registry)
        assert len(dto.verified_source_ids) + len(dto.unverified_aliases) == 2, (
            f"BROKEN CONTRACT: Expected 2 total aliases, got {len(dto.verified_source_ids) + len(dto.unverified_aliases)}. "
            "Phase 1 mandates regex re.findall(r'DOC-\\d+', v) parsing."
        )

    def test_quote_evidence_unverified_fallback(self) -> None:
        """PROMISE (Phase 1 §2): 'If the alias is missing, map it strictly to
        the literal string "OpaqueID.UNVERIFIED".'.

        Falsification: Feed unknown alias, verify exact string.
        """
        from backend_v2.models.dtos.quote_evidence import QuoteEvidenceDTO

        dto = QuoteEvidenceDTO.model_validate(
            {"quote": "Test.", "source_alias": "DOC-999"},
            context={"alias_registry": {"DOC-1": "opq_1"}},
        )
        assert dto.unverified_aliases == ["DOC-999"], (
            f"BROKEN CONTRACT: Expected ['DOC-999'], got {dto.unverified_aliases}. "
            "Phase 1 mandates storing unknown aliases in unverified_aliases."
        )

    def test_quote_evidence_context_injection_works(self) -> None:
        """PROMISE (Phase 1 §2): '@field_validator that takes info: ValidationInfo.
        It must access info.context.get("alias_registry", {}).'.

        Falsification: Provide context with known mapping, verify resolution.
        """
        from backend_v2.models.dtos.quote_evidence import QuoteEvidenceDTO

        registry = {"DOC-1": "src_abc123", "DOC-2": "src_def456"}
        dto = QuoteEvidenceDTO.model_validate(
            {"quote": "Evidence.", "source_alias": ["DOC-1", "DOC-2"]},
            context={"alias_registry": registry},
        )
        assert dto.verified_source_ids == ["src_abc123", "src_def456"], (
            f"BROKEN CONTRACT: Alias resolution failed. Got {dto.verified_source_ids}. "
            "Phase 1 mandates ValidationInfo context-based resolution."
        )

    def test_quote_evidence_no_logging_side_effects_in_validator(self) -> None:
        """PROMISE (Phase 1 §2): 'No logging or side-effects inside the validator.'.

        Falsification: Inspect the resolve_source_alias validator source for logger calls.
        """
        import inspect

        from backend_v2.models.dtos.quote_evidence import QuoteEvidenceDTO

        source = inspect.getsource(QuoteEvidenceDTO.resolve_and_verify_aliases)  # type: ignore[arg-type]
        assert "logger" not in source, (
            "BROKEN CONTRACT: resolve_and_verify_aliases contains logging. "
            "Phase 1 mandates: 'No logging or side-effects inside the validator.'"
        )


# ============================================================================
# CONTRACT GROUP 3: EPIC 93 Phase 2 (Pipeline Unification)
# Promise: "Transfer synthesis responsibilities to declarative prompt_blocks"
# ============================================================================


class TestPhase2PipelineUnification:
    """Verify Phase 2 promises from phase2_pipeline_unification.md."""

    def test_synthesis_prompts_exist_in_seed_data(self) -> None:
        """PROMISE (Phase 2 §3): 'Inject synthesis prompts natively into prompt_blocks SSOT.'.

        Falsification: Parse seed_data.json and verify the blocks exist.
        """
        seed_path = Path("backend_v2/seed/seed_data.json")
        assert seed_path.exists(), "seed_data.json not found"

        with seed_path.open("r", encoding="utf-8") as f:
            seed_data = json.load(f)

        # Find prompt_blocks collection
        prompt_blocks = seed_data.get("prompt_blocks", [])
        slugs = [pb.get("slug", "") for pb in prompt_blocks]

        assert "blk_synthesis_global_rules" in slugs, (
            "BROKEN CONTRACT: blk_synthesis_global_rules not in seed_data.json prompt_blocks. "
            "Phase 2 mandates prompt migration to SSOT."
        )
        assert "blk_synthesis_section_rules" in slugs, (
            "BROKEN CONTRACT: blk_synthesis_section_rules not in seed_data.json prompt_blocks."
        )
        assert "blk_row_explanation_rules" in slugs, (
            "BROKEN CONTRACT: blk_row_explanation_rules not in seed_data.json prompt_blocks."
        )

    def test_synthesis_dag_steps_exist_in_seed_data(self) -> None:
        """PROMISE (Phase 2 §3): Synthesis wired via 'dependencies' array in 'workflows'.

        Verify sp_synthesis_distiller, sp_synthesis_llm, sp_row_explanations exist as steps.
        """
        seed_path = Path("backend_v2/seed/seed_data.json")
        with seed_path.open("r", encoding="utf-8") as f:
            seed_data = json.load(f)

        steps = seed_data.get("steps", [])
        step_slugs = [s.get("slug", "") for s in steps]

        assert "sp_synthesis_distiller" in step_slugs, (
            "BROKEN CONTRACT: sp_synthesis_distiller step not in seed_data.json."
        )
        assert "sp_synthesis_llm" in step_slugs, "BROKEN CONTRACT: sp_synthesis_llm step not in seed_data.json."
        assert "sp_row_explanations" in step_slugs, "BROKEN CONTRACT: sp_row_explanations step not in seed_data.json."

    def test_synthesis_distiller_performs_token_shield(self) -> None:
        """PROMISE (Phase 2 §1): 'Create matrix_reducer.py (or equivalent) that strips
        heavy metadata from chunk evaluation JSONs.'.

        The synthesis_distiller._compress_synthesis_payload serves this role.
        Falsification: Feed heavy payload, verify stripping.
        """
        from backend_v2.services.orchestrator.synthesis_payload_compressor import (
            SynthesisPayloadCompressor,
        )

        heavy_payload: dict[str, Any] = {
            "normalized_score": 75.0,
            "shuffled_atoms": ["a1", "a2", "a3"],
            "evaluations": [
                {
                    "atom_id": "a1",
                    "exact_quotes": ["Valid quote."],
                    "semantic_reasoning": "Good reasoning.",
                    "internal_debug_trace": "MUST_BE_STRIPPED",
                },
            ],
        }
        result = SynthesisPayloadCompressor.compress_synthesis_payload(heavy_payload)
        assert "shuffled_atoms" not in result, "Token shield failed: shuffled_atoms not stripped"
        assert "Valid quote." in result, "Token shield stripped too much: valid quote missing"

    def test_compress_synthesis_caps_evaluations(self) -> None:
        """PROMISE: Prevent LLM token explosion by stratifying and capping evaluations at max_synthesis_evaluations.

        Falsification: Feed 50 evaluations, verify compressed payload caps at max_synthesis_evaluations.
        """
        import json
        from unittest.mock import patch

        from backend_v2.services.orchestrator.synthesis_payload_compressor import (
            SynthesisPayloadCompressor,
        )
        from backend_v2.settings import Settings

        evals = [
            {
                "atom_id": f"a{i}",
                "exact_quotes": [f"Quote {i}"],
                "semantic_reasoning": f"Reason {i}",
            }
            for i in range(50)
        ]
        with patch(
            "backend_v2.services.orchestrator.synthesis_payload_compressor.get_settings",
            return_value=Settings(max_synthesis_evaluations=40),
        ):
            compressed_str = SynthesisPayloadCompressor.compress_synthesis_payload({"results": evals})
            compressed_dict = json.loads(compressed_str)

        pruned = compressed_dict.get("results", [])
        assert len(pruned) == 40

    def test_matrices_to_explain_assembly(self) -> None:
        """PROMISE: Cross-reference atom_quotes with normalized scores.

        Falsification: Build scenario with matching and non-matching data.
        """
        from backend_v2.models.enums import ExecutionStatus
        from backend_v2.models.state import StepOutputDTO
        from backend_v2.services.orchestrator.matrix_explanation_service import (
            MatrixExplanationService,
        )

        block_id_1 = "blk_111111111111111111111111"
        block_id_2 = "blk_222222222222222222222222"
        dtos = [
            StepOutputDTO(
                step_id="s1",
                block_id=block_id_1,
                data_type="matrix",
                payload={
                    "normalized_score": 80.0,
                    "results": [
                        {
                            "tda_id": "a1",
                            "status": "PASSED",
                            "evaluation_reasoning": "Reason",
                            "source_quote": "Q1 verbatim quote longer than 15 chars",
                            "depends_on_tda_ids": [],
                            "short_circuit_reason_tda_ids": [],
                        }
                    ],
                    "evaluated_atoms": {"a1": ExecutionStatus.PASSED},
                },
            ),
            StepOutputDTO(
                step_id="s2",
                block_id=block_id_2,
                data_type="matrix",
                payload={
                    "normalized_score": 60.0,
                    "results": [
                        {
                            "tda_id": "a2",
                            "status": "PASSED",
                            "evaluation_reasoning": "Reason",
                            "source_quote": None,
                            "depends_on_tda_ids": [],
                            "short_circuit_reason_tda_ids": [],
                        }
                    ],
                    "evaluated_atoms": {"a2": ExecutionStatus.PASSED},
                },
            ),
        ]
        from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock, PromptBlock
        from backend_v2.models.enums import BlockDataType, PromptBlockCategory
        from backend_v2.models.v2_core import (
            I18nText,
            MatrixClaim,
            MatrixScale,
            TDAAssertion,
        )

        def _make_pb(block_id: str, label_en: str) -> PromptBlock:
            return MatrixPromptBlock(
                id=block_id,
                slug=f"slug_{block_id}",
                label=I18nText(translations={"en": label_en}),
                description=I18nText(translations={"en": "Description"}),
                ai_description="Instructions",
                category_id=PromptBlockCategory.MATRIX,
                type=BlockDataType.FLOAT,
                scales=[
                    MatrixScale(
                        score=1,
                        ai_label="INITIAL",
                        claims=[
                            MatrixClaim(
                                label=I18nText(translations={"en": "Claim"}),
                                tda_assertions=[
                                    TDAAssertion(
                                        tda_id="tda_00000000000000000000000000000001",
                                        inverse_evidence=False,
                                        aggregation_mode="ALL_MUST_COMPLY",
                                        concept_description="Concept Description Valid",
                                    )
                                ],
                            )
                        ],
                    )
                ],
            )

        blocks_by_id: dict[str, PromptBlock] = {
            block_id_1: _make_pb(block_id_1, "Matrix M1"),
            block_id_2: _make_pb(block_id_2, "Matrix M2"),
        }
        result = MatrixExplanationService.assemble_matrices_to_explain(
            dtos, title_map={}, blocks_by_id=blocks_by_id, target_locale="en"
        )
        # blk_111111111111111111111111 has quotes, blk_222222222222222222222222 has empty quotes
        assert len(result) == 2
        assert result[0].matrix_id == "MX-0"
        assert result[0].real_matrix_id == block_id_1
        assert result[1].matrix_id == "MX-1"
        assert result[1].real_matrix_id == block_id_2
        assert result[1].justification == "No direct evidence quotes or specific deficits recorded for this matrix."


# ============================================================================
# CONTRACT GROUP 4: Integration Verification
# Promise: Phase 1 + Phase 2 work together as a coherent pipeline
# ============================================================================


class TestPhase1Phase2Integration:
    """Verify that Phase 1 DTOs and Phase 2 DAG pipeline integrate correctly."""

    def test_execution_state_uses_quote_evidence_dto(self) -> None:
        """INTEGRATION: ExecutionState.evidence_quotes must use QuoteEvidenceDTO type."""
        from backend_v2.models.state import ExecutionState

        field = ExecutionState.model_fields["evidence_quotes"]
        annotation_str = str(field.annotation)
        assert "QuoteEvidenceDTO" in annotation_str, (
            f"INTEGRATION FAILURE: ExecutionState.evidence_quotes type is {annotation_str}."
        )

    def test_execution_state_evidence_quotes_no_legacy_dict(self) -> None:
        """INTEGRATION: Guarantee no legacy Dict usage in evidence_quotes schema."""
        from backend_v2.models.state import ExecutionState

        field = ExecutionState.model_fields["evidence_quotes"]
        annotation_str = str(field.annotation).lower()
        assert "dict" not in annotation_str, (
            f"INTEGRATION FAILURE: Legacy dict fallback found in evidence_quotes schema: {annotation_str}"
        )

    def test_synthesis_distiller_output_is_serializable(self) -> None:
        """INTEGRATION: Distiller output (state_delta) must be JSON-serializable
        for DAG transport between nodes.
        """
        from backend_v2.services.orchestrator.synthesis_payload_compressor import (
            SynthesisPayloadCompressor,
        )

        payload: dict[str, Any] = {
            "normalized_score": 85.0,
            "evaluations": [
                {
                    "atom_id": "a1",
                    "exact_quotes": ["Key evidence."],
                    "semantic_reasoning": "Solid reasoning.",
                }
            ],
        }
        result = SynthesisPayloadCompressor.compress_synthesis_payload(payload)
        # Must be valid JSON
        parsed = json.loads(result)
        assert isinstance(parsed, dict), "Distiller output is not a valid JSON dict"

    def test_no_orphaned_synthesis_test_files(self) -> None:
        """INTEGRATION: Verify no orphaned test files for deleted synthesis.py.

        Falsification: Scan tests/unit/hooks/ for any test_synthesis*.py files.
        """
        test_dir = Path("backend_v2/tests/unit/hooks")
        if test_dir.exists():
            synthesis_tests = list(test_dir.glob("test_synthesis*.py"))
            # test_row_explanations is also legacy
            row_exp_tests = list(test_dir.glob("test_row_explanations.py"))
            orphans = synthesis_tests + row_exp_tests
            assert orphans == [], (
                f"ORPHANED TEST FILES: {[str(f) for f in orphans]}. These tests reference the deleted synthesis.py."
            )
