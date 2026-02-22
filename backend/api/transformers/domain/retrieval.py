import logging

from pydantic import ValidationError

from backend.exceptions import AppException
from backend.models.domain import ContextData
from backend.models.enums import TitleKey

# UVM Refactor: Use strict extensions
from backend.models.view import EvidenceItem, EvidenceList, SectionType, UiSection

# Deprecated: from backend.models.view_extensions import EvidenceList, EvidenceItem
from ..base import BaseTransformer

logger = logging.getLogger(__name__)


class RetrievalDomainTransformer(BaseTransformer):
    def _extract_context_section(self, steps: dict) -> UiSection | None:
        step = steps.get("step_context")
        if not step:
            return None

        # STRICT VALIDATION
        try:
            # Handle wrapped vs flat
            if "context_data" in step:
                model = ContextData(**step["context_data"])
            else:
                model = ContextData(**step)
        except ValidationError as e:
            error_code = "CONTEXT_VALIDATION_FAILED"
            logger.error(f"{error_code}: {e}", exc_info=True)
            raise AppException(
                message=f"Context validation failed: {e}",
                status_code=500,
                details={"error_code": error_code, "errors": e.errors()},
            ) from e
        except Exception as e:
            error_code = "CONTEXT_VALIDATION_FAILED"
            logger.error(f"{error_code}: {e}", exc_info=True)
            raise AppException(message=str(e), status_code=500, details={"error_code": error_code}) from e

        try:
            display_model = self._transform_context_data(model)
            return UiSection(
                id="context-display",
                type=SectionType.EVIDENCE_LIST,
                title=self._get_title(TitleKey.CONTEXT),
                data=display_model,
            )
        except Exception as e:
            raise AppException(f"Failed to transform Context display: {e}", 500) from e

    def _transform_context_data(self, model: ContextData) -> EvidenceList:
        """Transforms ContextData into strict EvidenceList model."""
        items = []

        # 1. Knowledge Items (Primary)
        if model.knowledge_items:
            for item in model.knowledge_items:
                items.append(
                    EvidenceItem(
                        id=item.id,
                        source=item.source,
                        content=f"**{item.term}** - {item.definition}",
                        score=item.score,
                        type="regulation" if "regulation" in item.type else "concept",
                    )
                )

        # 2. Precedents (Secondary - Legacy String)
        if model.precedents:
            # Create a pseudo-item for the block
            items.append(
                EvidenceItem(
                    id="precedents-block",
                    source="Precedent Database",
                    content=model.precedents,
                    score=1.0,
                    type="precedent",
                )
            )

        return EvidenceList(items=items, total_count=len(items))
