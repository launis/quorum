"""Service for extracting knowledge during RAG Preflight."""

import logging
import re
from collections.abc import Awaitable, Callable
from typing import Any

from backend_v2.database.interfaces import ISystemRepository, IWorkflowRepository
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.llm.client import LLMClient
from backend_v2.models.domain.blackboard import GlobalAtomBlackboard
from backend_v2.models.v2_core import ExecutionRecord, Step, StepRule
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler
from backend_v2.services.orchestrator.two_pass_atomizer import TwoPassAtomizer
from backend_v2.settings import get_settings
from backend_v2.utils.alias_engine import AliasEngine

logger = logging.getLogger(__name__)


def _extract_effective_user_text(text: str) -> str:
    """Extract analytical user text from raw dynamic input.

    If <user_payload> XML tags are present, extracts and concatenates only the
    inner text of all <user_payload>...</user_payload> blocks, stripping XML wrapper
    tags and ignoring <ai_draft_context> AI response blocks. If no <user_payload>
    tags are present, returns the stripped raw text.

    Args:
        text: Raw string input from dynamic inputs.

    Returns:
        Extracted user content with XML tags and AI responses excluded.
    """
    if "<user_payload>" in text:
        matches = re.findall(r"<user_payload>(.*?)</user_payload>", text, flags=re.DOTALL)
        return "\n\n".join(m.strip() for m in matches if m.strip())
    return text.strip()


def _is_preflight_candidate_key(key: str, excluded_keys: list[str]) -> bool:
    """Determine whether an input key represents a primary analytical document for preflight.

    Excludes non-analytical metadata keys (such as document_date) as well as auxiliary
    projections produced by InputProcessingHook (such as chat_log_user_only or chat_log_ai_only).

    Args:
        key: Input key name.
        excluded_keys: Central list of excluded keys from settings.

    Returns:
        True if the key represents a primary candidate document, False otherwise.
    """
    if key in excluded_keys:
        return False
    if key.endswith("_user_only") or key.endswith("_ai_only"):
        return False
    return True


def _extract_inputs_from_record(exec_record: ExecutionRecord) -> dict[str, Any]:
    """Extract input dictionary from execution trace (processed) or fallback to raw inputs.

    Args:
        exec_record: ExecutionRecord containing trace events and raw inputs.

    Returns:
        Dictionary of dynamic inputs.
    """
    for event in reversed(exec_record.execution_trace):
        if event.step_name == "inputs" and event.event_type == "input" and isinstance(event.content, dict):
            inputs_payload = event.content.get("inputs")
            if isinstance(inputs_payload, dict):
                return inputs_payload
    return dict(exec_record.raw_inputs.dynamic_inputs)


class RAGPreflightService:
    """Service for RAG knowledge extraction phase 1B."""

    def __init__(
        self,
        workflow_repo: IWorkflowRepository,
        system_repo: ISystemRepository,
        prompt_compiler: PromptCompiler,
    ) -> None:
        """Initialize RAG Preflight Service.

        Args:
            workflow_repo: Workflow repository interface.
            system_repo: System repository interface.
            prompt_compiler: Compiler engine dynamic handler.
        """
        self.workflow_repo = workflow_repo
        self.system_repo = system_repo
        self.compiler = prompt_compiler

    async def execute(
        self,
        target_step: StepRule,
        step_def: Step,
        exec_record: ExecutionRecord,
        emit_progress: Callable[[str, int], Awaitable[None]],
    ) -> dict[str, Any]:
        """Phase 1B RAG Pre-flight Pipeline execution.

        Args:
            target_step: The step triggering the synthesis.
            step_def: The pre-fetched definition of the target step.
            exec_record: Current execution record to extract inputs from.
            emit_progress: Callback to push progress events.

        Returns:
            The serialized GlobalAtomBlackboard payload.

        Raises:
            AppException: If task_blueprint is missing (CONFIGURATION_ERROR).
            AppException: If model_strategy is missing (CONFIGURATION_ERROR).
            AppException: If atom ceiling is exceeded (VALIDATION_FAILED).
        """
        if not target_step.task_blueprint:
            raise AppException(
                message="Target synthesis step missing task_blueprint.",
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                status_code=500,
            )

        strategy_name = step_def.model_strategy
        if not strategy_name:
            raise AppException(
                message=f"Blueprint {target_step.task_blueprint} has no model_strategy.",
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                status_code=500,
            )

        inputs = _extract_inputs_from_record(exec_record)
        settings = get_settings()

        candidate_inputs = {
            k: v
            for k, v in inputs.items()
            if isinstance(v, str) and _is_preflight_candidate_key(k, settings.rag_preflight_excluded_keys)
        }

        total_input_chars = sum(len(_extract_effective_user_text(v)) for v in candidate_inputs.values())

        if total_input_chars < settings.rag_preflight_min_input_chars:
            logger.warning(
                "RAGPreflightService: Total analytical input characters (%d) is below minimum threshold (%d). "
                "Skipping LLM atomization.",
                total_input_chars,
                settings.rag_preflight_min_input_chars,
            )
            await emit_progress("Input data sparse/empty. Preflight extraction skipped.", 100)
            return GlobalAtomBlackboard(atoms_by_input={}, is_data_starved=True).model_dump(mode="json")

        bound_client = await LLMClient.from_strategy(strategy_name, self.system_repo, pipeline_name="chunk_worker")
        llm_executor = LLMTaskExecutor(self.compiler)
        atomizer = TwoPassAtomizer(llm_executor)

        candidate_files = [k for k, v in candidate_inputs.items() if len(_extract_effective_user_text(v)) >= 20]
        total_files = len(candidate_files)
        processed_files = 0
        atoms_by_input = {}

        for key, text_content in candidate_inputs.items():
            if key not in candidate_files:
                continue

            await emit_progress(
                f"Extracting knowledge from file {processed_files + 1}/{total_files}...",
                int(processed_files / total_files * 100),
            )

            alias_engine = AliasEngine()
            paragraphs = [p.strip() for p in text_content.split("\n\n") if p.strip()]
            numbered_lines = []
            for p in paragraphs:
                block_id = alias_engine.register(p, prefix="B")
                numbered_lines.append(f"[{block_id}] {p}")
            hydrated_text = "\n\n".join(numbered_lines)

            base_progress = (processed_files / total_files) * 100
            local_slice = 100 / total_files

            async def phase_0_progress(
                completed: int,
                total: int,
                pf: int = processed_files,
                tf: int = total_files,
                bp: float = base_progress,
                ls: float = local_slice,
            ) -> None:
                prog = int(bp + ((completed / total) * 0.3 * ls))
                await emit_progress(f"Extracting knowledge from file {pf + 1}/{tf}... (Mapping)", prog)

            ontology = await atomizer.execute_phase_0(bound_client, hydrated_text, progress_callback=phase_0_progress)

            async def phase_1_progress(
                completed: int,
                total: int,
                pf: int = processed_files,
                tf: int = total_files,
                bp: float = base_progress,
                ls: float = local_slice,
            ) -> None:
                prog = int(bp + (0.3 * ls) + ((completed / total) * 0.7 * ls))
                await emit_progress(f"Extracting knowledge from file {pf + 1}/{tf}... (Reducing)", prog)

            draft_list = await atomizer.execute_phase_1_drafts(
                bound_client, hydrated_text, ontology, progress_callback=phase_1_progress
            )

            if len(draft_list.atoms) > settings.max_extracted_atoms_per_document:
                raise AppException(
                    message=f"Atom ceiling exceeded for file {key}. Extracted {len(draft_list.atoms)} atoms.",
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                    status_code=400,
                )

            atoms_by_input[key] = draft_list
            processed_files += 1

        await emit_progress("Knowledge extraction complete.", 100)

        blackboard = GlobalAtomBlackboard(atoms_by_input=atoms_by_input)
        return blackboard.model_dump(mode="json")
