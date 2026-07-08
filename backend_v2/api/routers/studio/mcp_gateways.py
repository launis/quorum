"""Admin Studio MCP Gateways API Router.

Provides endpoints to manage MCP gateway configurations.
"""

import logging

from fastapi import APIRouter

from backend_v2.api.dependencies import CurrentUserDep, StudioSystemConfigServiceDep
from backend_v2.models.dtos.studio import MCPGatewayDeleteResponse
from backend_v2.models.v2_core import SystemConfigMCPGateways

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mcp-gateways", tags=["Admin Studio V2 - MCP Gateways"])


@router.get("/", response_model=list[SystemConfigMCPGateways])
async def get_all_mcp_gateways(
    current_user: CurrentUserDep, studio_service: StudioSystemConfigServiceDep
) -> list[SystemConfigMCPGateways]:
    """Retrieve all MCP Gateways configurations securely via SSOT Service Layer.

    Args:
        current_user: The authenticated user making the request.
        studio_service: The studio service dependency.

    Returns:
        A list of MCP gateways configurations.

    Raises:
        AppException: If fetching MCP gateways fails.
    """
    return await studio_service.list_mcp_gateways(current_user)


@router.post("/", response_model=SystemConfigMCPGateways)
async def create_mcp_gateways(
    current_user: CurrentUserDep, studio_service: StudioSystemConfigServiceDep
) -> SystemConfigMCPGateways:
    """Create a new MCP Gateway Config draft securely via SSOT.

    Args:
        current_user: The authenticated user making the request.
        studio_service: The studio service dependency.

    Returns:
        The newly created MCP gateway draft configuration.

    Raises:
        AppException: If creating the draft fails.
    """
    return await studio_service.create_mcp_gateway_draft(current_user)


@router.get("/{gateway_id}", response_model=SystemConfigMCPGateways)
async def get_mcp_gateway(
    gateway_id: str,
    current_user: CurrentUserDep,
    studio_service: StudioSystemConfigServiceDep,
) -> SystemConfigMCPGateways:
    """Retrieve a single MCP Gateway configuration securely via SSOT Service Layer.

    Args:
        gateway_id: The unique identifier of the MCP gateway.
        current_user: The authenticated user making the request.
        studio_service: The studio service dependency.

    Returns:
        The requested MCP gateway configuration.

    Raises:
        ResourceNotFoundError: If the MCP gateway is not found.
        AppException: If fetching the MCP gateway fails.
    """
    return await studio_service.get_mcp_gateways(current_user, gateway_id)


@router.put("/{gateway_id}", response_model=SystemConfigMCPGateways)
async def save_mcp_gateway(
    gateway_id: str,
    data: SystemConfigMCPGateways,
    current_user: CurrentUserDep,
    studio_service: StudioSystemConfigServiceDep,
) -> SystemConfigMCPGateways:
    """Update an MCP Gateway configuration securely via SSOT Service Layer.

    Args:
        gateway_id: The unique identifier of the MCP gateway.
        data: The new configuration data.
        current_user: The authenticated user making the request.
        studio_service: The studio service dependency.

    Returns:
        The updated MCP gateway configuration.

    Raises:
        ResourceNotFoundError: If the MCP gateway is not found.
        AppException: If updating the MCP gateway fails.
    """
    return await studio_service.save_mcp_gateways(current_user, gateway_id, data)


@router.delete("/{gateway_id}", response_model=MCPGatewayDeleteResponse)
async def delete_mcp_gateway(
    gateway_id: str, current_user: CurrentUserDep, studio_service: StudioSystemConfigServiceDep
) -> MCPGatewayDeleteResponse:
    """Delete an MCP Gateway configuration securely via SSOT Service Layer.

    Args:
        gateway_id: The unique identifier of the MCP gateway to delete.
        current_user: The authenticated user making the request.
        studio_service: The studio service dependency.

    Returns:
        An MCPGatewayDeleteResponse confirming the deletion.

    Raises:
        ResourceNotFoundError: If the MCP gateway is not found.
        AppException: If deleting the MCP gateway fails.
    """
    await studio_service.delete_system_config(current_user, gateway_id)
    return MCPGatewayDeleteResponse(status="success", deleted_id=gateway_id)


@router.post("/{gateway_id}/clone", response_model=SystemConfigMCPGateways)
async def clone_mcp_gateway(
    gateway_id: str,
    current_user: CurrentUserDep,
    studio_service: StudioSystemConfigServiceDep,
) -> SystemConfigMCPGateways:
    """Deep clone an MCP Gateway configuration securely via SSOT Service Layer.

    Args:
        gateway_id: The unique identifier of the MCP gateway to clone.
        current_user: The authenticated user making the request.
        studio_service: The studio service dependency.

    Returns:
        The newly cloned MCP gateway configuration.

    Raises:
        ResourceNotFoundError: If the source MCP gateway is not found.
        AppException: If cloning the MCP gateway fails.
    """
    return await studio_service.clone_mcp_gateways(current_user, gateway_id)
