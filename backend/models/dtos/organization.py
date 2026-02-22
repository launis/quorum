from pydantic import BaseModel


class OrganizationUsageResponse(BaseModel):
    """Usage statistics for an organization."""

    total_cost_usd: float
    quota_limit_usd: float
    tpm_limit: int
    rpm_limit: int
    percentage_used: float
    period: str
