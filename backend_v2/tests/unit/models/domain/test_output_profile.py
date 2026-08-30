def test_output_profile_exports() -> None:
    """Test that output profile models are successfully exported."""
    from backend_v2.models.domain.output_profile import OutputProfile

    assert OutputProfile is not None
