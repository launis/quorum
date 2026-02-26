import asyncio
import json
import uuid
import os
from datetime import UTC, datetime

# Ensure working dir is set
os.chdir("C:/src/quorum")

from backend.dependencies import get_db, get_usage_service
from backend.services.usage_service import UsageService
from backend.database.repository import UnifiedWorkflowRepository

async def test_usage_tracking():
    print("Testing Usage Tracking and Aggregation...")
    db = await get_db()
    repo = UnifiedWorkflowRepository(db)
    service = UsageService(repo)
    
    # 1. Track Usage
    print("1. Tracking new usage...")
    record = await service.track_usage(
        org_id="system_org",
        user_id="test_user",
        model="vertex_ai/gemini-2.5-flash",
        input_tokens=150,
        output_tokens=50,
        cost_usd=0.0025,
        system_fingerprint="test_fingerprint_001"
    )
    print(f"Usage tracked with ID: {record.id}")
    
    # 2. Verify aggregate
    print("2. Verifying aggregates...")
    period = datetime.now(UTC).strftime("%Y-%m")
    
    sys_agg = await repo.get_usage_aggregate("system", None, period)
    org_agg = await repo.get_usage_aggregate("organization", "system_org", period)
    user_agg = await repo.get_usage_aggregate("user", "test_user", period)
    
    print("\nSYSTEM AGGREGATE:")
    print(json.dumps(sys_agg, indent=2))
    
    print("\nORG AGGREGATE:")
    print(json.dumps(org_agg, indent=2))
    
    print("\nUSER AGGREGATE:")
    print(json.dumps(user_agg, indent=2))
    
    # 3. Test report generation
    print("\n3. Testing report generation...")
    report = await service.get_usage_report("system")
    print(report.model_dump_json(indent=2))

if __name__ == "__main__":
    asyncio.run(test_usage_tracking())
