"""Printable Sources SDUI Adapter.

Transforms cited sources, evaluation framework theory provenance, and MCP source
verification traces into polymorphic AnySduiBlock components for Server-Driven UI
rendering. Visual rules and MCP gateway mappings are co-located in SECTION 1
PRINTABLE_SOURCES_RULES to enforce Dumb Painter separation of presentation from logic.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from backend_v2.models.dtos.sdui_rules import (
    EvaluationFrameworkItemDTO,
    PrintableSourcesRulesDTO,
    SourceDisplayNameDTO,
)
from backend_v2.models.enums import EntityPrefix, SourcesDisplayMode
from backend_v2.models.view.sdui import (
    AnySduiBlock,
    MarkdownBlock,
)
from backend_v2.services.localization import LocalizationService
from backend_v2.services.sdui.sanitizers import McpPresentationSanitizer

if TYPE_CHECKING:
    from backend_v2.models.domain.system_config import MCPAuditTrace
    from backend_v2.services.sdui.adapters.base_adapter import AdapterContext

logger = logging.getLogger(__name__)

__all__ = ["PRINTABLE_SOURCES_RULES", "PrintableSourcesAdapter"]


# ============================================================================
# SECTION 1: AESTHETICS RULES
# ============================================================================
# All visual decisions, icon selections, and MCP tool badge mappings are defined
# here as a flat configuration. The adapter class below MUST NOT contain arbitrary
# if/elif/else chains for tool name resolution.
# ============================================================================

PRINTABLE_SOURCES_RULES: PrintableSourcesRulesDTO = PrintableSourcesRulesDTO(
    literature_source=SourceDisplayNameDTO(
        display_name_fi="Vertaisarvioitu tieteellinen julkaisu ja arviointimalli",
        display_name_en="Peer-reviewed scientific literature & framework",
    ),
    default_tool=SourceDisplayNameDTO(
        display_name_fi="Ulkoisen tiedonhaun yhdyskäytävä",
        display_name_en="External Information Retrieval Gateway",
    ),
)


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
    def _resolve_tool_badge(tool_id: str | None, context: AdapterContext, locale: str) -> str:
        """Resolve localized tool display name badge from context or tool ID.

        Args:
            tool_id: Unique tool identifier or slug.
            context: Adapter context containing configured tools.
            locale: User target language locale.

        Returns:
            Human-readable formatted tool badge string.
        """
        if tool_id and tool_id in context.mcp_tools_map:
            return context.mcp_tools_map[tool_id].name.resolve(locale)

        if tool_id and "__" in tool_id:
            short_tool_id = tool_id.split("__", 1)[1]
            if short_tool_id in context.mcp_tools_map:
                return context.mcp_tools_map[short_tool_id].name.resolve(locale)
            clean_name = short_tool_id.removeprefix("mcp_").replace("_", " ").title()
            return f"{clean_name} Gateway"

        if tool_id:
            clean_name = tool_id.removeprefix("mcp_").replace("_", " ").title()
            return f"{clean_name} Gateway"

        return PRINTABLE_SOURCES_RULES.default_tool.get_display_name(locale)

    @staticmethod
    def _extract_cited_sources(context: AdapterContext) -> list[str]:
        """Extract and sanitize cited sources while filtering internal DAG step keys.

        Args:
            context: Frozen, immutable adapter context.

        Returns:
            Deduplicated list of sanitized external citation strings.
        """
        clean_cited_sources: list[str] = []
        if context.profile_cache and context.profile_cache.cited_sources:
            for src in context.profile_cache.cited_sources:
                item = src.strip()
                if not item:
                    continue
                clean_item = item.removeprefix("- ").strip()
                if not clean_item:
                    continue
                # Scope isolation: filter internal execution step IDs like sr_... and stp_...
                if (
                    clean_item.startswith(f"{EntityPrefix.STEP_REFERENCE}_")
                    or clean_item.startswith(f"{EntityPrefix.STEP}_")
                    or "_results" in clean_item
                ):
                    continue
                if clean_item not in clean_cited_sources:
                    clean_cited_sources.append(clean_item)
        return clean_cited_sources

    @staticmethod
    def _extract_framework_items(context: AdapterContext, locale: str) -> list[EvaluationFrameworkItemDTO]:
        """Extract deterministic evaluation framework provenance from parsed matrices.

        Args:
            context: Frozen, immutable adapter context.
            locale: Target localization language code.

        Returns:
            Deduplicated list of EvaluationFrameworkItemDTO entries.
        """
        framework_items: list[EvaluationFrameworkItemDTO] = []
        if context.parsed_matrices:
            for mat in context.parsed_matrices.values():
                title = mat.cited_source_title
                if title and title.strip():
                    url: str | None = None
                    if mat.cited_source_url is not None and mat.cited_source_url.strip():
                        url = mat.cited_source_url.strip()
                    mat_name: str = mat.block_id
                    if mat.label_i18n is not None:
                        mat_name = mat.label_i18n.resolve(locale)
                    if mat.name and mat.name.strip():
                        mat_name = mat.name.strip()
                    framework_entry = EvaluationFrameworkItemDTO(
                        matrix_name=mat_name,
                        cited_source_title=title.strip(),
                        cited_source_url=url,
                    )
                    if framework_entry not in framework_items:
                        framework_items.append(framework_entry)
        return framework_items

    @staticmethod
    def _build_summary_box(
        mcp_traces: list[MCPAuditTrace],
        clean_cited_sources: list[str],
        context: AdapterContext,
        locale: str,
    ) -> str:
        """Assemble the Markdown NOTE summary box for sources and fact-checking audit.

        Args:
            mcp_traces: Extracted MCP audit trace items.
            clean_cited_sources: Sanitized external citation strings.
            context: Frozen, immutable adapter context.
            locale: Target localization language code.

        Returns:
            Formatted Markdown blockquote summary string.

        Raises:
            AppException: If a required localization key or directory is missing
                (ErrorCodes.CONFIGURATION_ERROR).
        """
        summary_box_title = LocalizationService.translate("sources_summary_box_title", locale)
        summary_lines: list[str] = [
            "> [!NOTE]",
            f"> **{summary_box_title}**",
        ]

        if mcp_traces:
            verified_claims_label = LocalizationService.translate("sources_verified_claims_count", locale)
            used_gateways_label = LocalizationService.translate("sources_used_gateways", locale)

            summary_lines.append(f"> - **{verified_claims_label}** {len(mcp_traces)}")

            unique_tool_ids = sorted({t.tool_id for t in mcp_traces})
            tool_badges: list[str] = [
                PrintableSourcesAdapter._resolve_tool_badge(t_id, context, locale) for t_id in unique_tool_ids
            ]

            summary_lines.append(f"> - **{used_gateways_label}** {', '.join(tool_badges)}")
        else:
            direct_citations_label = LocalizationService.translate("sources_direct_citations_count", locale)
            summary_lines.append(f"> - **{direct_citations_label}** {len(clean_cited_sources)}")

        return "\n".join(summary_lines)

    @staticmethod
    def _build_simple_bibliography(
        clean_cited_sources: list[str],
        framework_items: list[EvaluationFrameworkItemDTO],
        mcp_traces: list[MCPAuditTrace],
    ) -> str:
        """Assemble flat alphabetical Markdown list for SIMPLE_BIBLIOGRAPHY mode.

        Args:
            clean_cited_sources: Sanitized external citation strings.
            framework_items: Extracted evaluation framework provenance items.
            mcp_traces: Extracted MCP audit trace items.

        Returns:
            Alphabetically sorted Markdown bullet list string.
        """
        all_entries: list[str] = list(clean_cited_sources)
        for f_item in framework_items:
            if f_item.cited_source_url:
                f_entry = f"{f_item.matrix_name}: {f_item.cited_source_title} - {f_item.cited_source_url}"
            else:
                f_entry = f"{f_item.matrix_name}: {f_item.cited_source_title}"
            if f_entry not in all_entries:
                all_entries.append(f_entry)
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

        return "\n".join(formatted_entries)

    @staticmethod
    def _build_frameworks_subsection(
        framework_items: list[EvaluationFrameworkItemDTO],
        locale: str,
    ) -> str:
        """Format Subsection A (Scientific Evaluation Frameworks) in VERIFIED_EVIDENCE mode.

        Args:
            framework_items: Non-empty list of evaluation framework provenance items.
            locale: Target localization language code.

        Returns:
            Formatted Markdown subsection string.

        Raises:
            AppException: If a required localization key or directory is missing
                (ErrorCodes.CONFIGURATION_ERROR).
        """
        frameworks_title = LocalizationService.translate("sources_evaluation_frameworks_title", locale)
        framework_lines: list[str] = [f"#### {frameworks_title}"]
        for f_item in framework_items:
            if f_item.cited_source_url:
                framework_lines.append(
                    f"- **{f_item.matrix_name}**: {f_item.cited_source_title} - [{f_item.cited_source_url}]({f_item.cited_source_url})"
                )
            else:
                framework_lines.append(f"- **{f_item.matrix_name}**: {f_item.cited_source_title}")
        return "\n".join(framework_lines)

    @staticmethod
    def _build_mcp_subsection(
        mcp_traces: list[MCPAuditTrace],
        context: AdapterContext,
        locale: str,
    ) -> str:
        """Format Subsection B (External Fact-Checking Gateways) in VERIFIED_EVIDENCE mode.

        Args:
            mcp_traces: Non-empty list of MCP audit trace items.
            context: Frozen, immutable adapter context.
            locale: Target localization language code.

        Returns:
            Formatted Markdown subsection string.

        Raises:
            AppException: If a required localization key or directory is missing
                (ErrorCodes.CONFIGURATION_ERROR).
        """
        mcp_title = LocalizationService.translate("sources_mcp_title", locale)
        mcp_lines: list[str] = [f"#### {mcp_title}"]
        status_label = LocalizationService.translate("sources_status_label", locale)
        verified_status_text = LocalizationService.translate("sources_status_verified", locale)
        unverified_status_text = LocalizationService.translate("sources_status_unverified", locale)
        method_label = LocalizationService.translate("sources_verification_method", locale)
        synthesis_label = LocalizationService.translate("sources_synthesis_finding", locale)
        mcp_result_label = LocalizationService.translate("sources_mcp_result", locale)

        for trace in mcp_traces:
            t_name = PrintableSourcesAdapter._resolve_tool_badge(trace.tool_id, context, locale)
            clean_urls = [u.strip() for u in trace.source_urls if u.strip()]
            if clean_urls:
                item_status_text = verified_status_text
                urls_to_render = clean_urls
            else:
                item_status_text = unverified_status_text
                query_text = trace.query.strip()
                if query_text:
                    urls_to_render = [query_text]
                else:
                    urls_to_render = [trace.tool_id]

            for url in urls_to_render:
                if url.startswith("http://") or url.startswith("https://"):
                    mcp_lines.append(f"- **[{url}]({url})**")
                else:
                    mcp_lines.append(f"- **{url}**")

                mcp_lines.append(f"  - **{status_label}** {item_status_text}")
                mcp_lines.append(f"  - **{method_label}** {t_name}")

                if trace.claim_text and trace.claim_text.strip():
                    mcp_lines.append(f'  - **{synthesis_label}** "{trace.claim_text.strip()}"')
                if trace.response_summary and trace.response_summary.strip():
                    clean_finding = McpPresentationSanitizer.sanitize_finding(trace.response_summary)
                    if clean_finding:
                        mcp_lines.append(f"  - **{mcp_result_label}** {clean_finding}")

        return "\n".join(mcp_lines)

    @staticmethod
    def _build_citations_subsection(
        clean_cited_sources: list[str],
        locale: str,
    ) -> str:
        """Format Subsection C (Citations in Evaluated Material) in VERIFIED_EVIDENCE mode.

        Args:
            clean_cited_sources: Non-empty list of sanitized external citation strings.
            locale: Target localization language code.

        Returns:
            Formatted Markdown subsection string.

        Raises:
            AppException: If a required localization key or directory is missing
                (ErrorCodes.CONFIGURATION_ERROR).
        """
        citations_title = LocalizationService.translate("sources_input_citations_title", locale)
        citation_lines: list[str] = [f"#### {citations_title}"]
        status_label = LocalizationService.translate("sources_status_label", locale)
        verified_status_text = LocalizationService.translate("sources_status_verified", locale)
        method_label = LocalizationService.translate("sources_verification_method", locale)
        lit_name = PRINTABLE_SOURCES_RULES.literature_source.get_display_name(locale)

        for src in clean_cited_sources:
            if src.startswith("http://") or src.startswith("https://"):
                citation_lines.append(f"- **[{src}]({src})**")
            else:
                citation_lines.append(f"- **{src}**")
            citation_lines.append(f"  - **{status_label}** {verified_status_text}")
            citation_lines.append(f"  - **{method_label}** {lit_name}")

        return "\n".join(citation_lines)

    @staticmethod
    def _build_verified_evidence(
        framework_items: list[EvaluationFrameworkItemDTO],
        mcp_traces: list[MCPAuditTrace],
        clean_cited_sources: list[str],
        context: AdapterContext,
        locale: str,
    ) -> list[str]:
        """Assemble Three-Way Ontological Segregation sections for VERIFIED_EVIDENCE mode.

        Args:
            framework_items: Extracted evaluation framework provenance items.
            mcp_traces: Extracted MCP audit trace items.
            clean_cited_sources: Sanitized external citation strings.
            context: Frozen, immutable adapter context.
            locale: Target localization language code.

        Returns:
            Ordered list of formatted Markdown subsection strings.

        Raises:
            AppException: If a required localization key or directory is missing
                (ErrorCodes.CONFIGURATION_ERROR).
        """
        evidence_sections: list[str] = []
        if framework_items:
            evidence_sections.append(PrintableSourcesAdapter._build_frameworks_subsection(framework_items, locale))
        if mcp_traces:
            evidence_sections.append(PrintableSourcesAdapter._build_mcp_subsection(mcp_traces, context, locale))
        if clean_cited_sources:
            evidence_sections.append(PrintableSourcesAdapter._build_citations_subsection(clean_cited_sources, locale))
        return evidence_sections

    @staticmethod
    def build(context: AdapterContext) -> list[AnySduiBlock]:
        """Build SDUI blocks from the adapter context.

        Args:
            context: Frozen, immutable adapter context containing all
                required data for block construction.

        Returns:
            Ordered list of polymorphic SDUI blocks ready for rendering.

        Raises:
            AppException: If a required localization key or directory is missing
                (ErrorCodes.CONFIGURATION_ERROR).
        """
        blocks: list[AnySduiBlock] = []

        if context.is_data_starved:
            return blocks

        locale = context.locale
        display_mode = context.profile.sources_display_mode
        show_summary_box = context.profile.show_sources_summary_box

        clean_cited_sources = PrintableSourcesAdapter._extract_cited_sources(context)
        framework_items = PrintableSourcesAdapter._extract_framework_items(context, locale)
        mcp_traces: list[MCPAuditTrace] = []
        if context.mcp_audit_map:
            mcp_traces = list(context.mcp_audit_map.values())

        if not clean_cited_sources and not mcp_traces and not framework_items and not show_summary_box:
            return blocks

        title_str = LocalizationService.translate("sources_and_bibliography_title", locale)
        section_parts: list[str] = [f"### {title_str}"]

        if show_summary_box:
            section_parts.append(
                PrintableSourcesAdapter._build_summary_box(mcp_traces, clean_cited_sources, context, locale)
            )

        if not clean_cited_sources and not mcp_traces and not framework_items:
            no_citations_msg = LocalizationService.translate("sources_no_direct_citations", locale)
            section_parts.append(f"- {no_citations_msg}")
        elif display_mode == SourcesDisplayMode.SIMPLE_BIBLIOGRAPHY:
            section_parts.append(
                PrintableSourcesAdapter._build_simple_bibliography(clean_cited_sources, framework_items, mcp_traces)
            )
        else:
            section_parts.extend(
                PrintableSourcesAdapter._build_verified_evidence(
                    framework_items, mcp_traces, clean_cited_sources, context, locale
                )
            )

        md_content = "\n\n".join(section_parts)
        blocks.append(MarkdownBlock(text=md_content))
        return blocks
