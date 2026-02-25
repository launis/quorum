from pydantic import BaseModel


class OrganizationUsageResponse(BaseModel):
    """Usage statistics for an organization."""

    total_cost_usd: float
    quota_limit_usd: float
    tpm_limit: int
    rpm_limit: int
    percentage_used: float
    period: str


class DetailedUsageResponse(OrganizationUsageResponse):
    """Expanded usage statistics including telemetry metrics."""

    total_runs: int = 0
    total_processing_time_ms: int = 0
    models_used: dict[str, int] = {}
    workflows_used: dict[str, int] = {}
