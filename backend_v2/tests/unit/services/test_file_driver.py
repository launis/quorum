from backend_v2.services.file_driver import FileDriver


def test_file_driver_protocol() -> None:
    """Verify that the FileDriver Protocol is correctly defined."""
    # A protocol class cannot be instantiated directly if it has abstract methods,
    # but we can verify its attributes.
    assert hasattr(FileDriver, "save")
    assert hasattr(FileDriver, "read")
    assert hasattr(FileDriver, "delete")
    assert hasattr(FileDriver, "delete_directory")
    assert hasattr(FileDriver, "exists")
    assert hasattr(FileDriver, "get_url")
