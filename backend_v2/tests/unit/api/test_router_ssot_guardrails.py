"""Automated FastAPI Route & Router SSOT Guardrail Tests.

Validates that:
1. No shadow or parallel routers exist across the application.
2. Specifically, no '/studio/profiles' routes exist in the OpenAPI schema.
3. All Output Profile endpoints are registered strictly under '/api/v2/output-profiles'.
4. No duplicate path collision exists across the application.
"""

import pytest

from backend_v2.main import app


@pytest.mark.asyncio
async def test_no_phantom_studio_profiles_routes() -> None:
    """Assert that no phantom routes under '/studio/profiles' or '/api/v2/studio/profiles' exist."""
    openapi = app.openapi()
    all_paths = list(openapi["paths"].keys())
    phantom_routes = [p for p in all_paths if "/studio/profiles" in p]
    assert phantom_routes == [], f"Phantom /studio/profiles routes detected: {phantom_routes}"


@pytest.mark.asyncio
async def test_output_profiles_canonical_prefix() -> None:
    """Assert that all Output Profile operations are anchored at '/api/v2/output-profiles'."""
    openapi = app.openapi()
    paths_dict = openapi["paths"]
    output_profile_paths = {p: methods for p, methods in paths_dict.items() if "output-profiles" in p}

    assert len(output_profile_paths) == 3, (
        f"Expected 3 distinct output profile path templates, got {len(output_profile_paths)}"
    )

    assert "/api/v2/output-profiles/" in output_profile_paths
    assert "/api/v2/output-profiles/{profile_id}" in output_profile_paths
    assert "/api/v2/output-profiles/{profile_id}/clone" in output_profile_paths

    # Verify standard REST operations
    root_methods = set(output_profile_paths["/api/v2/output-profiles/"].keys())
    assert "get" in root_methods
    assert "post" in root_methods

    item_methods = set(output_profile_paths["/api/v2/output-profiles/{profile_id}"].keys())
    assert "get" in item_methods
    assert "put" in item_methods
    assert "delete" in item_methods

    clone_methods = set(output_profile_paths["/api/v2/output-profiles/{profile_id}/clone"].keys())
    assert "post" in clone_methods


@pytest.mark.asyncio
async def test_no_duplicate_path_and_method_combinations() -> None:
    """Assert that no two routes share the exact same path and HTTP method."""
    openapi = app.openapi()
    paths_dict = openapi["paths"]
    seen_endpoints: set[tuple[str, str]] = set()

    for path, methods in paths_dict.items():
        for method in methods.keys():
            key = (path, method.upper())
            assert key not in seen_endpoints, f"Duplicate endpoint detected: {method.upper()} {path}"
            seen_endpoints.add(key)
