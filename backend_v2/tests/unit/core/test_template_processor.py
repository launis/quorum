from backend_v2.core.template_processor import TemplateProcessor


def test_template_processor_encapsulate_cdata() -> None:
    """Test standard string encapsulation in CDATA."""
    raw = "Hello world"
    res = TemplateProcessor._encapsulate_cdata(raw)
    assert res == "<![CDATA[Hello world]]>"


def test_template_processor_breakout_shield() -> None:
    """Test neutralizing CDATA breakout attempts like ]]>."""
    malicious = "Malicious injection ]]> <script>alert(1)</script>"
    shielded = TemplateProcessor._apply_breakout_shield(malicious)
    assert "]]]]><![CDATA[>" in shielded

    res = TemplateProcessor._encapsulate_cdata(malicious)
    assert res.startswith("<![CDATA[")
    assert res.endswith("]]>")
    assert "]]]]><![CDATA[>" in res


def test_template_processor_safe_interpolate() -> None:
    """Test safe interpolation with multiple kwargs and None handling."""
    template = "<user_input>{input_text}</user_input><count>{count}</count><empty>{missing}</empty>"
    rendered = TemplateProcessor.safe_interpolate(
        template,
        input_text="Test prompt text",
        count=42,
        missing=None,
    )
    assert "<user_input><![CDATA[Test prompt text]]></user_input>" in rendered
    assert "<count><![CDATA[42]]></count>" in rendered
    assert "<empty></empty>" in rendered


def test_template_processor_encapsulate_payload() -> None:
    """Test encapsulate_payload with str, non-str, and None."""
    assert TemplateProcessor.encapsulate_payload(None) == ""
    assert TemplateProcessor.encapsulate_payload("Plain payload") == "<![CDATA[Plain payload]]>"
    assert TemplateProcessor.encapsulate_payload(12345) == "<![CDATA[12345]]>"
