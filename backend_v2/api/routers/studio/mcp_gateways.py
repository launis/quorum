import logging

from fastapi import APIRouter
from pydantic import BaseModel

from backend_v2.api.dependencies import CurrentUserDep, StudioServiceDep
from backend_v2.models.v2_core import SystemConfigMCPGateways


class MCPGatewayDeleteResponse(BaseModel):
    status: str
    deleted_id: str

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mcp-gateways", tags=["Admin Studio V2 - MCP Gateways"])


@router.get("/", response_model=list[SystemConfigMCPGateways])
async def get_all_mcp_gateways(
    current_user: CurrentUserDep, studio_service: StudioServiceDep
) -> list[SystemConfigMCPGateways]:
    """Retrieve all MCP Gateways configurations securely via SSOT Service Layer."""
    return await studio_service.list_mcp_gateways(current_user)


@router.get("/{gateway_id}", response_model=SystemConfigMCPGateways)
async def get_mcp_gateway(
    gateway_id: str,
    current_user: CurrentUserDep,
    studio_service: StudioServiceDep,
) -> SystemConfigMCPGateways:
    """Retrieve a single MCP Gateway configuration securely via SSOT Service Layer."""
    return await studio_service.get_mcp_gateways(current_user, gateway_id)


@router.put("/{gateway_id}", response_model=SystemConfigMCPGateways)
async def save_mcp_gateway(
    gateway_id: str,
    data: SystemConfigMCPGateways,
    current_user: CurrentUserDep,
    studio_service: StudioServiceDep,
) -> SystemConfigMCPGateways:
    """Update an MCP Gateway configuration securely via SSOT Service Layer."""
    return await studio_service.save_mcp_gateways(current_user, gateway_id, data)


@router.delete("/{gateway_id}", response_model=MCPGatewayDeleteResponse)
async def delete_mcp_gateway(
    gateway_id: str, current_user: CurrentUserDep, studio_service: StudioServiceDep
) -> MCPGatewayDeleteResponse:
    """Delete an MCP Gateway configuration securely via SSOT Service Layer."""
    try:
        await studio_service.delete_system_config(current_user, gateway_id)
        return MCPGatewayDeleteResponse(status="success", deleted_id=gateway_id)
    except Exception as e:
        from backend_v2.exceptions import AppException, ErrorCodes
        if isinstance(e, AppException):
            raise
        logger.error(
            "[MCPGatewaysRouter] %s: %s",
            ErrorCodes.INTERNAL_SERVER_ERROR.name,
            str(e),
            exc_info=True,
            extra={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value, "target_id": gateway_id, "error": str(e)},
        )
        raise AppException(
            message="Internal delete failure",
            status_code=500,
            details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
        ) from e


@router.post("/{gateway_id}/clone", response_model=SystemConfigMCPGateways)
async def clone_mcp_gateway(
    gateway_id: str,
    current_user: CurrentUserDep,
    studio_service: StudioServiceDep,
) -> SystemConfigMCPGateways:
    """Deep clone an MCP Gateway configuration securely via SSOT Service Layer."""
    return await studio_service.clone_mcp_gateways(current_user, gateway_id)
