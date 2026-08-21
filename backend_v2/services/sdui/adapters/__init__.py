"""SDUI adapters package."""

from backend_v2.services.sdui.adapters.base_adapter import AdapterContext, SduiAdapterProtocol
from backend_v2.services.sdui.adapters.executive_summary_adapter import ExecutiveSummaryAdapter
from backend_v2.services.sdui.adapters.global_score_adapter import GlobalScoreAdapter
from backend_v2.services.sdui.adapters.matrix_graphs_adapter import MatrixGraphsAdapter
from backend_v2.services.sdui.adapters.matrix_summary_table_adapter import MatrixSummaryTableAdapter
from backend_v2.services.sdui.adapters.mcp_audit_adapter import McpAuditAdapter
from backend_v2.services.sdui.adapters.metadata_adapter import MetadataAdapter
from backend_v2.services.sdui.adapters.penalties_adapter import PenaltiesAdapter
from backend_v2.services.sdui.adapters.printable_sources_adapter import PrintableSourcesAdapter
from backend_v2.services.sdui.adapters.synthesis_text_adapter import SynthesisTextAdapter
from backend_v2.services.sdui.adapters.warning_card_adapter import WarningCardAdapter
from backend_v2.services.sdui.adapters.xai_highlights_adapter import XaiHighlightsAdapter

__all__ = [
    "AdapterContext",
    "SduiAdapterProtocol",
    "ExecutiveSummaryAdapter",
    "GlobalScoreAdapter",
    "MatrixGraphsAdapter",
    "MatrixSummaryTableAdapter",
    "McpAuditAdapter",
    "MetadataAdapter",
    "PenaltiesAdapter",
    "PrintableSourcesAdapter",
    "SynthesisTextAdapter",
    "WarningCardAdapter",
    "XaiHighlightsAdapter",
]
