"""Automated FastAPI Route & Router SSOT Guardrail Tests.

Validates that:
1. No shadow, legacy /api/v1, or parallel routers exist across the application.
2. Specifically, no '/studio/profiles', '/system/system', or '/execution/reports' routes exist.
3. All 6 Studio blueprint routers expose universal CRUD + Clone lifecycle operations
   with strict OPAQUE_STRIPE_ID_REGEX path parameter patterns.
4. Non-cloneable entities reject /clone operations and eradicated shadow routes return 404.
5. No duplicate path and method collisions exist across the application.
"""

from typing import cast

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from backend_v2.main import app
from backend_v2.models.core_base import OPAQUE_STRIPE_ID_REGEX

BLUEPRINT_ROUTERS: list[dict[str, str]] = [
    {
        "name": "workflows",
        "root": "/api/v2/studio/workflows/",
        "item": "/api/v2/studio/workflows/{id}",
        "clone": "/api/v2/studio/workflows/{id}/clone",
        "param_name": "id",
    },
    {
        "name": "steps",
        "root": "/api/v2/studio/steps/",
        "item": "/api/v2/studio/steps/{id}",
        "clone": "/api/v2/studio/steps/{id}/clone",
        "param_name": "id",
    },
    {
        "name": "prompt_blocks",
        "root": "/api/v2/studio/prompt-blocks/",
        "item": "/api/v2/studio/prompt-blocks/{id}",
        "clone": "/api/v2/studio/prompt-blocks/{id}/clone",
        "param_name": "id",
    },
    {
        "name": "output_profiles",
        "root": "/api/v2/output-profiles/",
        "item": "/api/v2/output-profiles/{profile_id}",
        "clone": "/api/v2/output-profiles/{profile_id}/clone",
        "param_name": "profile_id",
    },
    {
        "name": "model_registry",
        "root": "/api/v2/studio/model-registry/",
        "item": "/api/v2/studio/model-registry/{registry_id}",
        "clone": "/api/v2/studio/model-registry/{registry_id}/clone",
        "param_name": "registry_id",
    },
    {
        "name": "mcp_gateways",
        "root": "/api/v2/studio/mcp-gateways/",
        "item": "/api/v2/studio/mcp-gateways/{gateway_id}",
        "clone": "/api/v2/studio/mcp-gateways/{gateway_id}/clone",
        "param_name": "gateway_id",
    },
]


@pytest.mark.asyncio
async def test_no_phantom_studio_profiles_routes() -> None:
    """Assert that no phantom routes under '/studio/profiles' or '/api/v2/studio/profiles' exist."""
    openapi = app.openapi()
    all_paths = list(openapi["paths"].keys())
    phantom_routes = [p for p in all_paths if "/studio/profiles" in p]
    assert phantom_routes == [], f"Phantom /studio/profiles routes detected: {phantom_routes}"


@pytest.mark.asyncio
async def test_no_v1_or_doubled_system_prefixes_in_routes() -> None:
    """Assert that zero routes start with '/api/v1' or doubled '/api/v2/system/system'."""
    all_routes = [route.path for route in app.routes if isinstance(route, APIRoute)]
    v1_routes = [p for p in all_routes if p.startswith("/api/v1")]
    assert v1_routes == [], f"Legacy /api/v1 routes detected: {v1_routes}"

    doubled_system = [p for p in all_routes if p.startswith("/api/v2/system/system")]
    assert doubled_system == [], f"Doubled /system/system routes detected: {doubled_system}"


@pytest.mark.asyncio
async def test_no_shadow_or_duplicate_router_mounts() -> None:
    """Assert zero shadow routes for execution reports, execution workflows, or dead system configs."""
    all_routes = [route.path for route in app.routes if isinstance(route, APIRoute)]

    shadow_reports = [p for p in all_routes if p.startswith("/api/v2/execution/reports")]
    assert shadow_reports == [], f"Shadow execution reports routes detected: {shadow_reports}"

    shadow_workflows = [p for p in all_routes if p.startswith("/api/v2/execution/workflows")]
    assert shadow_workflows == [], f"Shadow execution workflows routes detected: {shadow_workflows}"

    shadow_configs = [p for p in all_routes if p.startswith("/api/v2/studio/system-configs")]
    assert shadow_configs == [], f"Dead studio system-configs routes detected: {shadow_configs}"


@pytest.mark.asyncio
async def test_canonical_specialized_routes_exist_once() -> None:
    """Assert that consolidated specialized routes exist once and under canonical paths."""
    paths_dict = app.openapi()["paths"]

    # Consolidated Workflow UI schema route
    wf_schema_path = "/api/v2/studio/workflows/{id}/ui_schema"
    assert wf_schema_path in paths_dict, f"Expected canonical route '{wf_schema_path}' in OpenAPI schema"
    assert "get" in paths_dict[wf_schema_path]

    # Consolidated Report compilation and listing routes
    exe_reports_path = "/api/v2/executions/{execution_id}/reports"
    assert exe_reports_path in paths_dict, f"Expected canonical route '{exe_reports_path}' in OpenAPI schema"
    assert "post" in paths_dict[exe_reports_path]
    assert "get" in paths_dict[exe_reports_path]

    # Consolidated Report artifact route
    rep_path = "/api/v2/reports/{report_id}"
    assert rep_path in paths_dict, f"Expected canonical route '{rep_path}' in OpenAPI schema"
    assert "get" in paths_dict[rep_path]
    assert "delete" in paths_dict[rep_path]

    # Consolidated External report route
    ext_rep_path = "/api/v2/external/reports/{report_id}"
    assert ext_rep_path in paths_dict, f"Expected canonical route '{ext_rep_path}' in OpenAPI schema"
    assert "get" in paths_dict[ext_rep_path]


@pytest.mark.asyncio
async def test_all_blueprint_routers_crud_clone_parity() -> None:
    """Assert all 6 blueprint routers expose universal CRUD + Clone lifecycle operations and Opaque ID schemas."""
    paths_dict = app.openapi()["paths"]

    for blueprint in BLUEPRINT_ROUTERS:
        name = blueprint["name"]
        root_path = blueprint["root"]
        item_path = blueprint["item"]
        clone_path = blueprint["clone"]
        param_name = blueprint["param_name"]

        # 1. Root collection endpoints: GET and POST
        assert root_path in paths_dict, f"[{name}] Missing root path '{root_path}'"
        assert "get" in paths_dict[root_path], f"[{name}] Missing GET on '{root_path}'"
        assert "post" in paths_dict[root_path], f"[{name}] Missing POST on '{root_path}'"

        # 2. Item entity endpoints: GET, PUT, and DELETE
        assert item_path in paths_dict, f"[{name}] Missing item path '{item_path}'"
        assert "get" in paths_dict[item_path], f"[{name}] Missing GET on '{item_path}'"
        assert "put" in paths_dict[item_path], f"[{name}] Missing PUT on '{item_path}'"
        assert "delete" in paths_dict[item_path], f"[{name}] Missing DELETE on '{item_path}'"

        # 3. Clone endpoint: POST
        assert clone_path in paths_dict, f"[{name}] Missing clone path '{clone_path}'"
        assert "post" in paths_dict[clone_path], f"[{name}] Missing POST on '{clone_path}'"

        # 4. Verify OPAQUE_STRIPE_ID_REGEX path parameter regex pattern on GET item
        item_get_op = paths_dict[item_path]["get"]
        parameters = item_get_op.get("parameters", [])
        param_def = next((p for p in parameters if p.get("name") == param_name and p.get("in") == "path"), None)
        assert param_def is not None, f"[{name}] Path parameter '{param_name}' not documented on '{item_path}'"

        schema = cast(dict[str, str], param_def.get("schema", {}))
        assert schema.get("pattern") == OPAQUE_STRIPE_ID_REGEX, (
            f"[{name}] Expected path parameter '{param_name}' pattern '{OPAQUE_STRIPE_ID_REGEX}', got '{schema.get('pattern')}'"
        )


@pytest.mark.asyncio
async def test_non_cloneable_routers_reject_clone_partition() -> None:
    """Verify non-cloneable execution and report routers do not expose /clone endpoints and reject requests."""
    paths_dict = app.openapi()["paths"]
    non_cloneable_prefixes = ["/api/v2/executions", "/api/v2/reports", "/api/v2/system"]

    for path in paths_dict.keys():
        if any(path.startswith(prefix) for prefix in non_cloneable_prefixes):
            assert not path.endswith("/clone"), f"Non-cloneable router exposes illegal clone path: {path}"

    client = TestClient(app)
    mock_id = "exe_0195f3a0000070008123456789abcdef"
    res_exe_clone = client.post(f"/api/v2/executions/{mock_id}/clone")
    assert res_exe_clone.status_code == 404

    res_rep_clone = client.post("/api/v2/reports/rep_0195f3a0000070008123456789abcdef/clone")
    assert res_rep_clone.status_code == 404


@pytest.mark.asyncio
async def test_eradicated_shadow_routes_return_404_partition() -> None:
    """Verify that all eradicated legacy and shadow routes strictly return 404 Not Found."""
    client = TestClient(app)

    # Legacy /api/v1 external reports
    res_v1_ext = client.get("/api/v1/external/reports/rep_0195f3a0000070008123456789abcdef")
    assert res_v1_ext.status_code == 404

    # Shadow /api/v2/execution/reports
    res_shadow_rep = client.get("/api/v2/execution/reports/rep_0195f3a0000070008123456789abcdef")
    assert res_shadow_rep.status_code == 404

    # Eradicated split workflow ui_schema under /execution
    res_split_wf = client.get("/api/v2/execution/workflows/wor_0195f3a0000070008123456789abcdef/ui_schema")
    assert res_split_wf.status_code == 404

    # Eradicated empty studio system-configs router
    res_sys_cfg = client.get("/api/v2/studio/system-configs/")
    assert res_sys_cfg.status_code == 404

    # Doubled /api/v2/system/system
    res_doubled_sys = client.get("/api/v2/system/system/hooks")
    assert res_doubled_sys.status_code == 404


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
