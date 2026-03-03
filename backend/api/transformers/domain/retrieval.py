import logging

from backend.models.domain import ContextData
from backend.models.enums import TitleKey
from backend.models.state import WorkflowState

# UVM Refactor: Use strict extensions
from backend.models.view.semantic_models import BlockType, EvidenceItem, EvidenceList, SemanticBlock

# Deprecated: from backend.models.view.semantic_models_extensions import EvidenceList, EvidenceItem
from ..base import BaseTransformer

logger = logging.getLogger(__name__)


class RetrievalDomainTransformer(BaseTransformer):
    def _extract_context_section(self, state: WorkflowState) -> SemanticBlock | None:
        model = state.get_context("step_context", ContextData)
        if not model:
            return None

        try:
            display_model = self._transform_context_data(model)
            return SemanticBlock(id="context-display",
                type=BlockType.LIST,
                label=self._get_title(TitleKey.CONTEXT),
                value=display_model,
            )
        except Exception as e:
            from backend.exceptions import AppException
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


