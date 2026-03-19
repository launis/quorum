import json
import asyncio
from backend_v2.models.v2_core import ExecutionRecord, RenderBlueprint, Gauge1DComponent

record = ExecutionRecord(
    id="test",
    pipeline="test",
    blueprint=RenderBlueprint(
        version="1.0",
        components=[
            Gauge1DComponent(
                type="1d_gauge",
                data_path="$results.score",
                display_value_only="12.3",
                visual_pct=45.6
            )
        ]
    )
)

print(record.model_dump_json(exclude_none=True))
