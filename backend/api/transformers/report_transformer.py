from backend.api.transformers.report_core import ReportTransformer as ReportCoreTransformer
from backend.models.domain.execution import ExecutionRecord
from backend.models.view.semantic_models import SemanticReport as ExecutionReportView

# Profiler/Archivist/Interaction might be loosely typed or strict, we check inflating.


class ReportTransformer:
    """Transforms internal Domain/State models into agnostic SemanticBlocks (SDUI).
    Follows the BFF (Backend-for-Frontend) pattern.

    DUAL MODE:
    1. Produces strict BFF fields (summary_section, score_section...) for any generic UI client.
    2. Produces generic 'sections' list for PDF Generation.
    """

    def __init__(self, language: str = "en"):
        self.language = language

    def transform(self, execution: ExecutionRecord, workflow_name: str | None = None) -> ExecutionReportView:
        """Transforms a raw ExecutionRecord into a fully populated Server-Driven UI
        ReportView by delegating entirely to the ReportCoreTransformer.
        """
        core_transformer = ReportCoreTransformer(language=self.language)
        return core_transformer.transform(execution, workflow_name=workflow_name)
