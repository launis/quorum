"""Service for extracting knowledge during RAG Preflight."""

import logging
from collections.abc import Awaitable, Callable
from typing import Any

from backend_v2.database.interfaces import ISystemRepository, IWorkflowRepository
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.llm.client import LLMClient
from backend_v2.models.domain.blackboard import GlobalAtomBlackboard
from backend_v2.models.v2_core import ExecutionRecord, Step, StepRule
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.orchestrator.two_pass_atomizer import TwoPassAtomizer
from backend_v2.settings import get_settings

logger = logging.getLogger(__name__)


class RAGPreflightService:
    """Service for RAG knowledge extraction phase 1B."""

    def __init__(
        self,
        workflow_repo: IWorkflowRepository,
        system_repo: ISystemRepository,
        prompt_compiler: Any,
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

        bound_client = await LLMClient.from_strategy(strategy_name, self.system_repo, pipeline_name="chunk_worker")
        llm_executor = LLMTaskExecutor(self.compiler)
        atomizer = TwoPassAtomizer(llm_executor)

        inputs_payload = exec_record.raw_inputs.model_dump(mode="json")
        dynamic_inputs = inputs_payload.get("dynamic_inputs", {})
        atoms_by_input = {}

        total_files = len([k for k, v in dynamic_inputs.items() if isinstance(v, str)])
        processed_files = 0

        for key, text_content in dynamic_inputs.items():
            if not isinstance(text_content, str):
                continue

            await emit_progress(
                f"Extracting knowledge from file {processed_files + 1}/{total_files}...",
                int(processed_files / total_files * 100),
            )

            chunk_size = get_settings().rag_preflight_chunk_size
            text_chunks = [text_content[i : i + chunk_size] for i in range(0, max(len(text_content), 1), chunk_size)]

            max_dev_chunks = get_settings().max_development_chunks
            if max_dev_chunks > 0 and len(text_chunks) > max_dev_chunks:
                logger.warning(
                    "[DEV MODE] Slicing text_chunks from %d to %d to save tokens.", len(text_chunks), max_dev_chunks
                )
                text_chunks = text_chunks[:max_dev_chunks]

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

            ontology = await atomizer.execute_phase_0(bound_client, text_chunks, progress_callback=phase_0_progress)

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
                bound_client, text_chunks, ontology, progress_callback=phase_1_progress
            )

            if len(draft_list.atoms) > get_settings().max_extracted_atoms_per_document:
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
