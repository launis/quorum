def test_synthesis_schema_does_not_contain_complex_blocks() -> None:
    """Test that SynthesisOutputDTO json schema is constrained.

    Vertex AI throws a 400 'too many states for serving' if the schema contains
    massive polymorphic unions like SduiGridBlock or HeroInsightBlock.
    """
    from backend_v2.models.dtos.synthesis import SynthesisOutputDTO

    schema = SynthesisOutputDTO.model_json_schema()
    schema_str = str(schema)
    assert "SduiGridBlock" not in schema_str, "Schema contains forbidden complex block SduiGridBlock"
    assert "HeroInsightBlock" not in schema_str, "Schema contains forbidden complex block HeroInsightBlock"
    assert "HeaderBlock" not in schema_str, "Schema contains forbidden complex block HeaderBlock"
