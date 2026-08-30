"""Scoring Hook Package.

Exposes the decomposed scoring hooks through a Strangler Fig Facade for seamless backward compatibility.
"""

from backend_v2.hooks.scoring.falsifier_hook import (
    apply_scoring_logic_hook as apply_scoring_logic_hook,
)
from backend_v2.hooks.scoring.matrix_hook import (
    matrix_scoring_hook as matrix_scoring_hook,
)
from backend_v2.hooks.scoring.models import (
    ScoringPayloadWrapper as ScoringPayloadWrapper,
)
from backend_v2.hooks.scoring.models import (
    StateInputWrapper as StateInputWrapper,
)
from backend_v2.hooks.scoring.normalization_hook import (
    normalize_matrix_scores_hook as normalize_matrix_scores_hook,
)
from backend_v2.hooks.scoring.normalization_hook import (
    recalculate as recalculate,
)
from backend_v2.hooks.scoring.passivity_hook import (
    enforce_passivity_penalty_hook as enforce_passivity_penalty_hook,
)

__all__ = [
    "ScoringPayloadWrapper",
    "StateInputWrapper",
    "apply_scoring_logic_hook",
    "enforce_passivity_penalty_hook",
    "matrix_scoring_hook",
    "normalize_matrix_scores_hook",
    "recalculate",
]
