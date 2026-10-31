"""End-to-End Orchestration (PDF Execution & Dynamic MCP Verification Test).

This test validates the FastAPI backend's ability to ingest PDF files via Base64,
perform live MCP gateway tool discovery and invocation, execute a full LLM workflow
to completion, and render the resulting report PDF.
"""

import base64
import json
import logging
import os
import subprocess
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import fitz
import pytest
import requests
from pydantic import ValidationError

from backend_v2.exceptions import AppException
from backend_v2.models.core_base import I18nText, generate_opaque_id
from backend_v2.models.domain.matrix import AntiPattern, ContrastivePairDTO, MatrixClaim, MatrixScale, TDAAssertion
from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock
from backend_v2.models.domain.proposition_graph import FalsifiedClaimMatch
from backend_v2.models.domain.system_config import SystemConfigMCPGateways
from backend_v2.models.dtos.atom_evaluation import ReasoningStepDTO
from backend_v2.models.dtos.atom_result import AtomResultDTO, HydratedAtomDTO
from backend_v2.models.dtos.causal_discovery import (
    AntiFluffAuditDTO,
    CausalEdgeDTO,
    CausalGraphPayloadDTO,
    CausalNodeDTO,
    CausalRootCauseDiagnosisDTO,
    CausalTdaFusionResultDTO,
    FairScoringBreakdownDTO,
    PrescriptiveRemediationDTO,
)
from backend_v2.models.dtos.lightweight_matrix import LightweightMatrixOutput
from backend_v2.models.dtos.matrix_scorecard import MatrixScorecardRowDTO, ScorecardAtomDTO
from backend_v2.models.dtos.mcp import (
    MCPContentBlockDTO,
    MCPDiscoveredToolWireDTO,
    MCPInitializeResultDTO,
    MCPJsonRpcRequestDTO,
    MCPJsonRpcResponseDTO,
    MCPServerInfoDTO,
    MCPToolCallResultDTO,
    MCPToolInputSchemaDTO,
    MCPToolSchemaPropertyDTO,
    MCPToolsListResultDTO,
)
from backend_v2.models.dtos.quote_evidence import QuoteEvidenceDTO
from backend_v2.models.dtos.report_data import ReportDataDTO
from backend_v2.models.dtos.synthesis import (
    CausalSynthesisBriefDTO,
    MatrixFailureDeficitDTO,
)
from backend_v2.models.enums import (
    BlockDataType,
    CausalRootCauseType,
    EntityPrefix,
    ExecutionStatus,
    JSONSchemaPropertyType,
    PromptBlockCategory,
    ReportStatus,
    SDUIComponentType,
    VisualIntent,
)
from backend_v2.models.state import StepOutputDTO
from backend_v2.models.view.sdui import (
    MarkdownBlock,
    ParagraphBlock,
    SduiCausalGraphBlock,
    SduiMatrixSummaryTableBlock,
    SduiNACard,
)
from backend_v2.services.length_budget_enforcer import enforce_sentence_boundary_budget
from backend_v2.services.mcp.alias_registry import AliasRegistry
from backend_v2.services.mcp.url_validator import MCPUrlValidator
from backend_v2.services.orchestrator.matrix_explanation_service import MatrixExplanationService
from backend_v2.services.orchestrator.synthesis_payload_compressor import SynthesisPayloadCompressor
from backend_v2.services.pdf_generator import PdfReportService
from backend_v2.services.sdui.sdui_mapper_service import SduiMapperService
from backend_v2.settings import get_settings

logger = logging.getLogger(__name__)

# Paths
WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
BACKEND_LOG_FILE = os.path.join(WORKSPACE_ROOT, "backend_debug.log")
TESTILYHYT_DIR = os.path.join(WORKSPACE_ROOT, "docs", "testilyhyt")

TARGET_WORKFLOW_ID = os.environ.get("TEST_WORKFLOW_ID", "wf_d653170e174847559e08af42b938d826")
WAIT_TIMEOUT = int(os.environ.get("TEST_WAIT_TIMEOUT", "3600"))
DEFAULT_GATEWAY_ID = "sys_0195f3a00000700080008172bda70c86"


class _LocalMCPRequestHandler(BaseHTTPRequestHandler):
    """In-process JSON-RPC 2.0 HTTP handler serving dynamic MCP tools during live E2E verification."""

    def log_message(self, format: str, *args: object) -> None:
        """Silence standard HTTP server access logs during test execution.

        Args:
            format: Log message format string.
            *args: Format arguments.
        """
        return

    def do_POST(self) -> None:
        """Handle incoming JSON-RPC 2.0 POST requests for initialize, tools/list, and tools/call."""
        content_len = int(self.headers["Content-Length"]) if "Content-Length" in self.headers else 0
        raw_body = self.rfile.read(content_len).decode("utf-8")
        rpc_req = MCPJsonRpcRequestDTO.model_validate_json(raw_body)

        if rpc_req.method == "initialize":
            init_resp = MCPJsonRpcResponseDTO(
                id=rpc_req.id,
                result=MCPInitializeResultDTO(
                    protocol_version="2025-03-26",
                    server_info=MCPServerInfoDTO(icons=[]),
                    capabilities={},
                ),
            )
            payload_bytes = init_resp.model_dump_json(by_alias=True, exclude_none=True).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload_bytes)))
            self.end_headers()
            self.wfile.write(payload_bytes)
            return

        if rpc_req.method == "notifications/initialized":
            self.send_response(202)
            self.end_headers()
            return

        if rpc_req.method == "tools/list":
            list_resp = MCPJsonRpcResponseDTO(
                id=rpc_req.id,
                result=MCPToolsListResultDTO(
                    tools=[
                        MCPDiscoveredToolWireDTO(
                            name="mcp_tavily_search",
                            description="Perform an explicit search on the live internet using Tavily.",
                            input_schema=MCPToolInputSchemaDTO(
                                properties={
                                    "query": MCPToolSchemaPropertyDTO(
                                        type=JSONSchemaPropertyType.STRING,
                                        description="The search query to submit to the Tavily search engine.",
                                    )
                                },
                                required=["query"],
                            ),
                        ),
                        MCPDiscoveredToolWireDTO(
                            name="mcp_wikipedia_search",
                            description="Search Wikipedia articles and return top matching titles and snippets.",
                            input_schema=MCPToolInputSchemaDTO(
                                properties={
                                    "query": MCPToolSchemaPropertyDTO(
                                        type=JSONSchemaPropertyType.STRING,
                                        description="The search term to query on Wikipedia.",
                                    )
                                },
                                required=["query"],
                            ),
                        ),
                        MCPDiscoveredToolWireDTO(
                            name="mcp_wikipedia_read",
                            description="Retrieve the full encyclopedic summary of a specific Wikipedia article by title.",
                            input_schema=MCPToolInputSchemaDTO(
                                properties={
                                    "title": MCPToolSchemaPropertyDTO(
                                        type=JSONSchemaPropertyType.STRING,
                                        description="The exact title of the Wikipedia article to read.",
                                    )
                                },
                                required=["title"],
                            ),
                        ),
                    ]
                ),
            )
            payload_bytes = list_resp.model_dump_json(by_alias=True, exclude_none=True).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload_bytes)))
            self.end_headers()
            self.wfile.write(payload_bytes)
            return

        call_resp = MCPJsonRpcResponseDTO(
            id=rpc_req.id,
            result=MCPToolCallResultDTO(
                content=[
                    MCPContentBlockDTO(
                        type="text",
                        text="Verified external empirical reference from MCP gateway search.",
                    )
                ],
                is_error=False,
            ),
        )
        payload_bytes = call_resp.model_dump_json(by_alias=True, exclude_none=True).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload_bytes)))
        self.end_headers()
        self.wfile.write(payload_bytes)


def clear_logs() -> None:  # pragma: no cover
    """Clear backend debug log."""
    with open(BACKEND_LOG_FILE, "w", encoding="utf-8") as f:
        f.write("")


def is_redis_running() -> bool:  # pragma: no cover
    """Check if Redis is alive on port 6379.

    Returns:
        True if Redis responds to ping on port 6379.
    """
    try:
        import redis

        client = redis.Redis(host="127.0.0.1", port=6379, socket_timeout=1)
        return bool(client.ping())
    except redis.ConnectionError, redis.TimeoutError, OSError:
        return False


def is_backend_running(timeout: float = 1.0) -> bool:  # pragma: no cover
    """Check if the backend API is alive on port 8000.

    Args:
        timeout: Request timeout in seconds.

    Returns:
        True if the backend docs endpoint returns HTTP 200.
    """
    try:
        response = requests.get("http://127.0.0.1:8000/docs", timeout=timeout)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def wait_for_backend(timeout_seconds: int = 30) -> bool:  # pragma: no cover
    """Wait for backend API to become ready with retries.

    Args:
        timeout_seconds: Maximum wait time in seconds.

    Returns:
        True once the backend responds or False on timeout.
    """
    start = time.time()
    while time.time() - start < timeout_seconds:
        if is_backend_running():
            return True
        time.sleep(1)
    return False


def get_base64_file(file_path: str) -> str:  # pragma: no cover
    """Read a file and return its base64 encoded string.

    Args:
        file_path: Path to the binary file on disk.

    Returns:
        UTF-8 base64 string representation of the file content.
    """
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def test_local_mcp_request_handler_roundtrip_positive() -> None:
    """Positive: Verify that _LocalMCPRequestHandler serves initialize, tools/list, and tools/call JSON-RPC 2.0 envelopes."""
    mcp_server = ThreadingHTTPServer(("127.0.0.1", 0), _LocalMCPRequestHandler)
    mcp_port = mcp_server.server_address[1]
    mcp_thread = threading.Thread(target=mcp_server.serve_forever, daemon=True)
    mcp_thread.start()
    url = f"http://127.0.0.1:{mcp_port}/mcp"
    try:
        init_res = requests.post(
            url,
            data=MCPJsonRpcRequestDTO(id=1, method="initialize").model_dump_json(exclude_none=True),
            headers={"Content-Type": "application/json"},
            timeout=5,
        )
        assert init_res.status_code == 200
        init_dto = MCPJsonRpcResponseDTO.model_validate_json(init_res.text)
        assert isinstance(init_dto.result, MCPInitializeResultDTO)

        notif_res = requests.post(
            url,
            data=MCPJsonRpcRequestDTO(method="notifications/initialized").model_dump_json(exclude_none=True),
            headers={"Content-Type": "application/json"},
            timeout=5,
        )
        assert notif_res.status_code == 202

        list_res = requests.post(
            url,
            data=MCPJsonRpcRequestDTO(id=2, method="tools/list").model_dump_json(exclude_none=True),
            headers={"Content-Type": "application/json"},
            timeout=5,
        )
        assert list_res.status_code == 200
        list_dto = MCPJsonRpcResponseDTO.model_validate_json(list_res.text)
        assert isinstance(list_dto.result, MCPToolsListResultDTO)
        assert len(list_dto.result.tools) == 3

        call_res = requests.post(
            url,
            data=MCPJsonRpcRequestDTO(id=3, method="tools/call").model_dump_json(exclude_none=True),
            headers={"Content-Type": "application/json"},
            timeout=5,
        )
        assert call_res.status_code == 200
        call_dto = MCPJsonRpcResponseDTO.model_validate_json(call_res.text)
        assert isinstance(call_dto.result, MCPToolCallResultDTO)
        assert call_dto.result.is_error is False
    finally:
        mcp_server.shutdown()
        mcp_server.server_close()


def test_real_llm_mcp_url_ssrf_rejected_negative() -> None:
    """Negative: Verify that MCPUrlValidator blocks private and metadata endpoints when private networks are disabled."""
    with pytest.raises(AppException) as exc_info:
        MCPUrlValidator.validate_mcp_endpoint_url(
            "http://169.254.169.254/latest/meta-data",
            allow_private_networks=False,
        )
    assert exc_info.value.status_code in (400, 403)


def test_real_llm_mcp_invalid_alias_rejected_negative() -> None:
    """Negative: Verify that AliasRegistry rejects un-namespaced tool identifiers."""
    with pytest.raises(AppException) as exc_info:
        AliasRegistry.parse_namespaced_tool_alias("mcp_tavily_search_without_namespace")
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_integration_real_llm_preserves_topological_deficits_and_causal_brief() -> None:
    """Positive: Verify end-to-end topological synthesis cohesion, MatrixFailureDeficitDTO, and CausalSynthesisBriefDTO within 300,000-char ceiling."""
    # Phase 4, Step 4.3: Verify MatrixFailureDeficitDTO, CausalSynthesisBriefDTO, Micro-CoT/quote retention, and inline SDUI short-circuit lineage
    settings = get_settings()
    assert settings.max_synthesis_evaluations == 0
    assert settings.max_synthesis_reasoning_length == 0
    assert settings.max_synthesis_quote_length == 0
    assert settings.max_synthesis_quotes_per_matrix == 0
    assert settings.max_synthesis_unmet_criteria_per_matrix == 0

    block_id = generate_opaque_id(EntityPrefix.PROMPT_BLOCK)
    tda_parent_id = generate_opaque_id(EntityPrefix.TDA)
    tda_child_na_id = generate_opaque_id(EntityPrefix.TDA)
    tda_passed_id = generate_opaque_id(EntityPrefix.TDA)

    matrix_block = MatrixPromptBlock(
        id=block_id,
        slug="strategic_governance_matrix",
        label=I18nText(translations={"en": "Strategic Governance Matrix", "fi": "Strategisen Hallinnan Matriisi"}),
        description=I18nText(translations={"en": "Governance evaluation", "fi": "Hallinnan arviointi"}),
        ai_description="Evaluate strategic governance assertions with strict empirical grounding.",
        category_id=PromptBlockCategory.MATRIX,
        type=BlockDataType.FLOAT,
        scales=[
            MatrixScale(
                score=1,
                ai_label="FOUNDATION",
                claims=[
                    MatrixClaim(
                        label=I18nText(translations={"en": "Baseline Audit Trail Verified"}),
                        tda_assertions=[
                            TDAAssertion(
                                tda_id=tda_passed_id,
                                depends_on=(),
                                inverse_evidence=False,
                                aggregation_mode="ALL_MUST_COMPLY",
                                concept_description="Baseline audit trail is verified with immutable timestamps.",
                            )
                        ],
                    ),
                    MatrixClaim(
                        label=I18nText(translations={"en": "Root Capital Allocation Control"}),
                        tda_assertions=[
                            TDAAssertion(
                                tda_id=tda_parent_id,
                                depends_on=(),
                                inverse_evidence=False,
                                aggregation_mode="ALL_MUST_COMPLY",
                                concept_description="Root capital allocation threshold is quantified and enforced.",
                                anti_patterns=[
                                    AntiPattern(
                                        pattern="Vague qualitative commitment without numeric cap",
                                        allows_contextual_excuse=False,
                                    )
                                ],
                                contrastive_example=ContrastivePairDTO(
                                    acceptable="Capital expenditure is capped at EUR 2.5M per quarter.",
                                    rejected="We will monitor capital expenditure closely.",
                                ),
                            )
                        ],
                    ),
                ],
            ),
            MatrixScale(
                score=2,
                ai_label="ADVANCED",
                claims=[
                    MatrixClaim(
                        label=I18nText(translations={"en": "Downstream Portfolio Solvency Gate"}),
                        tda_assertions=[
                            TDAAssertion(
                                tda_id=tda_child_na_id,
                                depends_on=(),
                                inverse_evidence=False,
                                aggregation_mode="ALL_MUST_COMPLY",
                                concept_description="Downstream portfolio solvency gate depends on root capital control.",
                                anti_patterns=[
                                    AntiPattern(
                                        pattern="Unhedged solvency projection",
                                        allows_contextual_excuse=False,
                                    )
                                ],
                                contrastive_example=ContrastivePairDTO(
                                    acceptable="Solvency ratio remains >= 1.8x under -25% revenue shock.",
                                    rejected="Solvency is assumed under baseline growth.",
                                ),
                            )
                        ],
                    )
                ],
            ),
        ],
    )

    verbatim_quote = (
        "Section 4.2 confirms immutable ledger timestamps across all Q3 treasury transactions without exception."
    )
    parent_reasoning = (
        "Step 1: Premise requires numeric cap. Step 2: Scanned section 5. "
        "Step 3: Detected anti-pattern of vague commitment. Step 4: Failed due to missing numeric cap."
    )

    atom_results = [
        AtomResultDTO(
            tda_id=tda_passed_id,
            status=ExecutionStatus.PASSED,
            evaluation_reasoning="Verified immutable ledger timestamps in section 4.2.",
            source_quotes=(verbatim_quote,),
            extensions={},
            depends_on_tda_ids=[],
            short_circuit_reason_tda_ids=[],
        ),
        AtomResultDTO(
            tda_id=tda_parent_id,
            status=ExecutionStatus.FAILED,
            evaluation_reasoning=parent_reasoning,
            source_quotes=None,
            extensions={},
            depends_on_tda_ids=[],
            short_circuit_reason_tda_ids=[],
        ),
        AtomResultDTO(
            tda_id=tda_child_na_id,
            status=ExecutionStatus.N_A,
            evaluation_reasoning=None,
            source_quotes=None,
            extensions={},
            depends_on_tda_ids=[tda_parent_id],
            short_circuit_reason_tda_ids=[tda_parent_id],
        ),
    ]

    step_dtos = [
        StepOutputDTO(
            step_id="stp_0195f3a0000070018000000000000001",
            block_id="blk_atom_results",
            data_type="unknown",
            payload=atom_results,
        ),
        StepOutputDTO(
            step_id="stp_0195f3a0000070018000000000000002",
            block_id=block_id,
            data_type="matrix",
            payload=LightweightMatrixOutput(
                raw_score=1.0,
                normalized_score=25.0,
                level_breakdown={},
                justification="Initial matrix evaluation output.",
                evaluated_atoms={
                    tda_passed_id: ExecutionStatus.PASSED,
                    tda_parent_id: ExecutionStatus.FAILED,
                    tda_child_na_id: ExecutionStatus.N_A,
                },
                extensions={},
            ),
        ),
    ]

    explanation_contexts = MatrixExplanationService.assemble_matrices_to_explain(
        available_dtos=step_dtos,
        title_map={block_id: "Strategic Governance Matrix"},
        blocks_by_id={block_id: matrix_block},
        target_locale="en",
    )
    assert len(explanation_contexts) == 1
    ctx = explanation_contexts[0]
    assert verbatim_quote in ctx.justification
    assert len(ctx.unmet_deficits) == 2

    deficits_by_claim: dict[str, MatrixFailureDeficitDTO] = {d.claim: d for d in ctx.unmet_deficits}
    parent_deficit = deficits_by_claim["Root Capital Allocation Control"]
    assert parent_deficit.status == "FAILED"
    assert parent_deficit.evaluation_reasoning == parent_reasoning
    assert "Vague qualitative commitment without numeric cap" in parent_deficit.anti_patterns[0]
    assert parent_deficit.contrastive_rejected == "We will monitor capital expenditure closely."
    assert parent_deficit.contrastive_acceptable == "Capital expenditure is capped at EUR 2.5M per quarter."

    child_deficit = deficits_by_claim["Downstream Portfolio Solvency Gate"]
    assert child_deficit.status == "N_A"
    assert (
        f"[Downstream Portfolio Solvency Gate] <-- SHORT-CIRCUITED BY PREREQUISITE FAILURE: "
        f"[Root Capital Allocation Control: {parent_reasoning}]"
    ) in child_deficit.short_circuited_by_claims
    assert child_deficit.contrastive_acceptable == "Solvency ratio remains >= 1.8x under -25% revenue shock."

    # Build CausalTdaFusionResultDTO and verify CausalSynthesisBriefDTO hydration
    rebuttal_node_id = generate_opaque_id(EntityPrefix.NODE)
    warrant_node_id = generate_opaque_id(EntityPrefix.NODE)
    falsified_node_id = generate_opaque_id(EntityPrefix.NODE)

    fusion_dto = CausalTdaFusionResultDTO(
        graph=CausalGraphPayloadDTO(
            nodes=[
                CausalNodeDTO(
                    node_id=tda_parent_id,
                    claim="Root Capital Allocation Control",
                    status=ExecutionStatus.FAILED,
                    blame_parent_ids=[],
                    dependent_child_ids=[tda_child_na_id],
                    short_circuited_by_claims=[],
                    falsified_warrant_claims=[],
                ),
                CausalNodeDTO(
                    node_id=tda_child_na_id,
                    claim="Downstream Portfolio Solvency Gate",
                    status=ExecutionStatus.N_A,
                    blame_parent_ids=[tda_parent_id],
                    dependent_child_ids=[],
                    short_circuited_by_claims=child_deficit.short_circuited_by_claims,
                    falsified_warrant_claims=["Treasury stress test falsifies solvency warrant under -25% shock."],
                ),
            ],
            edges=[
                CausalEdgeDTO(
                    source_id=tda_parent_id,
                    target_id=tda_child_na_id,
                    reasoning="Root capital cap is a mandatory prerequisite for solvency gate.",
                )
            ],
            root_cause_node_ids=[tda_parent_id],
            isolated_node_ids=[],
            partition_node_ids={},
            edge_root_causes=[],
            cycle_detected=False,
        ),
        root_cause_diagnoses=[
            CausalRootCauseDiagnosisDTO(
                failing_node_id=tda_child_na_id,
                root_cause_parent_id=tda_parent_id,
                paragraph_ref="Section 5.1",
                explanation="Solvency gate blocked by unquantified capital allocation control.",
                penalty_points=2.5,
                root_cause_type=CausalRootCauseType.NODE_FAILURE,
                root_cause_claim="Root Capital Allocation Control",
                failing_node_claim="Downstream Portfolio Solvency Gate",
            )
        ],
        anti_fluff_audit=AntiFluffAuditDTO(
            isolated_concept_count=0,
            cycle_detected=False,
            unsupported_claims_count=1,
            logical_cohesion_score=0.82,
            detected_hollow_terms=[],
        ),
        prescriptive_remediations=[
            PrescriptiveRemediationDTO(
                target_node_id=tda_parent_id,
                required_action="Enforce binding EUR 2.5M quarterly capital expenditure ceiling.",
                unlocks_node_ids=[tda_child_na_id],
                potential_score_impact=3.0,
            )
        ],
        fair_scoring=FairScoringBreakdownDTO(
            independent_error_count=1,
            cascading_fault_count=1,
            raw_penalty_points=5.0,
            deduplicated_penalty_points=2.5,
            dampened_savings_points=2.5,
        ),
        total_deliverable_nodes=2,
        falsified_claims=[
            FalsifiedClaimMatch(
                rebuttal_id=rebuttal_node_id,
                invalidated_warrant_id=warrant_node_id,
                falsified_claim_id=falsified_node_id,
                rebuttal_confidence=0.94,
                claim_statement="Baseline solvency assumption holds without liquidity reserve.",
            )
        ],
    )

    brief_dto = CausalSynthesisBriefDTO.from_causal_payload(fusion_dto)
    brief_md = brief_dto.format_for_prompt()
    assert "Root Capital Allocation Control -> Downstream Portfolio Solvency Gate" in brief_md
    assert "Baseline solvency assumption holds without liquidity reserve." in brief_md
    assert "Enforce binding EUR 2.5M quarterly capital expenditure ceiling." in brief_md

    # Verify compressed payload stays strictly within the 300,000-character ceiling
    compressed_context = SynthesisPayloadCompressor.compress_synthesis_payload(ctx)
    combined_synthesis_prompt = f"{compressed_context}\n\n{brief_md}"
    bounded_synthesis_prompt = enforce_sentence_boundary_budget(combined_synthesis_prompt, max_chars=300_000)
    assert 0 < len(bounded_synthesis_prompt) <= 300_000

    # Verify completed ReportDataDTO preserves synthesized row explanations, XAI highlights, and SDUI blocks
    exec_id = generate_opaque_id(EntityPrefix.EXECUTION)
    matrix_row = MatrixScorecardRowDTO(
        block_id=block_id,
        name="Strategic Governance Matrix",
        label_i18n=I18nText(translations={"en": "Strategic Governance Matrix"}),
        description=None,
        row_explanation=(
            "Score capped at 1.0 because Root Capital Allocation Control lacked a numeric cap, "
            "short-circuiting Downstream Portfolio Solvency Gate."
        ),
        score=1.0,
        raw_score=1.0,
        raw_scale_min=1.0,
        raw_scale_max=5.0,
        scale_min=1.0,
        scale_max=5.0,
        normalized_score=25.0,
        true_atoms=1,
        total_atoms=3,
        score_display_label="1.0 / 5.0",
        evidence_type=None,
        cited_source_id=None,
        cited_text_quote=verbatim_quote,
        cited_web_citation=None,
        cited_source_title=None,
        cited_source_url=None,
        remediation_steps="Enforce binding EUR 2.5M quarterly capital expenditure ceiling to unlock solvency gate.",
        confidence=0.95,
        contextual_override=False,
        semantic_reasoning=None,
        ui_plot_ratio=0.25,
        ui_boundary_labels={},
        is_evaluative=True,
        allow_contextual_override=False,
        used_evidence_ids=[],
        clustered_row_sources=[],
        tda_state=None,
        level_names={"1": "Foundation", "2": "Advanced"},
        level_breakdown={"1": "1/2", "2": "0/1"},
        evaluated_atoms=[
            ScorecardAtomDTO(
                atom_id=tda_passed_id,
                level=1,
                level_name="Foundation",
                claim_label="Baseline Audit Trail Verified",
                extracted_facts={},
                exact_quotes=[
                    QuoteEvidenceDTO(
                        source_quotes=(verbatim_quote,),
                        is_verified=True,
                        verified_source_ids=["src_0"],
                        unverified_aliases=[],
                    )
                ],
                internal_logic_en=ReasoningStepDTO(
                    step_1_identify_premise="Verify ledger timestamps.",
                    step_2_scan_source="Scanned section 4.2.",
                    step_3_evaluate_anti_patterns="No anti-patterns detected.",
                    step_4_final_conclusion="Criterion satisfied.",
                ),
                status=ExecutionStatus.PASSED,
                semantic_reasoning="Verified immutable ledger timestamps in section 4.2.",
                contextual_override=False,
                structural_location=None,
                chart_display_label="Audit Trail",
                visual_intent=VisualIntent.SUCCESS,
            )
        ],
        inner_sdui_blocks=[],
    )

    sdui_matrix_block = SduiMatrixSummaryTableBlock(
        title=I18nText(translations={"en": "Strategic Governance Summary"}),
        matrix_visible_columns=["label", "raw_score", "row_explanation"],
        matrix_column_labels={
            "label": I18nText(translations={"en": "Dimension"}),
            "raw_score": I18nText(translations={"en": "Score"}),
            "row_explanation": I18nText(translations={"en": "Diagnostic Explanation"}),
        },
        axes=[matrix_row],
        short_circuited_by_claims=child_deficit.short_circuited_by_claims,
        falsified_warrant_claims=["Baseline solvency assumption holds without liquidity reserve."],
    )

    sdui_causal_block = SduiCausalGraphBlock(
        critical_path_nodes=fusion_dto.graph.nodes,
        critical_edges=fusion_dto.graph.edges,
        root_cause_diagnoses=fusion_dto.root_cause_diagnoses,
        anti_fluff_audit=fusion_dto.anti_fluff_audit,
        prescriptive_remediations=fusion_dto.prescriptive_remediations,
        fair_scoring=fusion_dto.fair_scoring,
        intact_claims_count=0,
        total_claims_count=2,
        summary=I18nText(translations={"en": "Causal Argument Topology"}),
        short_circuited_by_claims=child_deficit.short_circuited_by_claims,
        falsified_warrant_claims=["Baseline solvency assumption holds without liquidity reserve."],
    )

    report_dto = ReportDataDTO(
        execution_id=exec_id,
        workflow_id=generate_opaque_id(EntityPrefix.WORKFLOW),
        profile_id=generate_opaque_id(EntityPrefix.OUTPUT_PROFILE),
        profile_name=I18nText(translations={"en": "Executive Audit Report"}),
        available_profiles={},
        visible_metadata=[],
        results=atom_results,
        hydrated_references={
            tda_passed_id: HydratedAtomDTO(
                sdui_component=SDUIComponentType.BOOLEAN_CARD,
                resolved_claim="Baseline Audit Trail Verified",
                source_quotes=(verbatim_quote,),
            ),
            tda_parent_id: HydratedAtomDTO(
                sdui_component=SDUIComponentType.BOOLEAN_CARD,
                resolved_claim="Root Capital Allocation Control",
            ),
            tda_child_na_id: HydratedAtomDTO(
                sdui_component=SDUIComponentType.BOOLEAN_CARD,
                resolved_claim="Downstream Portfolio Solvency Gate",
            ),
        },
        mcp_tool_audit=[],
        short_circuited_by_claims=child_deficit.short_circuited_by_claims,
        falsified_warrant_claims=["Baseline solvency assumption holds without liquidity reserve."],
        inner_sdui_blocks=[
            MarkdownBlock(text="# Executive Audit Report"),
            ParagraphBlock(
                text="Synthesized executive summary grounded in causal root cause chains.",
                exact_quotes=[],
                citations=[],
            ),
            sdui_matrix_block,
            sdui_causal_block,
        ],
    )

    mapper = SduiMapperService()
    mapped_report = mapper.map_report_to_sdui(report_dto, execution_id=exec_id, lang="en")
    assert not any(isinstance(b, SduiNACard) for b in mapped_report.inner_sdui_blocks)
    assert matrix_row.remediation_steps is not None

    pdf_service = PdfReportService()
    rendered_html = await pdf_service.generate_execution_html(exec_id, report_dto=report_dto, locale="en")
    assert "Root Capital Allocation Control" in rendered_html
    assert "Baseline solvency assumption holds without liquidity reserve." in rendered_html


def test_integration_real_llm_topological_deficit_and_brief_validation_negative() -> None:
    """Negative & Boundary: Verify MatrixFailureDeficitDTO, CausalSynthesisBriefDTO, and compressor reject invalid inputs."""
    # Phase 4, Step 4.3: Negative & boundary validation for topological synthesis contracts
    with pytest.raises(ValidationError):
        MatrixFailureDeficitDTO.model_validate(
            {
                "claim": "Invalid Passed Deficit",
                "status": "PASSED",
                "scale_score": 1,
            }
        )

    with pytest.raises(ValidationError):
        CausalSynthesisBriefDTO.model_validate(
            {
                "intact_propositions": -1,
                "total_propositions": 2,
            }
        )

    with pytest.raises(AppException) as exc_info:
        SynthesisPayloadCompressor.compress_synthesis_payload("   ")
    assert exc_info.value.status_code == 400


@pytest.mark.skipif(
    os.environ.get("RUN_LIVE_E2E") != "true",
    reason="Live E2E tests skipped by default. Set $env:RUN_LIVE_E2E='true' to run as final verification gate.",
)
@pytest.mark.asyncio
@pytest.mark.order("last")
async def test_real_llm_pdf_execution() -> None:  # pragma: no cover
    """Live E2E test verifying PDF processing and dynamic MCP execution via the FastAPI Backend."""
    pdf_dir = os.path.join(WORKSPACE_ROOT, "docs", "jwdatat")
    pdf_files = {
        "chat_log": os.path.join(pdf_dir, "keskusteluhistoria.pdf"),
        "product_text": os.path.join(pdf_dir, "lopputuote.pdf"),
        "reflection_text": os.path.join(pdf_dir, "reflektiodokumentti.pdf"),
    }

    for _, path in pdf_files.items():
        if not os.path.exists(path):
            pytest.skip(f"Required PDF not found: {path}. Skipping test.")

    clear_logs()

    mcp_server = ThreadingHTTPServer(("127.0.0.1", 0), _LocalMCPRequestHandler)
    mcp_port = mcp_server.server_address[1]
    mcp_thread = threading.Thread(target=mcp_server.serve_forever, daemon=True)
    mcp_thread.start()

    redis_server = None
    if not is_redis_running():
        logger.info("Local Redis not detected on port 6379. Starting TcpFakeServer daemon on port 6379.")
        from fakeredis import TcpFakeServer

        redis_server = TcpFakeServer(("127.0.0.1", 6379))
        redis_thread = threading.Thread(target=redis_server.serve_forever, daemon=True)
        redis_thread.start()
        time.sleep(0.5)
        assert is_redis_running(), "Failed to start TcpFakeServer on port 6379."

    backend_process = None
    worker_process = None
    backend_log_fp = None
    if not is_backend_running():
        logger.info("Backend is not running. Starting local FastAPI instance on port 8000.")
        env = os.environ.copy()
        if "PYTEST_CURRENT_TEST" in env:
            del env["PYTEST_CURRENT_TEST"]
        # Phase 4, Step 4.3: Strip synthetic conftest mock keys so subprocesses load real credentials from .env
        for mock_env_key, mock_env_val in (
            ("OPENAI_API_KEY", "mock-openai-key"),
            ("ANTHROPIC_API_KEY", "mock-anthropic-key"),
            ("GOOGLE_API_KEY", "mock-google-key"),
            ("GEMINI_API_KEY", "mock-gemini-key"),
        ):
            if mock_env_key in env and env[mock_env_key] == mock_env_val:
                del env[mock_env_key]
        env["USE_FIREBASE_AUTH"] = "false"
        env["MCP_ALLOW_PRIVATE_NETWORKS"] = "true"
        env["PYTHONUTF8"] = "1"
        env["PYTHONIOENCODING"] = "utf-8"
        env["NO_COLOR"] = "1"
        env["TERM"] = "dumb"

        backend_log_fp = open(BACKEND_LOG_FILE, "a", encoding="utf-8")
        backend_cmd = [
            "uv",
            "run",
            "python",
            "-m",
            "uvicorn",
            "backend_v2.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
        ]
        backend_process = subprocess.Popen(
            backend_cmd, cwd=WORKSPACE_ROOT, env=env, stdout=backend_log_fp, stderr=subprocess.STDOUT
        )

        worker_cmd = [
            "uv",
            "run",
            "python",
            "-m",
            "backend_v2.run_worker",
        ]
        worker_process = subprocess.Popen(
            worker_cmd, cwd=WORKSPACE_ROOT, env=env, stdout=backend_log_fp, stderr=subprocess.STDOUT
        )

        if not wait_for_backend(timeout_seconds=30):
            if backend_process:
                subprocess.run(f"taskkill /F /T /PID {backend_process.pid}", shell=True, capture_output=True)
            if worker_process:
                subprocess.run(f"taskkill /F /T /PID {worker_process.pid}", shell=True, capture_output=True)
            if backend_log_fp:
                backend_log_fp.close()
            if redis_server:
                redis_server.shutdown()
                redis_server.server_close()
            mcp_server.shutdown()
            mcp_server.server_close()
            pytest.fail("Failed to start FastAPI backend for testing.")
    else:
        logger.info("Backend is already running. Re-using active instance.")

    headers = {
        "Authorization": "Bearer mock-token:usr_0195f3a00000700188a0d5f6151349a5",
        "Content-Type": "application/json",
        "Accept-Language": "fi",
    }
    root_headers = {
        "Authorization": "Bearer mock-token:usr_0195f3a00000700a83fd6b3d77c748f4",
        "Content-Type": "application/json",
        "Accept-Language": "fi",
    }
    original_gateway: SystemConfigMCPGateways | None = None

    try:
        gw_get_res = requests.get(
            f"http://127.0.0.1:8000/api/v2/studio/mcp-gateways/{DEFAULT_GATEWAY_ID}",
            headers=root_headers,
            timeout=15,
        )
        if gw_get_res.status_code == 200:
            original_gateway = SystemConfigMCPGateways.model_validate_json(gw_get_res.text)
            updated_gateway = original_gateway.model_copy(update={"endpoint_url": f"http://127.0.0.1:{mcp_port}/mcp"})
            gw_put_res = requests.put(
                f"http://127.0.0.1:8000/api/v2/studio/mcp-gateways/{DEFAULT_GATEWAY_ID}",
                data=updated_gateway.model_dump_json(),
                headers=root_headers,
                timeout=15,
            )
            assert gw_put_res.status_code == 200, f"Failed to point MCP gateway to local server: {gw_put_res.text}"

        dynamic_inputs = {}
        for key, path in pdf_files.items():
            dynamic_inputs[key] = {
                "filename": os.path.basename(path),
                "content_base64": get_base64_file(path),
                "content_type": "application/pdf",
            }

        workflow_id = "wf_0195f3a0000070098d68c573802341db"
        payload = {"workflow_id": workflow_id, "target_locale": "fi", "raw_inputs": {"dynamic_inputs": dynamic_inputs}}

        logger.info("Sending execution POST request to backend...")
        response = requests.post(
            "http://127.0.0.1:8000/api/v2/execution/executions/", json=payload, headers=headers, timeout=30
        )

        assert response.status_code == 202, f"Failed to start execution: {response.text}"

        execution_data = response.json()
        execution_id = execution_data["id"]
        logger.info(f"Execution started with ID: {execution_id}. Polling for completion...")

        start_time = time.time()
        completed = False

        while time.time() - start_time < WAIT_TIMEOUT:
            status_res = requests.get(
                f"http://127.0.0.1:8000/api/v2/execution/executions/{execution_id}", headers=headers, timeout=30
            )

            assert status_res.status_code == 200, f"Failed to get execution status: {status_res.text}"

            status_data = status_res.json()
            current_status = status_data["status"] if "status" in status_data else None

            if current_status == ExecutionStatus.PASSED.value:
                logger.info(f"Execution {execution_id} completed successfully.")
                completed = True
                break
            elif current_status == ExecutionStatus.FAILED.value:
                logger.error(f"Execution failed: {json.dumps(status_data)}")
                pytest.fail(f"Execution {execution_id} failed.")

            time.sleep(5)

        assert completed, f"Execution {execution_id} timed out after {WAIT_TIMEOUT} seconds."

        logger.info("Requesting report generation via canonical reports endpoint...")
        create_report_res = requests.post(
            f"http://127.0.0.1:8000/api/v2/executions/{execution_id}/reports",
            json={"profile_id": "prf_0195f3a0000070058d6e7f8091a2b3c4"},
            headers=headers,
            timeout=30,
        )
        assert create_report_res.status_code == 202, (
            f"Failed to create report: {create_report_res.status_code} - {create_report_res.text}"
        )
        report_data = create_report_res.json()
        report_id = report_data["id"]
        logger.info("Report creation accepted, report_id=%s. Polling for READY status...", report_id)

        render_start = time.time()
        pdf_ready = False
        while time.time() - render_start < 120:
            status_res = requests.get(
                f"http://127.0.0.1:8000/api/v2/reports/{report_id}",
                headers=headers,
                timeout=30,
            )
            assert status_res.status_code == 200, (
                f"Failed to fetch report status: {status_res.status_code} - {status_res.text}"
            )
            current_status = status_res.json()["status"]
            if current_status == ReportStatus.READY.value:
                logger.info("Report generation completed successfully (READY).")
                pdf_ready = True
                break
            elif current_status == ReportStatus.FAILED.value:
                pytest.fail(f"Report generation failed for report_id={report_id}: {status_res.text}")
            elif current_status in (ReportStatus.PENDING.value, ReportStatus.GENERATING.value):
                logger.info("Report generation in progress (%s)...", current_status)
            else:
                logger.warning("Unexpected report status: %s", current_status)
            time.sleep(3)

        assert pdf_ready, f"Report generation timed out for {report_id}"

        logger.info("Verifying generated PDF via canonical reports PDF endpoint...")
        pdf_res = requests.get(
            f"http://127.0.0.1:8000/api/v2/reports/{report_id}/pdf",
            headers=headers,
            timeout=30,
        )
        assert pdf_res.status_code == 200, f"Failed to download PDF: {pdf_res.status_code} - {pdf_res.text}"
        assert pdf_res.headers["content-type"] == "application/pdf"

        doc = fitz.open(stream=pdf_res.content, filetype="pdf")
        full_text = ""
        for page in doc:
            full_text += page.get_text()

        assert "Kokonaisvaltainen Auditointi" in full_text or "Raportti" in full_text, (
            "Standard executive synthesis header missing from PDF!"
        )

        logger.info("PDF Execution E2E test passed successfully.")

    finally:
        if original_gateway is not None and is_backend_running():
            try:
                requests.put(
                    f"http://127.0.0.1:8000/api/v2/studio/mcp-gateways/{DEFAULT_GATEWAY_ID}",
                    data=original_gateway.model_dump_json(),
                    headers=root_headers,
                    timeout=10,
                )
            except requests.exceptions.RequestException:
                pass
        logger.info("Tearing down E2E orchestrator processes...")
        if backend_process:
            subprocess.run(f"taskkill /F /T /PID {backend_process.pid}", shell=True, capture_output=True)
        if worker_process:
            subprocess.run(f"taskkill /F /T /PID {worker_process.pid}", shell=True, capture_output=True)
        if backend_log_fp:
            backend_log_fp.close()
        if redis_server:
            redis_server.shutdown()
            redis_server.server_close()
        mcp_server.shutdown()
        mcp_server.server_close()
