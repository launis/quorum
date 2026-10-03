from backend_v2.services.file_driver import FileDriver


def test_file_driver_protocol() -> None:
    """Verify that the FileDriver Protocol is correctly defined."""
    # A protocol class cannot be instantiated directly if it has abstract methods,
    # but we can verify its attributes.
    file_driver_members = dir(FileDriver)
    assert "save" in file_driver_members
    assert "read" in file_driver_members
    assert "delete" in file_driver_members
    assert "delete_directory" in file_driver_members
    assert "exists" in file_driver_members
    assert "get_url" in file_driver_members
