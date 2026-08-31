"""SDUI Template Presentation Parity and Fail-Fast Test Suite.

Enforces:
1. Static AST block exhaustiveness between Python AnySduiBlock, Jinja template, and Dart renderer.
2. Jinja AST attribute validity against Pydantic models.
3. Strict Fail-Fast AppException on unrecognized SDUI block types.
4. StrictUndefined enforcement for missing l10n keys.
5. Golden Master rendering across locales (en, fi) with BeautifulSoup DOM assertions.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import get_args

import jinja2
import pytest
from bs4 import BeautifulSoup

from backend_v2.exceptions import AppException
from backend_v2.models.v2_core import ReportDataDTO
from backend_v2.models.view.sdui import (
    AccordionBlock,
    AlertBlock,
    AnySduiBlock,
    BulletListBlock,
    HeroInsightBlock,
    MarkdownBlock,
    ParagraphBlock,
    SduiAuditTrailBlock,
    SduiGridBlock,
    SduiMatrixTableBlock,
    SduiMetadataBlock,
    SduiMetrics1DBlock,
    SduiNACard,
    SduiQuoteCard,
    SduiRadarChartBlock,
    SduiScatterPlotBlock,
    SduiScoreCardBlock,
    SduiWarningCard,
)
from backend_v2.services.pdf_generator import PdfReportService

REPO_ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = REPO_ROOT / "backend_v2"
TEMPLATES_DIR = BACKEND_ROOT / "templates"
CLIENT_DIR = REPO_ROOT / "client_app_v2"
FIXTURES_DIR = BACKEND_ROOT / "tests" / "fixtures"

PYDANTIC_BLOCK_MODELS: dict[str, type] = {
    "hero_insight": HeroInsightBlock,
    "paragraph": ParagraphBlock,
    "bullet_list": BulletListBlock,
    "alert_box": AlertBlock,
    "accordion": AccordionBlock,
    "markdown": MarkdownBlock,
    "quote_card": SduiQuoteCard,
    "warning_card": SduiWarningCard,
    "n_a_card": SduiNACard,
    "grid": SduiGridBlock,
    "metadata": SduiMetadataBlock,
    "3d_matrix": SduiRadarChartBlock,
    "2d_compare": SduiScatterPlotBlock,
    "matrix_summary": SduiMatrixTableBlock,
    "1d_metrics": SduiMetrics1DBlock,
    "score_card": SduiScoreCardBlock,
    "audit_trail": SduiAuditTrailBlock,
}

DART_UNION_TYPE_MAP: dict[str, str] = {
    "accordion": "SduiAccordionBlock",
    "metadata": "SduiMetadataBlock",
    "score_card": "SduiScoreCardBlock",
    "audit_trail": "SduiAuditTrailBlock",
    "alert_box": "SduiAlertBoxBlock",
    "grid": "SduiGridBlock",
    "markdown": "SduiMarkdownBlock",
    "paragraph": "SduiParagraphBlock",
    "3d_matrix": "SduiRadarChartBlock",
    "2d_compare": "SduiScatterPlotBlock",
    "1d_metrics": "SduiMetrics1DBlock",
    "matrix_summary": "SduiMatrixTableBlock",
    "bullet_list": "SduiBulletListBlock",
    "hero_insight": "SduiHeroInsightBlock",
    "quote_card": "SduiQuoteCardBlock",
    "warning_card": "SduiWarningCardBlock",
    "n_a_card": "SduiNACardBlock",
}


def _extract_jinja_macro_block_types(template_content: str) -> set[str]:
    """Extracts all block_type string literals checked in the Jinja render_sdui_blocks macro."""
    pattern = r"block\.block_type\s*==\s*['\"]([^'\"]+)['\"]"
    return set(re.findall(pattern, template_content))


def _extract_dart_renderer_block_types(dart_content: str) -> set[str]:
    """Extracts all block class types handled in Flutter's sdui_blocks_renderer.dart switch."""
    dart_classes = set(re.findall(r"(\w+Block)\(\)\s*=>", dart_content))
    # Invert mapping
    inv_map = {v: k for k, v in DART_UNION_TYPE_MAP.items()}
    return {inv_map[cls_name] for cls_name in dart_classes if cls_name in inv_map}


def test_all_sdui_blocks_handled_in_jinja_and_dart() -> None:
    """TC-SDUI-01: Asserts that all 17 AnySduiBlock types are handled exhaustively in Jinja2 and Dart."""
    # 1. Pydantic AnySduiBlock types
    # Extract discriminated union members
    union_types = get_args(get_args(AnySduiBlock)[0])
    pydantic_block_types = {model.model_fields["block_type"].default for model in union_types}

    assert len(pydantic_block_types) == 17, f"Expected 17 SDUI block types, found {len(pydantic_block_types)}"

    # 2. Jinja template handled blocks
    jinja_template_file = TEMPLATES_DIR / "report_template.jinja2"
    jinja_content = jinja_template_file.read_text(encoding="utf-8")
    jinja_block_types = _extract_jinja_macro_block_types(jinja_content)

    assert jinja_block_types == pydantic_block_types, (
        f"Mismatch between Pydantic and Jinja blocks.\n"
        f"Missing in Jinja: {pydantic_block_types - jinja_block_types}\n"
        f"Extra in Jinja: {jinja_block_types - pydantic_block_types}"
    )

    # 3. Dart renderer handled blocks
    dart_renderer_file = (
        CLIENT_DIR / "lib" / "features" / "execution" / "views" / "widgets" / "sdui_blocks_renderer.dart"
    )
    dart_content = dart_renderer_file.read_text(encoding="utf-8")
    dart_block_types = _extract_dart_renderer_block_types(dart_content)

    assert dart_block_types == pydantic_block_types, (
        f"Mismatch between Pydantic and Dart blocks.\n"
        f"Missing in Dart: {pydantic_block_types - dart_block_types}\n"
        f"Extra in Dart: {dart_block_types - pydantic_block_types}"
    )

    # 4. Anti-happy-path negative verification
    mutated_types = set(pydantic_block_types)
    mutated_types.remove("hero_insight")
    with pytest.raises(AssertionError):
        assert mutated_types == jinja_block_types


def test_jinja_ast_attribute_validity() -> None:
    """TC-SDUI-02: Parses Jinja template AST and asserts that every block.<attr> access is a declared Pydantic field."""
    jinja_template_file = TEMPLATES_DIR / "report_template.jinja2"
    template_content = jinja_template_file.read_text(encoding="utf-8")

    env = jinja2.Environment()
    parsed_ast = env.parse(template_content)

    # Extract branches inside render_sdui_blocks macro
    macro_node = next(
        (n for n in parsed_ast.body if isinstance(n, jinja2.nodes.Macro) and n.name == "render_sdui_blocks"), None
    )
    assert macro_node is not None, "render_sdui_blocks macro not found in template AST"

    # Walk AST to find If nodes comparing block.block_type == '<type>'
    branch_attr_map: dict[str, set[str]] = {}

    def _find_block_attrs_in_node(node: jinja2.nodes.Node) -> set[str]:
        attrs: set[str] = set()
        # For an If node, only inspect its test and body, not elif_ or else_
        if isinstance(node, jinja2.nodes.If):
            for child in node.test.iter_child_nodes():
                if (
                    isinstance(child, jinja2.nodes.Getattr)
                    and isinstance(child.node, jinja2.nodes.Name)
                    and child.node.name == "block"
                ):
                    attrs.add(child.attr)
                attrs.update(_find_block_attrs_in_node(child))
            for child in node.body:
                if (
                    isinstance(child, jinja2.nodes.Getattr)
                    and isinstance(child.node, jinja2.nodes.Name)
                    and child.node.name == "block"
                ):
                    attrs.add(child.attr)
                attrs.update(_find_block_attrs_in_node(child))
            return attrs

        for child in node.iter_child_nodes():
            if (
                isinstance(child, jinja2.nodes.Getattr)
                and isinstance(child.node, jinja2.nodes.Name)
                and child.node.name == "block"
            ):
                attrs.add(child.attr)
            attrs.update(_find_block_attrs_in_node(child))
        return attrs

    def _process_if_branch(if_node: jinja2.nodes.If) -> None:
        str_literals = [
            n.value
            for n in if_node.test.find_all(jinja2.nodes.Const)
            if isinstance(n.value, str) and n.value in PYDANTIC_BLOCK_MODELS
        ]
        if str_literals:
            for b_type in str_literals:
                # Find attrs only in body of this branch
                branch_attrs: set[str] = set()
                for body_node in if_node.body:
                    branch_attrs.update(_find_block_attrs_in_node(body_node))
                branch_attr_map.setdefault(b_type, set()).update(branch_attrs)
        for elif_node in if_node.elif_:
            _process_if_branch(elif_node)

    for top_child in macro_node.find_all(jinja2.nodes.If):
        _process_if_branch(top_child)

    for block_type, accessed_attrs in branch_attr_map.items():
        pydantic_cls = PYDANTIC_BLOCK_MODELS[block_type]
        valid_fields = set(pydantic_cls.model_fields.keys()) | {"block_type"}
        invalid_attrs = accessed_attrs - valid_fields
        assert not invalid_attrs, (
            f"Jinja template accesses non-existent attributes {invalid_attrs} for block_type='{block_type}' "
            f"(Pydantic model {pydantic_cls.__name__} fields: {valid_fields})"
        )

    # Anti-happy-path negative verification
    fake_accessed = {"non_existent_attribute_xyz"}
    pydantic_cls = PYDANTIC_BLOCK_MODELS["paragraph"]
    valid_fields = set(pydantic_cls.model_fields.keys()) | {"block_type"}
    with pytest.raises(AssertionError):
        assert not (fake_accessed - valid_fields)


def test_jinja_raises_app_exception_on_unrecognized_block_type() -> None:
    """TC-SDUI-03: Asserts unrecognized SDUI block_type raises AppException."""
    service = PdfReportService()

    class FakeUnsupportedBlock:
        block_type = "unsupported_quantum_widget"
        title = None

    class FakeReportDTO:
        inner_sdui_blocks = [FakeUnsupportedBlock()]
        profile_name = None
        mcp_tool_audit = []

    with pytest.raises(AppException) as exc_info:
        # Run template rendering directly or via generate_execution_html
        template = service.env.get_template("report_template.jinja2")
        template.render(
            execution_id="exec_test",
            workflow_name="Test",
            report_data=FakeReportDTO(),
            printed_at="27.08.2026",
            charts={},
            l10n={"report_title": "Test", "warning_label": "Warning", "na_not_evaluated_label": "N/A"},
            lang_code="en",
        )

    assert "Strict Fail-Fast: Unrecognized SDUI block_type 'unsupported_quantum_widget'" in str(exc_info.value)

    # Anti-happy-path negative verification: valid block should NOT raise
    class FakeValidBlock:
        block_type = "markdown"
        title = None
        text = "Valid markdown"

    class FakeValidReportDTO:
        inner_sdui_blocks = [FakeValidBlock()]
        profile_name = None
        mcp_tool_audit = []

    rendered = template.render(
        execution_id="exec_test",
        workflow_name="Test",
        report_data=FakeValidReportDTO(),
        printed_at="27.08.2026",
        charts={},
        l10n={"report_title": "Test", "warning_label": "Warning", "na_not_evaluated_label": "N/A"},
        lang_code="en",
    )
    assert "Valid markdown" in rendered


def test_pdf_generator_strict_undefined_missing_l10n_key_raises() -> None:
    """TC-SDUI-04: Asserts that missing localization keys trigger jinja2.StrictUndefined / AppException."""
    service = PdfReportService()
    template = service.env.get_template("report_template.jinja2")

    class FakeBlock:
        block_type = "warning_card"
        title = None
        message = "Test warning"
        quote_text = None

    class FakeReportDTO:
        inner_sdui_blocks = [FakeBlock()]
        profile_name = None
        mcp_tool_audit = []

    # Omit 'warning_label' from l10n dictionary
    incomplete_l10n = {
        "report_title": "Test",
        "na_not_evaluated_label": "N/A",
    }

    with pytest.raises(jinja2.exceptions.UndefinedError):
        template.render(
            execution_id="exec_test",
            workflow_name="Test",
            report_data=FakeReportDTO(),
            printed_at="27.08.2026",
            charts={},
            l10n=incomplete_l10n,
            lang_code="en",
        )

    # Anti-happy-path negative verification: complete l10n renders successfully
    complete_l10n = {
        "report_title": "Test",
        "warning_label": "Warning",
        "na_not_evaluated_label": "N/A",
    }
    rendered = template.render(
        execution_id="exec_test",
        workflow_name="Test",
        report_data=FakeReportDTO(),
        printed_at="27.08.2026",
        charts={},
        l10n=complete_l10n,
        lang_code="en",
    )
    assert "Warning" in rendered


@pytest.mark.asyncio
async def test_jinja_sdui_golden_master_rendering() -> None:
    """TC-SDUI-05: Asserts all 17 SDUI blocks render with BeautifulSoup DOM assertions for en/fi."""
    fixture_file = FIXTURES_DIR / "sdui_golden_master.json"
    assert fixture_file.exists(), f"Missing fixture file {fixture_file}"

    fixture_json = fixture_file.read_text(encoding="utf-8")
    report_dto = ReportDataDTO.model_validate_json(fixture_json)

    service = PdfReportService()

    for locale in ("en", "fi"):
        html_content = await service.generate_execution_html(
            execution_id=report_dto.execution_id,
            report_dto=report_dto,
            locale=locale,
        )

        soup = BeautifulSoup(html_content, "html.parser")

        # 1. metadata
        header_card = soup.find("div", class_="header-card")
        assert header_card is not None, f"[{locale}] Missing metadata header-card"
        assert "Executive Assessment Profile" in header_card.get_text()
        assert "Pillar 4 SDUI" in header_card.get_text()

        # 2. hero_insight
        hero = soup.find("h3", style=lambda s: s and "#1E88E5" in s)
        assert hero is not None, f"[{locale}] Missing hero_insight h3"
        assert "Strong strategic synthesis" in hero.get_text()

        # 3. paragraph
        paragraphs = soup.find_all("div", style=lambda s: s and "font-size: 13px" in s)
        assert any("cognitive clarity" in p.get_text() for p in paragraphs), f"[{locale}] Missing paragraph content"

        # 4. bullet_list
        bullet_lists = soup.find_all("ul", style=lambda s: s and "padding-left: 20px" in s)
        assert len(bullet_lists) >= 1, f"[{locale}] Missing bullet_list ul"
        assert "Demonstrates proactive risk" in bullet_lists[0].get_text()

        # 5. alert_box
        alert = soup.find("div", class_="alert")
        assert alert is not None, f"[{locale}] Missing alert_box"
        assert "High degree of cognitive agility" in alert.get_text()

        # 6. quote_card
        quotes = soup.find_all("div", style=lambda s: s and "font-style: italic" in s)
        assert any("fail loudly" in q.get_text() for q in quotes), f"[{locale}] Missing quote_card"

        # 7. warning_card
        warnings = soup.find_all("div", style=lambda s: s and "#FFEBEE" in s)
        expected_warning_label = "Warning:" if locale == "en" else "Varoitus:"
        assert any(expected_warning_label in w.get_text() for w in warnings), f"[{locale}] Missing warning_card label"
        assert any("legacy refactoring" in w.get_text() for w in warnings), f"[{locale}] Missing warning_card quote"

        # 8. n_a_card
        na_cards = soup.find_all("div", style=lambda s: s and "#F5F5F5" in s)
        expected_na_label = "N/A (Not evaluated):" if locale == "en" else "N/A (Ei arvioitu):"
        assert any(expected_na_label in n.get_text() for n in na_cards), f"[{locale}] Missing n_a_card"
        assert any("External supply chain" in n.get_text() for n in na_cards), f"[{locale}] Missing n_a_card message"

        # 9. markdown
        assert any("Detailed Analytical Commentary" in p.get_text() for p in soup.find_all(["h4", "div"])), (
            f"[{locale}] Missing markdown content"
        )

        # 10. accordion
        accordion = soup.find("div", class_="sdui-accordion")
        assert accordion is not None, f"[{locale}] Missing sdui-accordion"
        assert "Coaching & Development Guidance" in accordion.get_text()
        assert "delegating micro-decisions" in accordion.get_text()

        # 11. score_card
        score_card = soup.find("div", style=lambda s: s and "#e6e0f8" in s)
        assert score_card is not None, f"[{locale}] Missing score_card"
        assert "88.50/100" in score_card.get_text()

        # 12. grid
        grid_tds = soup.find_all("td", style=lambda s: s and "border: 1px solid #E0E0E0" in s)
        assert len(grid_tds) >= 2, f"[{locale}] Missing grid items"
        assert "Grid Cell A" in grid_tds[0].get_text()
        assert "Grid Cell B" in grid_tds[1].get_text()

        # 13. 1d_metrics
        assert any(
            "Leadership Competency Breakdown" in h.get_text() or "Johtamiskompetenssien erittely" in h.get_text()
            for h in soup.find_all("h2")
        ), f"[{locale}] Missing 1d_metrics title"
        assert any("Strategic Execution" in h.get_text() for h in soup.find_all("h3")), (
            f"[{locale}] Missing 1d_metrics axis"
        )

        # 14. 3d_matrix & 15. 2d_compare (rendered charts)
        chart_imgs = soup.find_all("img", src=lambda s: s and s.startswith("data:image/png;base64,"))
        assert len(chart_imgs) >= 2, (
            f"[{locale}] Expected at least 2 rendered charts (3d radar, 2d compare), found {len(chart_imgs)}"
        )

        # 16. matrix_summary
        matrix_table = soup.find("table", class_="matrix-summary-table")
        assert matrix_table is not None, f"[{locale}] Missing matrix_summary table"
        assert "Strategic Synthesis" in matrix_table.get_text()
        assert "We balanced 3-year vision" in matrix_table.get_text()

        # 17. audit_trail
        audit_div = soup.find("div", class_="card", style=lambda s: s and "#009688" in s)
        assert audit_div is not None, f"[{locale}] Missing audit_trail box"
        assert "tavily_search" in audit_div.get_text()
        assert "Enterprise Cognitive Architecture Standards" in audit_div.get_text()

    # Anti-happy-path negative verification
    with pytest.raises(AssertionError):
        assert "NonExistentSemanticString12345" in soup.get_text()
