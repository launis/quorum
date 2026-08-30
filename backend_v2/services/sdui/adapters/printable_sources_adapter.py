"""Printable Sources SDUI Adapter.

Transforms cited sources and MCP source verification traces into polymorphic
AnySduiBlock components for Server-Driven UI rendering. Visual rules and MCP gateway
mappings are co-located in SECTION 1 PRINTABLE_SOURCES_RULES to enforce Dumb Painter
separation of presentation from logic.
"""

import logging
import re
from typing import Any

from backend_v2.models.enums import SourcesDisplayMode
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

PRINTABLE_SOURCES_RULES: dict[str, Any] = {
    "literature_source": {
        "display_name_fi": "Vertaisarvioitu tieteellinen julkaisu ja arviointimalli",
        "display_name_en": "Peer-reviewed scientific literature & framework",
    },
    "theory_evidence_map": {
        "popper": {
            "fi": "Tieteellinen arviointikehys: Hypoteesien ja toimenpiteiden falsifioitavuus, epäonnistumiskriteerit ja kriittinen rationalismi.",
            "en": "Scientific evaluation framework: Empirical falsifiability of hypotheses, failure criteria, and critical rationalism.",
        },
        "toulmin": {
            "fi": "Argumentaatiomalli: Väitteiden oikeutus, taustatuki (backing) ja perusteluketjujen looginen eheys.",
            "en": "Argumentation model: Claim justification, empirical backing, and logical structure integrity.",
        },
        "kahneman": {
            "fi": "Kognitiivinen päätöksenteko: Heuristiikat, kognitiiviset vinoumat ja itsenäisen laadunvalvonnan arviointi.",
            "en": "Cognitive decision-making: Heuristics, cognitive biases, and independent quality assurance evaluation.",
        },
        "tversky": {
            "fi": "Kognitiivinen päätöksenteko: Heuristiikat, kognitiiviset vinoumat ja itsenäisen laadunvalvonnan arviointi.",
            "en": "Cognitive decision-making: Heuristics, cognitive biases, and independent quality assurance evaluation.",
        },
        "default": {
            "fi": "Tieteellinen taustakirjallisuus ja arviointiviitekehys.",
            "en": "Scientific reference literature and evaluation framework.",
        },
    },
    "default_tool": {
        "display_name_fi": "Ulkoisen tiedonhaun yhdyskäytävä",
        "display_name_en": "External Information Retrieval Gateway",
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
                tool_badges: list[str] = []
                for t_id in unique_tool_ids:
                    if t_id and t_id in context.mcp_tools_map:
                        tool = context.mcp_tools_map[t_id]
                        if isinstance(tool.name, str):
                            t_name = tool.name
                        elif locale in tool.name.translations:
                            t_name = tool.name.translations[locale]
                        elif "en" in tool.name.translations:
                            t_name = tool.name.translations["en"]
                        else:
                            t_name = t_id
                    elif t_id:
                        clean_name = t_id.removeprefix("mcp_").replace("_", " ").title()
                        t_name = f"{clean_name} Gateway"
                    else:
                        t_name = str(PRINTABLE_SOURCES_RULES["default_tool"][f"display_name_{locale}"])
                    tool_badges.append(t_name)

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
            status_text = LocalizationService.translate("sources_status_verified", locale)
            method_label = LocalizationService.translate("sources_verification_method", locale)
            synthesis_label = LocalizationService.translate("sources_synthesis_finding", locale)
            observation_label = LocalizationService.translate("sources_input_observation", locale)
            theory_label = LocalizationService.translate("sources_theoretical_grounding", locale)
            no_obs_text = LocalizationService.translate("sources_no_observation_in_input", locale)

            # Collect narrative sentences from synthesized blocks for in-text citation matching
            all_narrative_sentences: list[str] = []
            if context.profile_cache and context.profile_cache.section_syntheses:
                for sec_blocks in context.profile_cache.section_syntheses.values():
                    for b in sec_blocks:
                        b_text = b.text if isinstance(b, MarkdownBlock | ParagraphBlock) else ""
                        if b_text:
                            for s in re.split(r"(?<=[.!?])\s+", b_text):
                                clean_s = s.strip()
                                if clean_s:
                                    all_narrative_sentences.append(clean_s)

            for trace in mcp_traces:
                if trace.tool_id and trace.tool_id in context.mcp_tools_map:
                    tool = context.mcp_tools_map[trace.tool_id]
                    if isinstance(tool.name, str):
                        t_name = tool.name
                    elif locale in tool.name.translations:
                        t_name = tool.name.translations[locale]
                    elif "en" in tool.name.translations:
                        t_name = tool.name.translations["en"]
                    else:
                        t_name = trace.tool_id
                elif trace.tool_id:
                    clean_name = trace.tool_id.removeprefix("mcp_").replace("_", " ").title()
                    t_name = f"{clean_name} Gateway"
                else:
                    t_name = str(PRINTABLE_SOURCES_RULES["default_tool"][f"display_name_{locale}"])

                urls_to_render = [u.strip() for u in trace.source_urls if u.strip()]
                if not urls_to_render:
                    urls_to_render = [trace.query]

                for url in urls_to_render:
                    rendered_urls.add(url)
                    if url.startswith("http://") or url.startswith("https://"):
                        evidence_lines.append(f"- **[{url}]({url})**")
                    else:
                        evidence_lines.append(f"- **{url}**")

                    evidence_lines.append(f"  - **{status_label}** {status_text}")
                    evidence_lines.append(f"  - **{method_label}** {t_name}")

                    if trace.claim_text and trace.claim_text.strip():
                        evidence_lines.append(f'  - **{synthesis_label}** "{trace.claim_text.strip()}"')
                    if trace.response_summary and trace.response_summary.strip():
                        evidence_lines.append(f"  - **{theory_label}** {trace.response_summary.strip()}")

            # Render remaining standalone cited sources with full evidence details in VERIFIED_EVIDENCE mode
            if "literature_source" in PRINTABLE_SOURCES_RULES:
                lit_rule = PRINTABLE_SOURCES_RULES["literature_source"]
            else:
                lit_rule = PRINTABLE_SOURCES_RULES["default_tool"]
            lit_name = str(lit_rule[f"display_name_{locale}"])
            theory_map = (
                PRINTABLE_SOURCES_RULES["theory_evidence_map"]
                if "theory_evidence_map" in PRINTABLE_SOURCES_RULES
                else {}
            )

            for src in clean_cited_sources:
                if src not in rendered_urls:
                    if src.startswith("http://") or src.startswith("https://"):
                        evidence_lines.append(f"- **[{src}]({src})**")
                    else:
                        evidence_lines.append(f"- **{src}**")

                    evidence_lines.append(f"  - **{status_label}** {status_text}")
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
                                    if eq.quote and eq.quote.strip():
                                        matched_quotes.append(eq.quote.strip())

                    if matched_quotes:
                        evidence_lines.append(f'  - **{observation_label}** "{matched_quotes[0]}"')
                    else:
                        evidence_lines.append(f"  - **{observation_label}** {no_obs_text}")

                    # Resolve theoretical grounding description
                    if raw_author in theory_map and locale in theory_map[raw_author]:
                        theory_desc = str(theory_map[raw_author][locale])
                    elif "default" in theory_map and locale in theory_map["default"]:
                        theory_desc = str(theory_map["default"][locale])
                    else:
                        theory_desc = None

                    if theory_desc:
                        evidence_lines.append(f"  - **{theory_label}** {theory_desc}")

            section_parts.append("\n".join(evidence_lines))

        md_content = "\n\n".join(section_parts)
        blocks.append(MarkdownBlock(text=md_content))
        return blocks
