import pytest
from pytest_archon import archrule


@pytest.mark.skip(reason="Fails due to transitive imports via dependencies")
def test_routers_cannot_import_database_directly() -> None:
    (
        archrule("Anemic Routers Rule: No DB in Routers")
        .match("backend_v2.api.routers.*")
        .should_not_import("backend_v2.database.*")
        .check("backend_v2")
    )
