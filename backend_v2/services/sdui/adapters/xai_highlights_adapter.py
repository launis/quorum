"""XAI Highlights SDUI Adapter.

Transforms extracted XAI extensions into polymorphic AnySduiBlock components
for Server-Driven UI rendering. Visual rules are co-located as a module-level
XAI_AESTHETICS_RULES dictionary to enforce separation of presentation from logic.
"""

import logging
from typing import Any, Literal, cast

from pydantic import ValidationError

from backend_v2.exceptions import AppException, ConfigurationError, ErrorCodes
from backend_v2.models.dtos.lightweight_matrix import LightweightMatrixOutput
from backend_v2.models.dtos.trace import TraceMatrixPayloadDTO
from backend_v2.models.enums import VisualIntent, XaiExtensionType
from backend_v2.models.state import StateProjector
from backend_v2.models.view.sdui import AccordionBlock, AlertBlock, AnySduiBlock
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext

logger = logging.getLogger(__name__)


# ============================================================================
# SECTION 1: AESTHETICS RULES
# ============================================================================
XAI_AESTHETICS_RULES: dict[str, dict[str, VisualIntent]] = {
    "coaching": {"severity": VisualIntent.SUCCESS},
    "falsification": {"severity": VisualIntent.ERROR},
    "risk_flag": {"severity": VisualIntent.ERROR},
    "remediation_steps": {"severity": VisualIntent.WARNING},
    "missing_context": {"severity": VisualIntent.WARNING},
    "emotional_sentiment": {"severity": VisualIntent.INFO},
    "theory_link": {"severity": VisualIntent.INFO},
}


# ============================================================================
# SECTION 2: ADAPTER CLASS
# ============================================================================
class XaiHighlightsAdapter:
    """Transforms XAI highlights into SDUI visual blocks.

    Uses co-located XAI_AESTHETICS_RULES for all aesthetic decisions.
    Stateless: no instance state, no side effects.
    """

    @staticmethod
    def build(context: AdapterContext) -> list[AnySduiBlock]:
        """Build SDUI blocks from the adapter context.

        Args:
            context: Frozen, immutable adapter context containing all
                required data for block construction.

        Returns:
            Ordered list of polymorphic SDUI blocks ready for rendering.
        """
        blocks: list[AnySduiBlock] = []

        if not context.execution or not context.execution.execution_trace:
            return blocks

        projector = StateProjector()
        results = projector.fold_trace(context.execution.execution_trace)

        profile = context.profile
        locale = context.locale

        global_exts: list[AccordionBlock] = []

        for dto in results:
            if not isinstance(dto.payload, dict):
                continue

            try:
                mapped_block_data = LightweightMatrixOutput.map_llm_extensions_to_domain(dto.payload)
                matrix_payload = TraceMatrixPayloadDTO.model_validate(mapped_block_data)
            except ValidationError:
                continue

            ext = matrix_payload.extensions
            if not ext:
                continue

            def _add_ext(key: str, val: Any) -> None:
                if not val:
                    return

                try:
                    ext_enum = XaiExtensionType(key)
                except ValueError as v_err:
                    msg = f"Invalid XaiExtensionType key '{key}'"
                    logger.error("[XaiHighlightsAdapter] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                    raise AppException(
                        message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
                    ) from v_err

                try:
                    aesthetics = XAI_AESTHETICS_RULES[key]
                except KeyError as e:
                    msg = f"Missing rule mapping for extension key: {key}"
                    logger.error("[XaiHighlightsAdapter] CONFIGURATION_ERROR: %s", msg, exc_info=True)
                    raise AppException(
                        message=msg,
                        status_code=500,
                        details={"error_code": "CONFIGURATION_ERROR"},
                    ) from e

                label_obj = profile.extension_labels.get(ext_enum) if profile.extension_labels else None
                if not label_obj:
                    raise ConfigurationError(
                        f"Missing extension label configuration for {key} in profile SSOT",
                        details={"extension_key": key},
                    )

                if profile.visible_block_extensions and ext_enum in profile.visible_block_extensions:
                    lines = list(dict.fromkeys(line.strip() for line in str(val).split("\n") if line.strip()))
                    label_str = label_obj.resolve(locale)

                    acc_severity = aesthetics["severity"]

                    acc_severity_literal = cast(
                        Literal["info", "warning", "critical_override", "success", "error", "default"],
                        acc_severity.value,
                    )

                    max_lines = profile.max_extension_items if profile.max_extension_items else 999

                    accordion = next(
                        (b for b in global_exts if b.title == label_str),
                        None,
                    )
                    if not accordion:
                        accordion = AccordionBlock(
                            title=label_str, severity=acc_severity_literal, icon_name=None, children=[]
                        )
                        global_exts.append(accordion)

                    for line in lines:
                        if len(accordion.children) >= max_lines:
                            break
                        if not any(isinstance(c, AlertBlock) and c.text == line for c in accordion.children):
                            block = AlertBlock(
                                severity=VisualIntent.INFO,
                                text=f"**{label_str}**: {line}",
                                exact_quotes=[],
                                citations=[],
                            )
                            accordion.children.append(block)

            _add_ext("coaching", ext.coaching)
            _add_ext("falsification", ext.falsification)
            _add_ext("remediation_steps", ext.remediation_steps)
            _add_ext("missing_context", ext.missing_context)
            _add_ext("emotional_sentiment", ext.emotional_sentiment)
            _add_ext("theory_link", ext.theory_link)
            _add_ext("risk_flag", ext.risk_flag)

        blocks.extend(cast(list[AnySduiBlock], global_exts))
        return blocks
