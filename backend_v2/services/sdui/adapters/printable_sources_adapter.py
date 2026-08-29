"""Printable Sources SDUI Adapter.

Transforms cited sources and MCP source verification traces into polymorphic
AnySduiBlock components for Server-Driven UI rendering. Visual rules and MCP gateway
mappings are co-located in SECTION 1 PRINTABLE_SOURCES_RULES to enforce Dumb Painter
separation of presentation from logic.
"""

import logging
from typing import Any

from backend_v2.models.enums import SourcesDisplayMode
from backend_v2.models.view.sdui import (
    AnySduiBlock,
    MarkdownBlock,
)
from backend_v2.services.localization import LocalizationService
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext

logger = logging.getLogger(__name__)

__all__ = ["PRINTABLE_SOURCES_RULES", "PrintableSourcesAdapter"]


# ============================================================================
# SECTION 1: AESTHETICS RULES
# ============================================================================
# All visual decisions, icon selections, and MCP tool badge mappings are defined
# here as a flat dictionary. The adapter class below MUST NOT contain arbitrary
# if/elif/else chains for tool name resolution.
# ============================================================================

PRINTABLE_SOURCES_RULES: dict[str, Any] = {
    "mcp_tools": {
        "mcp_tavily_search": {
            "display_name_fi": "Tavily AI Search Gateway",
            "display_name_en": "Tavily AI Search Gateway",
            "icon": "🌐",
        },
        "mcp_wikipedia_search": {
            "display_name_fi": "Wikipedia Search Gateway",
            "display_name_en": "Wikipedia Search Gateway",
            "icon": "📚",
        },
        "mcp_wikipedia_read": {
            "display_name_fi": "Wikipedia Article Gateway",
            "display_name_en": "Wikipedia Article Gateway",
            "icon": "📖",
        },
        "mcp_pubmed_search": {
            "display_name_fi": "PubMed Biomedical Database Gateway",
            "display_name_en": "PubMed Biomedical Database Gateway",
            "icon": "🧬",
        },
    },
    "default_tool": {
        "display_name_fi": "Ulkoisen tiedonhaun yhdyskäytävä",
        "display_name_en": "External Information Retrieval Gateway",
        "icon": "🔍",
    },
}


# ============================================================================
# SECTION 2: ADAPTER CLASS
# ============================================================================
# This class is a stateless transformer. It reads data from AdapterContext,
# looks up visual properties from SECTION 1, and assembles SDUI blocks.
# ============================================================================


class PrintableSourcesAdapter:
    """Transforms printable sources into SDUI visual blocks.

    Uses co-located PRINTABLE_SOURCES_RULES for all aesthetic decisions.
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

        if context.is_data_starved:
            return blocks

        locale = context.locale if context.locale in ("fi", "en") else "en"
        display_mode = context.profile.sources_display_mode
        show_summary_box = context.profile.show_sources_summary_box

        # 1. READ & SANITIZE: Extract and clean cited sources (filter internal DAG step IDs)
        clean_cited_sources: list[str] = []
        if context.profile_cache and context.profile_cache.cited_sources:
            for src in context.profile_cache.cited_sources:
                item = src.strip()
                if not item:
                    continue
                # Scope isolation: filter internal execution keys like sr_... and _results
                if item.startswith("sr_") or "_results" in item:
                    continue
                clean_item = item.removeprefix("- ").strip()
                if clean_item and clean_item not in clean_cited_sources:
                    clean_cited_sources.append(clean_item)

        # 2. READ: Extract MCP audit traces
        mcp_traces = list(context.mcp_audit_map.values()) if context.mcp_audit_map else []

        if not clean_cited_sources and not mcp_traces:
            return blocks

        # 3. ASSEMBLE: Section Title
        title_str = LocalizationService.translate("sources_and_bibliography_title", locale)
        section_parts: list[str] = [f"### {title_str}"]

        # 4. ASSEMBLE: Audit Summary Box
        if show_summary_box:
            summary_box_title = LocalizationService.translate("sources_summary_box_title", locale)
            summary_lines: list[str] = [
                "> [!NOTE]",
                f"> **{summary_box_title}**",
            ]

            if mcp_traces:
                verified_claims_label = LocalizationService.translate("sources_verified_claims_count", locale)
                used_gateways_label = LocalizationService.translate("sources_used_gateways", locale)

                summary_lines.append(f"> - **{verified_claims_label}** {len(mcp_traces)}")

                unique_tool_ids = sorted(list({t.tool_id for t in mcp_traces}))
                tool_badges: list[str] = []
                for t_id in unique_tool_ids:
                    if t_id in PRINTABLE_SOURCES_RULES["mcp_tools"]:
                        t_rule = PRINTABLE_SOURCES_RULES["mcp_tools"][t_id]
                    else:
                        t_rule = PRINTABLE_SOURCES_RULES["default_tool"]
                    t_icon = str(t_rule["icon"])
                    t_name = str(t_rule[f"display_name_{locale}"])
                    tool_badges.append(f"{t_icon} {t_name}")

                summary_lines.append(f"> - **{used_gateways_label}** {', '.join(tool_badges)}")
            elif clean_cited_sources:
                direct_citations_label = LocalizationService.translate("sources_direct_citations_count", locale)
                summary_lines.append(f"> - **{direct_citations_label}** {len(clean_cited_sources)}")

            section_parts.append("\n".join(summary_lines))

        # 5. ASSEMBLE: Content Body based on sources_display_mode
        if display_mode == SourcesDisplayMode.SIMPLE_BIBLIOGRAPHY:
            # Simple Alphabetical Bibliography
            all_entries: list[str] = list(clean_cited_sources)
            for trace in mcp_traces:
                for url in trace.source_urls:
                    clean_u = url.strip()
                    if clean_u and clean_u not in all_entries:
                        all_entries.append(clean_u)

            all_entries.sort()
            formatted_entries: list[str] = []
            for entry in all_entries:
                if entry.startswith("http://") or entry.startswith("https://"):
                    formatted_entries.append(f"- [{entry}]({entry})")
                else:
                    formatted_entries.append(f"- {entry}")

            section_parts.append("\n".join(formatted_entries))
        else:
            # Verified Evidence Mode with Symmetrical MCP Tool badges and nested details
            evidence_lines: list[str] = []
            rendered_urls: set[str] = set()

            status_label = LocalizationService.translate("sources_status_label", locale)
            status_text = LocalizationService.translate("sources_status_verified", locale)
            method_label = LocalizationService.translate("sources_verification_method", locale)
            claim_label = LocalizationService.translate("sources_claim_in_text", locale)
            evidence_label = LocalizationService.translate("sources_verified_evidence", locale)

            for trace in mcp_traces:
                if trace.tool_id in PRINTABLE_SOURCES_RULES["mcp_tools"]:
                    t_rule = PRINTABLE_SOURCES_RULES["mcp_tools"][trace.tool_id]
                else:
                    t_rule = PRINTABLE_SOURCES_RULES["default_tool"]
                t_icon = str(t_rule["icon"])
                t_name = str(t_rule[f"display_name_{locale}"])

                urls_to_render = [u.strip() for u in trace.source_urls if u.strip()]
                if not urls_to_render:
                    urls_to_render = [trace.query]

                for url in urls_to_render:
                    rendered_urls.add(url)
                    if url.startswith("http://") or url.startswith("https://"):
                        evidence_lines.append(f"- **[{url}]({url})**")
                    else:
                        evidence_lines.append(f"- **{url}**")

                    evidence_lines.append(f"  - **{status_label}** ✅ {status_text}")
                    evidence_lines.append(f"  - **{method_label}** {t_icon} {t_name}")

                    if trace.claim_text and trace.claim_text.strip():
                        evidence_lines.append(f'  - **{claim_label}** "{trace.claim_text.strip()}"')
                    if trace.response_summary and trace.response_summary.strip():
                        evidence_lines.append(f"  - **{evidence_label}** {trace.response_summary.strip()}")

            # Render remaining standalone cited sources
            for src in clean_cited_sources:
                if src not in rendered_urls:
                    if src.startswith("http://") or src.startswith("https://"):
                        evidence_lines.append(f"- [{src}]({src})")
                    else:
                        evidence_lines.append(f"- {src}")

            section_parts.append("\n".join(evidence_lines))

        md_content = "\n\n".join(section_parts)
        blocks.append(MarkdownBlock(text=md_content))
        return blocks
