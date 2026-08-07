from typing import Annotated, Any, Literal

from pydantic import Field, PrivateAttr, ValidationInfo, field_validator, model_validator

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.dtos.quote_evidence import LLMExtractedQuote
from backend_v2.models.enums import DEFAULT_NULL_HYPOTHESIS_BLACKLIST, LaxVisualIntent
from backend_v2.settings import get_settings

_settings = get_settings()
_schema_max_quotes_target = _settings.schema_max_quotes_target
_schema_max_quotes = _schema_max_quotes_target + 5
_schema_max_quote_length = _settings.schema_max_quote_length


class ReasoningStepDTO(V2CoreBase):
    """Structured micro-CoT reasoning step schema to prevent JSON escaping issues."""

    step_1_identify_premise: Annotated[str, Field(description="Extract the exact claim from the prompt.")]
    step_2_scan_source: Annotated[
        str, Field(description="Analyze if the source text physically contains evidence for or against the premise.")
    ]
    step_3_evaluate_anti_patterns: Annotated[
        str, Field(description="Check if any strict anti-patterns or exclusions apply.")
    ]
    step_4_final_conclusion: Annotated[str, Field(description="Synthesize steps 1-3 into a final logical conclusion.")]


class LightweightExtractionAtom(V2CoreBase):
    """Strict schema for Zero-Reasoning extraction protocols.

    This model enforces the 'Zero-Reasoning Mandate' by lacking cognitive fields
    like semantic_reasoning. This reduces token load and prevents hallucination.

    Attributes:
        atom_id: The unique identifier tracking this extraction atom logic.
        extracted_facts: Dictionary of data fragments extracted from source.
        exact_quote: Strict text matched physically within the source text.
        status: The evaluation status. Must be one of PASS, FAIL, DLQ.
        confidence: Internal confidence factor metric between 0.0 and 1.0.
    """

    atom_id: str
    used_source_aliases: Annotated[
        list[str],
        Field(
            default_factory=list,
            description="List of exact <search_result id> strings you relied upon for this specific extraction.",
        ),
    ]
    used_evidence_ids: Annotated[
        list[str],
        Field(
            default_factory=list,
            description="Resolved document or search IDs relied upon for this specific extraction.",
        ),
    ]
    extracted_facts: Annotated[dict[str, str | None], Field(default_factory=dict)]
    exact_quotes: Annotated[
        list[LLMExtractedQuote],
        Field(
            default_factory=list,
            max_length=_schema_max_quotes,
            description=(
                f"A list of physically contiguous, character-for-character verbatim substrings extracted "
                f"directly from the source text. Maximum {_schema_max_quotes_target} items. Each quote MUST be UNDER {_schema_max_quote_length} characters. "
                f"NEVER translate, fix grammar, paraphrase, or alter the language. The quote MUST remain "
                f"in the ORIGINAL language of the source document."
            ),
        ),
    ]
    status: Annotated[
        Literal["PASS", "FAIL", "CONTESTED", "DLQ"] | None,
        Field(default=None, description="The evaluation status. Must be one of PASS, FAIL, CONTESTED, DLQ."),
    ]
    confidence: float | None = None

    @field_validator("exact_quotes", mode="before")
    @classmethod
    def _truncate_quotes(cls, v: Any) -> Any:
        if isinstance(v, list):
            max_len = _schema_max_quotes
            if len(v) > max_len:
                return v[:max_len]
        return v

    @field_validator("confidence")
    @classmethod
    def _validate_confidence(cls, v: float | None) -> float | None:
        if v is not None and not (0.0 <= v <= 1.0):
            raise ValueError("confidence must be between 0.0 and 1.0")
        return v

    _null_hypothesis_blacklist: frozenset[str] = PrivateAttr(default_factory=frozenset)

    @model_validator(mode="after")
    def _inject_context(self, info: ValidationInfo) -> LightweightExtractionAtom:
        context = info.context or {}
        self._null_hypothesis_blacklist = context.get("null_hypothesis_blacklist", DEFAULT_NULL_HYPOTHESIS_BLACKLIST)
        return self

    @property
    def evidence_found(self) -> bool:
        """Prevent Phantom Booleans: Sanitize hallucinated nulls produced by LLMs.

        Returns:
            True if meaningful, non-hallucinated evidence text is found, else False.
        """
        if self.exact_quotes:
            for quote in self.exact_quotes:
                if quote.text and quote.text.strip().lower() not in self._null_hypothesis_blacklist:
                    return True
        for val in self.extracted_facts.values():
            if val is not None and val.strip().lower() not in self._null_hypothesis_blacklist:
                return True
        return False

    def calculate_rule_satisfied(self, inverse_evidence: bool, allow_contextual_override: bool = False) -> bool | str:
        """Deterministic judgment. Lightweight extraction does not support contextual_override.

        Args:
            inverse_evidence: True to flip logic condition (e.g. absence means PASS).
            allow_contextual_override: Ignored parameter for strict interface parity.

        Returns:
            Evaluated boolean rule, or string 'DLQ' if dead letter queue was hit.
        """
        if self.status:
            if self.status == "DLQ":
                return "DLQ"
            # Phase 1: CONTESTED bypasses inversion logic
            if self.status == "CONTESTED":
                return True
            evidence_found = self.status == "PASS"
            if inverse_evidence:
                return not evidence_found
            return evidence_found

        if inverse_evidence:
            return not self.evidence_found
        return self.evidence_found

    # Compatibility properties for scoring.py
    @property
    def contextual_override(self) -> bool:
        return False

    @property
    def structural_location(self) -> str:
        return "N/A"

    @property
    def semantic_reasoning(self) -> str:
        return "N/A (Lightweight extraction)"


class MatrixEvaluationItemDTO(V2CoreBase):
    """Strict schema for individual matrix evaluation items."""

    atom_id: str
    semantic_reasoning: str = ""


class AtomEvaluationItemDTO(V2CoreBase):
    """Strict schema for individual atom evaluations in the waterfall pipeline.

    Attributes:
        atom_id: Identifying key of the executed atom node.
        extracted_facts: Collected findings data explicitly extracted from context.
        exact_quote: String data ensuring precise verification boundaries.
        internal_logic_en: Rigorous internal mathematical/logical Chain of Thought in English.
        status: Evaluated lifecycle status state marker string.
        semantic_reasoning: Detailed reasoning for the evaluation output.
        contextual_override: Boolean flag enabling non-strict logic jumps.
        structural_location: Location reference where exact context occurred.
        dlq_status: Internal indicator to track failure tracking queues.
        is_mcp_verified: True if quotes were dynamically verified against MCP source texts.
        mcp_source_reference: The ID of the MCP source where the quote was matched.
    """

    atom_id: str
    used_source_aliases: Annotated[
        list[str],
        Field(
            default_factory=list,
            description="List of exact <search_result id> strings you relied upon for this specific extraction.",
        ),
    ]
    used_evidence_ids: Annotated[
        list[str],
        Field(
            default_factory=list,
            description="Resolved document or search IDs relied upon for this specific extraction.",
        ),
    ]
    extracted_facts: Annotated[dict[str, str | None], Field(default_factory=dict)]
    exact_quotes: Annotated[
        list[LLMExtractedQuote],
        Field(
            default_factory=list,
            max_length=_schema_max_quotes,
            description=(
                f"A list of physically contiguous, character-for-character verbatim substrings extracted "
                f"directly from the source text. Maximum {_schema_max_quotes_target} items. Each quote MUST be UNDER {_schema_max_quote_length} characters. "
                f"NEVER translate, fix grammar, paraphrase, or alter the language. The quote MUST remain "
                f"in the ORIGINAL language of the source document."
            ),
        ),
    ]
    internal_logic_en: Annotated[
        ReasoningStepDTO,
        Field(
            description="Rigorous internal mathematical/logical Chain of Thought deduction mapped step-by-step in English."
        ),
    ]
    status: Annotated[
        Literal["PASS", "FAIL", "CONTESTED", "DLQ"] | None,
        Field(default=None, description="The evaluation status. Must be one of PASS, FAIL, CONTESTED, DLQ."),
    ]
    chart_display_label: Annotated[
        str,
        Field(
            max_length=25, description="Short display label for UI charts, truncated to max 3 words and 25 characters."
        ),
    ]
    visual_intent: Annotated[
        LaxVisualIntent, Field(description="Visual intent for SDUI rendering. Must not have a default fallback.")
    ]
    counter_quote: Annotated[
        str | None,
        Field(
            default=None,
            description=(
                "If you believe the exact_quotes are taken out of context, provide a SEPARATE "
                "verbatim quote from the source text that contradicts or contextualizes them. "
                "This counter-evidence MUST also be a physically contiguous substring. "
                "If you cannot find contradicting evidence, leave this as null."
            ),
        ),
    ]
    semantic_reasoning: Annotated[
        str,
        Field(
            description="Detailed reasoning for the evaluation. Must be in the Localized Target Language.",
        ),
    ]
    extensions: Annotated[
        dict[str, Any] | None,
        Field(
            description="Schema-less escape hatch for dynamic custom integrations.",
            default_factory=dict,
        ),
    ] = Field(default_factory=dict)
    contextual_override: Annotated[
        bool,
        Field(
            description=(
                "Set to true ONLY if evidence is implicitly valid despite lacking exact quote. "
                "If true, you MUST populate structural_location."
            ),
        ),
    ]
    structural_location: Annotated[
        str,
        Field(
            description=(
                "Exact structural location (e.g. 'page 3', 'paragraph 2'). Must be in the Localized "
                "Target Language. If contextual_override is False, you MUST output 'N/A'. "
                "If contextual_override is True, you MUST provide the concrete location."
            ),
        ),
    ]

    dlq_status: bool | None = None
    is_mcp_verified: bool = False
    mcp_source_reference: str | None = None

    @field_validator("exact_quotes", mode="before")
    @classmethod
    def _truncate_quotes(cls, v: Any) -> Any:
        if isinstance(v, list):
            max_len = _schema_max_quotes
            if len(v) > max_len:
                return v[:max_len]
        return v

    @field_validator("chart_display_label", mode="before")
    @classmethod
    def _truncate_chart_label(cls, v: Any) -> Any:
        if not isinstance(v, str):
            return v
        words = v.split()
        truncated = False
        if len(words) > 3:
            words = words[:3]
            truncated = True

        res = " ".join(words)
        if len(res) > 25:
            res = res[:22] + "..."
        elif truncated and not res.endswith("..."):
            if len(res) > 22:
                res = res[:22] + "..."
            else:
                res += "..."
        return res

    _null_hypothesis_blacklist: frozenset[str] = PrivateAttr(default_factory=frozenset)

    @model_validator(mode="after")
    def _inject_context(self, info: ValidationInfo) -> AtomEvaluationItemDTO:
        context = info.context or {}
        self._null_hypothesis_blacklist = context.get("null_hypothesis_blacklist", DEFAULT_NULL_HYPOTHESIS_BLACKLIST)
        return self

    @property
    def evidence_found(self) -> bool:
        """Prevent Phantom Booleans: Sanitize hallucinated nulls produced by LLMs.

        Returns:
            True if robust quote or extracted data exists, False otherwise.
        """
        if self.exact_quotes:
            for quote in self.exact_quotes:
                if quote.text and quote.text.strip().lower() not in self._null_hypothesis_blacklist:
                    return True
        for val in self.extracted_facts.values():
            if val is not None and val.strip().lower() not in self._null_hypothesis_blacklist:
                return True
        return False

    def calculate_rule_satisfied(self, inverse_evidence: bool, allow_contextual_override: bool = False) -> bool | str:
        """Deterministic judgment: Calculates rule_satisfied at the code level.

        Args:
            inverse_evidence: True if successful condition implies missing evidence.
            allow_contextual_override: True if explicit spatial contextual bridging is allowed.

        Returns:
            True if atom logic evaluates to satisfied, False if not, or 'DLQ' if corrupt.
        """
        if allow_contextual_override and self.contextual_override:
            return True

        if self.status:
            if self.status == "DLQ":
                return "DLQ"
            # Phase 1: CONTESTED bypasses inversion logic
            if self.status == "CONTESTED":
                return True
            evidence_found = self.status == "PASS"
            if inverse_evidence:
                return not evidence_found
            return evidence_found

        if inverse_evidence:
            return not self.evidence_found
        return self.evidence_found

    @model_validator(mode="before")
    @classmethod
    def _enforce_null_hypothesis_before(cls, data: Any, info: ValidationInfo) -> Any:
        if isinstance(data, dict):
            if data.get("contextual_override"):
                data["exact_quotes"] = []
                data["used_evidence_ids"] = []
        return data

    @model_validator(mode="after")
    def _enforce_zero_variance_protocols(self, info: ValidationInfo) -> AtomEvaluationItemDTO:
        """Validates spatial anchoring, Anti-Laziness enforcement, and quote integrity.

        Args:
            info: The validation info context provided by Pydantic V2 engine.

        Returns:
            The validated instance if it meets Zero-Variance mandates.

        Raises:
            ValueError: If lengths, strings or contextual fuzz ratios fail compliance checks.
        """
        if self.contextual_override:
            # Milestone 4: Spatial anchoring & Anti-Laziness enforcement
            reasoning = self.semantic_reasoning or ""
            if len(reasoning) < 50:
                raise ValueError("Contextual override requires semantic_reasoning to be at least 50 characters long.")

            if not self.structural_location or self.structural_location.strip().upper() == "N/A":
                raise ValueError(
                    "Contextual override requires an explicit structural_location reference "
                    "(e.g., 'page 3', 'paragraph 2')."
                )
        else:
            # Milestone 3: Check quote integrity
            if self.exact_quotes:
                max_len = _schema_max_quote_length
                for quote in self.exact_quotes:
                    if not quote.text:
                        continue
                    if len(quote.text) > max_len:
                        raise ValueError(
                            f"Quote too long ({len(quote.text)} chars > {max_len}). "
                            "Split into separate shorter quotes from different source locations."
                        )
        return self


class ReducedAtomDTO(V2CoreBase):
    """Reduced atom data for synthesis, containing only what is strictly necessary."""

    tda_id: str
    status: str
    reasoning: str | None = None
    source_quote: str | None = None
    extracted_data: dict[str, Any] | None = None


class LightweightMatrixDTO(V2CoreBase):
    """Token-compressed matrix payload for Synthesis Generation."""

    execution_id: str
    reduced_atoms: list[ReducedAtomDTO]
    global_metrics: dict[str, Any]
    raw_extensions: list[dict[str, Any]] = Field(default_factory=list)
