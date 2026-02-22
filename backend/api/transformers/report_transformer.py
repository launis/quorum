from backend.api.transformers.report_core import ReportTransformer as ReportCoreTransformer
from backend.models.domain.execution import ExecutionRecord
from backend.models.view.sdui import ReportView as ExecutionReportView

# Profiler/Archivist/Interaction might be loosely typed or strict, we check inflating.


class ReportTransformer:
    """Transforms internal Domain/State models into Flutter-ready ViewModels.
    Follows the BFF (Backend-for-Frontend) pattern.

    DUAL MODE:
    1. Produces strict BFF fields (summary_section, score_section...) for new Flutter UI.
    2. Produces generic 'sections' list for Legacy PDF Generation / SDUI.
    """

    def __init__(self, language: str = "en"):
        self.language = language

    def transform(self, execution: ExecutionRecord) -> ExecutionReportView:
        """Transforms a raw ExecutionRecord into a fully populated Server-Driven UI
        ReportView by delegating entirely to the ReportCoreTransformer.
        """
        core_transformer = ReportCoreTransformer(language=self.language)
        return core_transformer.transform(execution)
