"""Deterministic Input Processing Hook for V2 Architecture.

This hook replaces the legacy V1 `InputProcessorAgent` LLM overhead.
It safely merges and transforms structured `guided_reflection` questionnaires
and unstructured `reflection_text` strings into a unified text format for downstream AI nodes.
"""

import base64
import logging
from typing import Any

import fitz
from fastapi import status
from fastapi.concurrency import run_in_threadpool

from backend_v2.core.hook_registry import hook_registry
from backend_v2.exceptions import AppException

logger = logging.getLogger(__name__)

def _extract_pdf(file_bytes: bytes) -> str:
    """CPU-bound hook helper to extract text strictly from PDF bytes via PyMuPDF."""
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text.strip()

async def resolve_input(val: Any) -> str:
    """Helper to detect Base64 V1-style payloads and route them strictly to extraction."""
    if isinstance(val, dict) and "content_base64" in val:
        file_bytes = base64.b64decode(val["content_base64"])
        filename = val.get("filename", "unknown.txt").lower()
        logger.info(f"[InputProcessingHook] Detected binary input payload: {filename}")

        if filename.endswith(".pdf"):
            logger.info(f"[InputProcessingHook] Running PyMuPDF extraction for {filename}")
            try:
                extracted = await run_in_threadpool(_extract_pdf, file_bytes)
                logger.debug(f"[InputProcessingHook] Extracted {len(extracted)} chars from {filename}")
                return extracted
            except Exception as e:
                # V2 STRICT FAIL-FAST
                raise AppException(
                    message=f"Failed to extract text from PDF {filename}",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details={"error_code": "FILE_EXTRACTION_FAILED", "original_error": str(e)}
                ) from e
        else:
            return file_bytes.decode("utf-8", errors="ignore")
    elif isinstance(val, str):
        return val
    return str(val) if val else ""


@hook_registry.register(name="input_processing")
async def process_inputs(data: dict[str, Any]) -> dict[str, Any]:
    """HOOK: input_processing.

    Reads raw input modalities passed from the client, normalizes them,
    extracts PDF text if base64 encoded, and handles transformations like expanding
    `questionnaire` inputs into Markdown documents. Uses is_chat_history flag to
    dynamically route unstructured text to ChatParserService.
    """
    logger.info("[InputProcessingHook] Running deterministic input normalizer...")

    # Fetch workflow to know about expected_inputs
    repo = data.get("_sys_repository")
    workflow_id = data.get("_sys_workflow_id")

    if not repo or not workflow_id:
        logger.error("[InputProcessingHook] Missing repository or workflow_id in context.")
        raise AppException(
            message="Missing execution context for input processing.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": "MISSING_EXECUTION_CONTEXT"}
        )

    workflow_dict = await repo.get_workflow_by_id(workflow_id)
    if not workflow_dict:
        raise AppException(
            message=f"Workflow {workflow_id} not found.",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"error_code": "WORKFLOW_NOT_FOUND"}
        )

    from pydantic import TypeAdapter

    from backend_v2.models.v2_core import Workflow
    workflow = TypeAdapter(Workflow).validate_python(workflow_dict)

    expected_inputs = workflow.expected_inputs
    output_dict: dict[str, str] = {}

    for expected_input in expected_inputs:
        key = expected_input.input_key
        raw_val = data.get(key)

        # 1. Handle Questionnaire mode specifically if it exists
        if isinstance(raw_val, dict) and any(str(k).startswith("q") for k in raw_val.keys()):
            logger.info(f"[InputProcessingHook] Found questionnaire dict for {key}. Generating Markdown...")
            title_text = expected_input.label.translations.get("en", "Questionnaire")
            markdown_parts = [f"# {title_text}\n"]
            keys = sorted(raw_val.keys())
            for q_key in keys:
                val = raw_val[q_key]
                if str(q_key).startswith("q"):
                    markdown_parts.append(f"### Q: {val}")
                elif str(q_key).startswith("a"):
                    markdown_parts.append(f"**A:** {val}\n")
                else:
                    markdown_parts.append(f"**{q_key}:** {val}\n")
            resolved_text = "\n".join(markdown_parts)

        else:
            # 2. Standard resolution (File, Paste)
            resolved_text = await resolve_input(raw_val)

        # 3. V2 ChatParser LLM Hook (if designated as chat history)
        if expected_input.is_chat_history and resolved_text and not resolved_text.strip().startswith("{"):
            logger.info(f"[InputProcessingHook] Unstructured chat detected for {key}. Invoking ChatParserLLM...")
            try:
                from backend_v2.services.chat_parser import ChatParserService

                chat_dto = await ChatParserService.parse_pasted_chat(resolved_text, repository=repo)
                
                # Format to Markdown instead of raw JSON to prevent \n escaping in LLM prompt
                chat_lines = []
                for turn in chat_dto.conversation:
                     chat_lines.append(f"**{turn.role}**: {turn.content}")
                resolved_text = "\n\n".join(chat_lines)
                
                logger.info(f"[InputProcessingHook] Successfully structured {key} via ChatParser (Markdown).")
            except Exception as e:
                logger.error(f"[InputProcessingHook] Chat parsing failed for {key}: {e}")
                if isinstance(e, AppException):
                    raise e
                raise AppException(
                    message=f"Failed to parse unstructured chat for {key} using AI.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details={"error_code": "CHAT_PARSING_FAILED"}
                ) from e

        # 4. Injektoidaan `ai_description` suoraan raakatekstin yläpuolelle (Universal Routing)
        lang_code = data.get("language", "fi")
        if expected_input.ai_description and hasattr(expected_input.ai_description, "translations"):
            desc_text = expected_input.ai_description.translations.get(lang_code, expected_input.ai_description.default_locale)
            if desc_text:
                logger.info(f"[InputProcessingHook] Injecting ai_description for {key}.")
                if lang_code == "fi":
                    header = f"--- TEKOÄLYN OHJEISTUS TÄLLE LÄHTEELLE ({key}) ---\n"
                    footer = f"\n--- LÄHDE: {key} ---"
                else:
                    header = f"--- AI INSTRUCTION FOR THIS SOURCE ({key}) ---\n"
                    footer = f"\n--- SOURCE: {key} ---"
                resolved_text = f"{header}{desc_text}{footer}\n{resolved_text}"

        output_dict[key] = resolved_text.strip()

    return {"inputs": output_dict}
