import re
import os

target_file = r"c:\src\quorum\backend_v2\hooks\scoring.py"

with open(target_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
imports_to_hoist = set()

for line in lines:
    stripped = line.strip()
    # Check if the line is an inline import
    if stripped.startswith("from backend_v2.") or stripped.startswith("import hashlib") or stripped.startswith("import json") or stripped.startswith("from pydantic import ValidationError"):
        if not line.startswith("from ") and not line.startswith("import "):
            # It's an indented import
            continue  # Skip it (delete it from new_lines)
            
    new_lines.append(line)

# Let's do it safely: we just use regex to remove any indented import statements
def clean_imports(lines):
    cleaned = []
    for line in lines:
        stripped = line.strip()
        is_inline_import = False
        
        # Match indented imports
        if line.startswith(" ") or line.startswith("\t"):
            if stripped.startswith("from backend_v2.") or stripped.startswith("from pydantic ") or stripped.startswith("import hashlib") or stripped.startswith("import json"):
                is_inline_import = True
        
        if not is_inline_import:
            cleaned.append(line)
            
    return cleaned

cleaned_lines = clean_imports(lines)

# Now define the global imports block
global_imports = """\"\"\"Scoring Hook for evaluating agent performance and applying penalties.\"\"\"

import hashlib
import json
import logging
from typing import Any

from pydantic import ValidationError

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState, hook_registry
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.judge import JudgeScoreCard
from backend_v2.models.domain.scoring import StepFalsifierDTO, StepGuardDTO, StepPanelDTO
from backend_v2.models.dtos.lightweight_matrix import LightweightMatrixOutput, MicroCotDTO, StrictMatrixPayload
from backend_v2.models.enums import (
    CognitiveFlowStatus,
    CognitiveFlowThreshold,
    EvaluationMandate,
    ScoringCalibrationThresholds,
    WaterfallThreshold,
    XaiExtensionType,
)
from backend_v2.settings import get_settings
from backend_v2.utils.math_utils import (
    calculate_progressive_dampening_score,
    calculate_waterfall_floor,
    calculate_weighted_score,
    normalize_score_to_100,
    scale_to_custom_range,
)

logger = logging.getLogger(__name__)

"""

# Find the index to insert after docstring and original global imports
start_idx = 0
for i, line in enumerate(cleaned_lines):
    if line.startswith("def _extract_guard_flag"):
        start_idx = i
        break

final_lines = [global_imports] + cleaned_lines[start_idx:]

with open(target_file, "w", encoding="utf-8") as f:
    f.writelines(final_lines)

print("Imports hoisted successfully!")
