"""Deterministic Input Processing Hook for V2 Architecture.

This hook replaces the legacy V1 `InputProcessorAgent` LLM overhead.
It safely merges and transforms structured `guided_reflection` questionnaires 
and unstructured `reflection_text` strings into a unified text format for downstream AI nodes.
"""

import logging
from typing import Any

from fastapi import status

from backend_v2.core.hook_registry import hook_registry
from backend_v2.exceptions import AppException, ErrorCodes

import base64
import io
import fitz
import logging
from fastapi.concurrency import run_in_threadpool

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


@hook_registry.register(name="process_inputs")
async def process_inputs(data: dict[str, Any]) -> dict[str, Any]:
    """HOOK: process_inputs.

    Reads raw input modalities passed from the client, normalizes them, 
    extracts PDF text if base64 encoded, and handles transformations like expanding 
    `guided_reflection` into an alternative Markdown document via V1 compatibility logic.
    """
    logger.info("[InputProcessingHook] Running deterministic input normalizer...")

    # In V2 DAGExecutor, raw_inputs from the payload are flattened into the root state_data dictionary
    history_text = await resolve_input(data.get("history_text", ""))
    product_text = await resolve_input(data.get("product_text", ""))
    reflection_text = await resolve_input(data.get("reflection_text", ""))
    guided_reflection = data.get("guided_reflection")

    # 1. Transform Guided Reflection to Markdown if provided
    # Note: Guided reflection is an alternative input to a direct reflection_text document.
    if guided_reflection and isinstance(guided_reflection, dict):
        logger.info("[InputProcessingHook] Found guided_reflection dict. Generating alternative Markdown reflection...")
        try:
            markdown_parts = ["# Guided Reflection\n"]
            keys = sorted(guided_reflection.keys())
            for key in keys:
                val = guided_reflection[key]
                if str(key).startswith("q"):
                    markdown_parts.append(f"### Q: {val}")
                elif str(key).startswith("a"):
                    markdown_parts.append(f"**A:** {val}\n")
                else:
                    markdown_parts.append(f"**{key}:** {val}\n")
            
            # Form the reflection_text entirely from the questionnaire 
            # (as it's an alternative to a direct uploaded document)
            reflection_text = "\n".join(markdown_parts)
                
            logger.debug("[InputProcessingHook] Successfully transformed guided reflection.")
        except Exception as e:
            logger.error(f"[InputProcessingHook] Failed to parse guided_reflection: {e}")
            # Do not fail fast here, graceful degradation to original text if possible

    # 2. V2 ChatParser LLM Hook (Y-Funnel equivalent)
    # If history_text is present and is raw text (not already parsed JSON)
    if history_text and not history_text.strip().startswith("{"):
        logger.info("[InputProcessingHook] Unstructured history_text detected. Invoking ChatParserLLM...")
        try:
            from backend_v2.services.chat_parser import ChatParserService
            repo = data.get("_sys_repository")
            if not repo:
                logger.warning("[InputProcessingHook] _sys_repository missing; LLM parser might fail if not mocked.")
                
            chat_dto = await ChatParserService.parse_pasted_chat(history_text, repository=repo)
            # Serialize the structured DTO back to a JSON string so downstream PromptCompilers can safely embed it
            history_text = chat_dto.model_dump_json(indent=2)
            logger.info("[InputProcessingHook] Successfully structured history_text via ChatParser.")
        except Exception as e:
            logger.error(f"[InputProcessingHook] Chat parsing failed: {e}")
            # Fail-fast bubble up to match V1 specification
            if isinstance(e, AppException):
                raise e
            raise AppException(
                message="Failed to parse unstructured chat history using AI.",
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": "CHAT_PARSING_FAILED"}
            ) from e

    # 3. Construct and return the output dictionary.
    # The DAG engine mounts this dict exactly to `$steps.<this_step_id>.<key>`
    return {
        "history_text": history_text,
        "product_text": product_text,
        "reflection_text": reflection_text.strip(),
        "status": "Inputs processed deterministically (or structured via LLM if needed)."
    }
