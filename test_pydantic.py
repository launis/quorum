import json
# v2_core.py import
from backend_v2.models.v2_core import Gauge1DComponent

comp = Gauge1DComponent(
    type="1d_gauge",
    data_path="$results.score",
    display_value_only="12.3",
    visual_pct=45.6
)

print(comp.model_dump(mode="json"))
