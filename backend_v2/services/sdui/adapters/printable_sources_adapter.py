"""Printable Sources SDUI Adapter.

Transforms cited sources and MCP source verification traces into polymorphic
AnySduiBlock components for Server-Driven UI rendering. Visual rules and MCP gateway
mappings are co-located in SECTION 1 PRINTABLE_SOURCES_RULES to enforce Dumb Painter
separation of presentation from logic.
"""

from __future__ import annotations

import logging
import re

from backend_v2.models.core_base import I18nText
from backend_v2.models.dtos.sdui_rules import (
    PrintableSourcesRulesDTO,
    SourceDisplayNameDTO,
    TheoryEvidenceItemDTO,
)
from backend_v2.models.enums import EntityPrefix, SourcesDisplayMode
from backend_v2.models.view.sdui import (
    AnySduiBlock,
    MarkdownBlock,
    ParagraphBlock,
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

PRINTABLE_SOURCES_RULES: PrintableSourcesRulesDTO = PrintableSourcesRulesDTO(
    literature_source=SourceDisplayNameDTO(
        display_name_fi="Vertaisarvioitu tieteellinen julkaisu ja arviointimalli",
        display_name_en="Peer-reviewed scientific literature & framework",
    ),
    theory_evidence_map={
        "popper": TheoryEvidenceItemDTO(
            fi=(
                "Tieteellinen arviointikehys: Hypoteesien ja toimenpiteiden falsifioitavuus, "
                "epäonnistumiskriteerit ja kriittinen rationalismi."
            ),
            en=(
                "Scientific evaluation framework: Empirical falsifiability of hypotheses, "
                "failure criteria, and critical rationalism."
            ),
        ),
        "toulmin": TheoryEvidenceItemDTO(
            fi="Argumentaatiomalli: Väitteiden oikeutus, taustatuki (backing) ja perusteluketjujen looginen eheys.",
            en="Argumentation model: Claim justification, empirical backing, and logical structure integrity.",
        ),
        "kahneman": TheoryEvidenceItemDTO(
            fi=(
                "Kognitiivinen päätöksenteko: Heuristiikat, kognitiiviset vinoumat ja "
                "itsenäisen laadunvalvonnan arviointi."
            ),
            en=(
                "Cognitive decision-making: Heuristics, cognitive biases, and independent quality assurance evaluation."
            ),
        ),
        "tversky": TheoryEvidenceItemDTO(
            fi=(
                "Kognitiivinen päätöksenteko: Heuristiikat, kognitiiviset vinoumat ja "
                "itsenäisen laadunvalvonnan arviointi."
            ),
            en=(
                "Cognitive decision-making: Heuristics, cognitive biases, and independent quality assurance evaluation."
            ),
        ),
        "default": TheoryEvidenceItemDTO(
            fi="Tieteellinen taustakirjallisuus ja arviointiviitekehys.",
            en="Scientific reference literature and evaluation framework.",
        ),
    },
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
            tool = context.mcp_tools_map[tool_id]
            if isinstance(tool.name, str):
                return tool.name
            if isinstance(tool.name, I18nText):
                return tool.name.resolve(locale)
            return tool_id

        if tool_id:
            clean_name = tool_id.removeprefix("mcp_").replace("_", " ").title()
            return f"{clean_name} Gateway"

        return PRINTABLE_SOURCES_RULES.default_tool.get_display_name(locale)

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

        locale = context.locale
        display_mode = context.profile.sources_display_mode
        show_summary_box = context.profile.show_sources_summary_box

        # 1. READ & SANITIZE: Extract and clean cited sources (filter internal DAG step IDs)
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

        # 2. READ: Extract MCP audit traces
        mcp_traces = []
        if context.mcp_audit_map:
            mcp_traces = list(context.mcp_audit_map.values())

        if not clean_cited_sources and not mcp_traces and not show_summary_box:
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
                tool_badges: list[str] = [
                    PrintableSourcesAdapter._resolve_tool_badge(t_id, context, locale) for t_id in unique_tool_ids
                ]

                summary_lines.append(f"> - **{used_gateways_label}** {', '.join(tool_badges)}")
            else:
                direct_citations_label = LocalizationService.translate("sources_direct_citations_count", locale)
                summary_lines.append(f"> - **{direct_citations_label}** {len(clean_cited_sources)}")

            section_parts.append("\n".join(summary_lines))

        # 5. ASSEMBLE: Content Body based on sources_display_mode
        if not clean_cited_sources and not mcp_traces:
            no_citations_msg = LocalizationService.translate("sources_no_direct_citations", locale)
            section_parts.append(f"- {no_citations_msg}")
        elif display_mode == SourcesDisplayMode.SIMPLE_BIBLIOGRAPHY:
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
            verified_status_text = LocalizationService.translate("sources_status_verified", locale)
            unverified_status_text = LocalizationService.translate("sources_status_unverified", locale)
            method_label = LocalizationService.translate("sources_verification_method", locale)
            synthesis_label = LocalizationService.translate("sources_synthesis_finding", locale)
            observation_label = LocalizationService.translate("sources_input_observation", locale)
            mcp_result_label = LocalizationService.translate("sources_mcp_result", locale)
            theory_label = LocalizationService.translate("sources_theoretical_grounding", locale)
            no_obs_text = LocalizationService.translate("sources_no_observation_in_input", locale)

            # Collect narrative sentences from synthesized blocks for in-text citation matching
            all_narrative_sentences: list[str] = []
            if context.profile_cache and context.profile_cache.section_syntheses:
                for sec_blocks in context.profile_cache.section_syntheses.values():
                    for b in sec_blocks:
                        b_text = ""
                        if isinstance(b, MarkdownBlock | ParagraphBlock):
                            b_text = b.text
                        if b_text:
                            for s in re.split(r"(?<=[.!?])\s+", b_text):
                                clean_s = s.strip()
                                if clean_s:
                                    all_narrative_sentences.append(clean_s)

            for trace in mcp_traces:
                t_name = PrintableSourcesAdapter._resolve_tool_badge(trace.tool_id, context, locale)

                clean_urls = [u.strip() for u in trace.source_urls if u.strip()]
                is_verified = len(clean_urls) > 0
                if is_verified:
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
                    rendered_urls.add(url)
                    if url.startswith("http://") or url.startswith("https://"):
                        evidence_lines.append(f"- **[{url}]({url})**")
                    else:
                        evidence_lines.append(f"- **{url}**")

                    evidence_lines.append(f"  - **{status_label}** {item_status_text}")
                    evidence_lines.append(f"  - **{method_label}** {t_name}")

                    if trace.claim_text and trace.claim_text.strip():
                        evidence_lines.append(f'  - **{synthesis_label}** "{trace.claim_text.strip()}"')
                    if trace.response_summary and trace.response_summary.strip():
                        evidence_lines.append(f"  - **{mcp_result_label}** {trace.response_summary.strip()}")

            # Render remaining standalone cited sources with full evidence details in VERIFIED_EVIDENCE mode
            lit_rule = PRINTABLE_SOURCES_RULES.literature_source
            lit_name = lit_rule.get_display_name(locale)
            theory_map = PRINTABLE_SOURCES_RULES.theory_evidence_map

            for src in clean_cited_sources:
                if src not in rendered_urls:
                    if src.startswith("http://") or src.startswith("https://"):
                        evidence_lines.append(f"- **[{src}]({src})**")
                    else:
                        evidence_lines.append(f"- **{src}**")

                    evidence_lines.append(f"  - **{status_label}** {verified_status_text}")
                    evidence_lines.append(f"  - **{method_label}** {lit_name}")

                    # Author token extraction (e.g. "Popper, K. (1959)..." -> "popper")
                    raw_author = src.split("(")[0].split(",")[0].split("&")[0].strip().lower()

                    # Find matching sentence from narrative
                    matched_sentence = None
                    for sent in all_narrative_sentences:
                        if raw_author and raw_author in sent.lower():
                            matched_sentence = sent
                            break

                    if matched_sentence:
                        evidence_lines.append(f'  - **{synthesis_label}** "{matched_sentence}"')

                    # Collect empirical quotes from evaluated matrix atoms
                    matched_quotes: list[str] = []
                    if context.parsed_matrices:
                        for mat in context.parsed_matrices.values():
                            for atom in mat.evaluated_atoms:
                                for eq in atom.exact_quotes:
                                    if eq.source_quotes:
                                        joined_quote = " [...] ".join(
                                            q.strip() for q in eq.source_quotes if q and q.strip()
                                        )
                                        if joined_quote:
                                            matched_quotes.append(joined_quote)
                                    else:
                                        for quote_str in eq.get_quotes():
                                            if quote_str and quote_str.strip():
                                                matched_quotes.append(quote_str.strip())

                    if matched_quotes:
                        evidence_lines.append(f'  - **{observation_label}** "{matched_quotes[0]}"')
                    else:
                        evidence_lines.append(f"  - **{observation_label}** {no_obs_text}")

                    # Resolve theoretical grounding description
                    if raw_author in theory_map:
                        theory_desc = theory_map[raw_author].get_text(locale)
                    elif "default" in theory_map:
                        theory_desc = theory_map["default"].get_text(locale)
                    else:
                        theory_desc = None

                    if theory_desc:
                        evidence_lines.append(f"  - **{theory_label}** {theory_desc}")

            section_parts.append("\n".join(evidence_lines))

        md_content = "\n\n".join(section_parts)
        blocks.append(MarkdownBlock(text=md_content))
        return blocks
