"""Matrix level distribution and row explanation formatting utilities."""

from __future__ import annotations

import logging
import re

from fastapi import status

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.dtos.lightweight_matrix import LevelStatsDTO
from backend_v2.services.localization import LocalizationService

__all__ = [
    "clean_hallucinated_numbers",
    "format_level_breakdown",
    "format_level_distribution",
    "resolve_row_explanation",
]

logger = logging.getLogger(__name__)


# Phase 1, Step 2: Relocate leaf distribution and explanation formatting functions
def format_level_distribution(lvl_data: LevelStatsDTO, locale: str) -> str:
    """Formats the empirical scale distribution according to Model B architecture.

    Args:
        lvl_data: The LevelStatsDTO containing decomposed affirmative and inverse counts.
        locale: Language string ('fi' or 'en').

    Returns:
        Formatted distribution string adhering to Dumb Painter SDUI contract.
    """
    k_pos = lvl_data.pos_hits
    n_pos = lvl_data.pos_total
    k_clean = lvl_data.inv_clean
    n_inv = lvl_data.inv_total

    skills_word = LocalizationService.translate("matrix_dist_skills", lang=locale)
    purity_word = LocalizationService.translate("matrix_dist_purity", lang=locale)
    defect_singular = LocalizationService.translate("matrix_dist_defect", lang=locale)
    defect_plural = LocalizationService.translate("matrix_dist_defects", lang=locale)

    # Rule 1: Pure Capability Level (N_pos > 0 and N_inv == 0)
    if n_pos > 0 and n_inv == 0:
        if n_pos == 1:
            return f"{k_pos}/{n_pos}"
        return f"{k_pos}/{n_pos} {skills_word}"

    # Rule 2: Pure Error Radar Level (N_pos == 0 and N_inv > 0)
    if n_pos == 0 and n_inv > 0:
        d_inv = n_inv - k_clean
        if d_inv == 0:
            return f"{purity_word} {k_clean}/{n_inv}"
        defect_label = defect_singular if d_inv == 1 else defect_plural
        return f"{purity_word} {k_clean}/{n_inv} (⚠️ {d_inv} {defect_label})"

    # Rule 3: Hybrid Level (N_pos > 0 and N_inv > 0)
    if n_pos > 0 and n_inv > 0:
        skills_part = f"{k_pos}/{n_pos}" if n_pos == 1 else f"{k_pos}/{n_pos} {skills_word}"
        d_inv = n_inv - k_clean
        if d_inv == 0:
            purity_part = f"{purity_word} {k_clean}/{n_inv}"
        else:
            defect_label = defect_singular if d_inv == 1 else defect_plural
            purity_part = f"{purity_word} {k_clean}/{n_inv} (⚠️ {d_inv} {defect_label})"
        return f"{skills_part}, {purity_part}"

    # Rule 5: Unpartitioned Count Normalization (N_pos == 0 and N_inv == 0)
    hits = int(lvl_data.hits)
    total = int(lvl_data.total)
    return f"{hits}/{total}"


def clean_hallucinated_numbers(text: str) -> str:
    """Removes sentences that contain numeric evaluations to prevent hallucinations.

    Args:
        text: Raw input text.

    Returns:
        Cleaned text string.
    """
    if not text:
        return ""

    sentences = re.split(r"(?<=[.!?]) +", text)
    cleaned = []

    # Regex checks for words like taso, tason, tasolle, arvosana,
    # piste etc. followed by an optional colon and a number
    pattern = re.compile(r"(?i)(taso|arvosana|level|piste|score|grade)[a-zäö]*\s*:?\s*\d")

    for s in sentences:
        if not pattern.search(s):
            cleaned.append(s)

    return " ".join(cleaned).strip()


def format_level_breakdown(
    raw_breakdown: dict[str, LevelStatsDTO] | None,
    locale: str,
    block_id: str,
) -> dict[str, str] | None:
    """Validates numeric level keys and formats the level breakdown dictionary.

    Args:
        raw_breakdown: Raw level breakdown mapping from matrix payload.
        locale: Target language locale string.
        block_id: Canonical matrix PromptBlock identifier.

    Returns:
        Formatted mapping of normalized level key to distribution string, or None.

    Raises:
        AppException: If a level key cannot be parsed as a float (ErrorCodes.VALIDATION_FAILED).
    """
    if not raw_breakdown:
        return None

    clean_level_dict: dict[str, str] = {}
    for lvl_key, lvl_data in raw_breakdown.items():
        try:
            f_lvl = float(lvl_key)
            is_int = f_lvl.is_integer()
            if is_int:
                c_key = str(int(f_lvl))
            else:
                c_key = str(lvl_key)
            clean_level_dict[c_key] = format_level_distribution(lvl_data, locale)
        except ValueError as v_err:
            logger.error(
                "[MatrixDomainParser] %s: Fail-Fast: Invalid level key '%s' in matrix breakdown for '%s'.",
                ErrorCodes.VALIDATION_FAILED.name,
                lvl_key,
                block_id,
                exc_info=True,
            )
            raise AppException(
                message=f"Fail-Fast: Invalid level key '{lvl_key}' in matrix breakdown for '{block_id}'.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            ) from v_err
    return clean_level_dict


def resolve_row_explanation(
    block_id: str,
    profile: OutputProfile,
    row_explanations_cache: dict[str, str],
    has_synthesis_cache: bool,
    execution: ExecutionRecord | None = None,
) -> str:
    """Resolves and sanitizes the synthesized row explanation for a matrix block.

    Args:
        block_id: Canonical matrix PromptBlock identifier.
        profile: Active OutputProfile governing row explanation requirements.
        row_explanations_cache: Mapping of block ID to synthesized row explanation text.
        has_synthesis_cache: Whether synthesis cache is expected to be present.
        execution: Optional ExecutionRecord instance for checking data starvation state.

    Returns:
        Sanitized row explanation string with hallucinated numbers removed.

    Raises:
        AppException: If row explanation synthesis is required and not data-starved,
            but the block ID is missing from row_explanations_cache (ErrorCodes.CONFIGURATION_ERROR).
    """
    synthesis_expected = profile.requires_row_explanations and has_synthesis_cache
    is_data_starved = False
    if execution and execution.profile_syntheses:
        current_cache = None
        if profile.id in execution.profile_syntheses:
            current_cache = execution.profile_syntheses[profile.id]
        if current_cache and current_cache.data_starvation is not None:
            is_data_starved = True

    final_explanation = ""
    if synthesis_expected and not is_data_starved:
        if block_id not in row_explanations_cache:
            msg = (
                f"Fail-Fast: row_explanations_cache missing entry for matrix '{block_id}'. Worker synthesis incomplete."
            )
            logger.error("[MatrixDomainParser] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
            raise AppException(
                message=msg,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )
        final_explanation = row_explanations_cache[block_id]
    elif block_id in row_explanations_cache:
        final_explanation = row_explanations_cache[block_id]

    return clean_hallucinated_numbers(final_explanation)
