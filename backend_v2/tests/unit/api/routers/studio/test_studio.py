"""Unit tests for Studio API Routers package (__init__.py).

Validates that the studio parent router correctly mounts all active domain routers
(workflows, prompt_blocks, steps, model_registry, mcp_gateways) and does not mount
deprecated or dead routers (system_configs).
"""

from fastapi import FastAPI

from backend_v2.api.routers.studio import router


def test_studio_router_prefix() -> None:
    """Verifies that the studio root router has the canonical /studio prefix."""
    assert router.prefix == "/studio"


def test_studio_router_includes_all_active_domain_routers() -> None:
    """Verifies that the studio parent router mounts all expected domain routers."""
    app = FastAPI()
    app.include_router(router)
    route_paths = list(app.openapi()["paths"].keys())

    # Workflows routes
    assert any(p.startswith("/studio/workflows") for p in route_paths)

    # Prompt blocks routes
    assert any(p.startswith("/studio/prompt-blocks") for p in route_paths)

    # Steps routes
    assert any(p.startswith("/studio/steps") for p in route_paths)

    # Model registry routes
    assert any(p.startswith("/studio/model-registry") for p in route_paths)

    # MCP gateways routes
    assert any(p.startswith("/studio/mcp-gateways") for p in route_paths)


def test_studio_router_excludes_dead_system_configs() -> None:
    """Verifies that the studio parent router does NOT mount dead system-configs."""
    app = FastAPI()
    app.include_router(router)
    route_paths = list(app.openapi()["paths"].keys())
    assert not any("/studio/system-configs" in p for p in route_paths)
