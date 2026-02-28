import logging
from collections.abc import Sequence
from datetime import datetime
from typing import Any

from backend.exceptions import AppException
from backend.models.enums import LabelKey, TitleKey
from backend.models.state import TraceEvent
from backend.services.localization import LocalizationService

logger = logging.getLogger(__name__)


class BaseTransformer:
    def __init__(self, language: str = "en"):
        self.language = language
        self.loc = LocalizationService()

    def _t(self, key: str, default: str) -> str:
        return self.loc.get(key, self.language, default)

    def _get_title(self, key: TitleKey) -> str:
        """Fetches translated title using TitleKey Enum. Fallback to Title Case of Enum name."""
        return self._t(key.value, default=key.name.replace("_", " ").title())

    def _get_label(self, key: LabelKey) -> str:
        """Fetches translated label using LabelKey Enum."""
        return self._t(key.value, default=key.name.replace("_", " ").title())

    def _format_date(self, timestamp_str: str | None) -> str:
        """Formats ISO timestamp to locale-specific string."""
        if not timestamp_str:
            return ""

        try:
            # Parse ISO string (e.g. "2026-02-12T10:00:00")
            dt = datetime.fromisoformat(str(timestamp_str).replace("Z", "+00:00"))

            if self.language == "fi":
                return dt.strftime("%d.%m.%Y %H:%M")
            else:
                return dt.strftime("%Y-%m-%d %H:%M")
        except Exception as e:
            logger.warning(f"Date formatting failed for '{timestamp_str}': {e}")
            return str(timestamp_str)

    def _format_number(self, value: float | int | None, decimals: int = 0, percent: bool = False) -> str:
        """Formats a number based on locale (fi-FI vs en-US)."""
        if value is None:
            return "-"

        # Basic Locale Logic (Expand if using Babel later)
        is_fi = self.language == "fi"

        # 2. Formatting
        try:
            # Python f-string doesn't support locale unaware custom separators easily without locale module.
            # Manual implementation for safety/strictness.

            # Rounding
            rounded = round(value, decimals)
            if decimals == 0:
                rounded = int(rounded)

            s = f"{rounded}"

            # Decimal separator
            if is_fi:
                s = s.replace(".", ",")

            # Thousand separator (Space for FI, Comma for EN)

            # Default (EN-ish)
            s_en = f"{rounded:,}"  # 1,200.5

            if is_fi:
                # 1 200,5
                s_fi = s_en.replace(",", " ").replace(".", ",")
                return f"{s_fi} %" if percent else s_fi
            else:
                return f"{s_en}%" if percent else s_en

        except Exception as e:
            logger.warning(f"Number formatting failed for '{value}': {e}")
            return str(value)

    def _reconstruct_state_from_trace(self, trace: Sequence[TraceEvent | dict[str, Any]]) -> dict[str, Any]:
        """Reconstructs the 'step_results' map from an append-only linear trace."""
        reconstructed = {}

        try:
            for event in trace:
                # Handle both Pydantic TraceEvent and legacy dict
                evt_type = event.event_type if isinstance(event, TraceEvent) else event.get("event_type")

                # We are interested in OUTPUT events
                if evt_type == "output":
                    step_name = event.step_name if isinstance(event, TraceEvent) else event.get("step_name")

                    if not step_name or not isinstance(step_name, str):
                        continue

                    # Modern output paths use UUID as step_name and `task_key` in metadata.
                    # We remap the UUID to the domain key (`step_<task_key>`).
                    evt_meta = event.metadata if isinstance(event, TraceEvent) else event.get("metadata", {})
                    task_key = evt_meta.get("task_key")
                    if task_key:
                        step_name = f"step_{task_key}"

                    # Content handling
                    if isinstance(event, TraceEvent):
                        content = event.content.copy() if event.content else {}
                        reasoning = event.reasoning
                        timestamp = event.timestamp
                    else:
                        content = event.get("content", {}) or {}
                        # Copy to avoid mutation if shared ref (though strict dict usually new)
                        if isinstance(content, dict):
                            content = content.copy()
                        reasoning = event.get("reasoning")
                        timestamp = event.get("timestamp") or evt_meta.get("timestamp")

                    # Check for reasoning trace availability (optional optimization)
                    if reasoning:
                        if isinstance(reasoning, dict):
                            content["reasoning_trace"] = reasoning.get("thought_process")
                        elif hasattr(reasoning, "thought_process"):  # Pydantic ReasoningTrace
                            content["reasoning_trace"] = reasoning.thought_process

                    # Timestamp to metadata
                    if timestamp:
                        if content.get("metadata") is None:
                            content["metadata"] = {}

                        # Normalize Pydantic datetime to string for Dict compatibility (or keep object?)

                        # KEEP ORIGINAL for Pydantic Validation:
                        content["metadata"]["luontiaika"] = timestamp
                        # Add formatted for UI:
                        content["metadata"]["luontiaika_formatted"] = self._format_date(str(timestamp))

                    reconstructed[step_name] = content
        except Exception as e:
            raise AppException(f"Failed to reconstruct state from trace: {e}", 500) from e

        return reconstructed
