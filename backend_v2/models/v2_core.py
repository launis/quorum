"""V2 Core Models Facade.

Strangler Fig Facade re-exporting all V2 domain models and DTOs from their decomposed
canonical locations in domain/ and dtos/. Satisfies PEP 484 and provides 100% backward
compatibility across all existing callers.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from backend_v2.models.dtos.dag_models import CausalEdge
    from backend_v2.models.dtos.trace import DataStarvationEvent
    from backend_v2.models.view.sdui import AnySduiBlock

from backend_v2.models.core_base import (
    OPAQUE_STRIPE_ID_REGEX as OPAQUE_STRIPE_ID_REGEX,
)
from backend_v2.models.core_base import (
    I18nText as I18nText,
)
from backend_v2.models.core_base import (
    V2CoreBase as V2CoreBase,
)
from backend_v2.models.domain.execution import (
    EvaluatedMatrixContextDTO as EvaluatedMatrixContextDTO,
)
from backend_v2.models.domain.execution import (
    EvidenceRejectionRequest as EvidenceRejectionRequest,
)
from backend_v2.models.domain.execution import (
    ExecutionCreate as ExecutionCreate,
)
from backend_v2.models.domain.execution import (
    ExecutionRecord as ExecutionRecord,
)
from backend_v2.models.domain.execution import (
    ExecutionStep as ExecutionStep,
)
from backend_v2.models.domain.execution import (
    ExecutionStepState as ExecutionStepState,
)
from backend_v2.models.domain.execution import (
    ExecutionSummarySnapshot as ExecutionSummarySnapshot,
)
from backend_v2.models.domain.execution import (
    FrozenContext as FrozenContext,
)
from backend_v2.models.domain.execution import (
    JobAcceptedDTO as JobAcceptedDTO,
)
from backend_v2.models.domain.inputs import (
    WorkflowInputs as WorkflowInputs,
)
from backend_v2.models.domain.inputs import (
    WorkflowInputsIngress as WorkflowInputsIngress,
)
from backend_v2.models.domain.matrix import (
    AcceptanceCriterion as AcceptanceCriterion,
)
from backend_v2.models.domain.matrix import (
    AntiPattern as AntiPattern,
)
from backend_v2.models.domain.matrix import (
    ContrastivePairDTO as ContrastivePairDTO,
)
from backend_v2.models.domain.matrix import (
    MatrixClaim as MatrixClaim,
)
from backend_v2.models.domain.matrix import (
    MatrixRow as MatrixRow,
)
from backend_v2.models.domain.matrix import (
    MatrixScale as MatrixScale,
)
from backend_v2.models.domain.matrix import (
    TDAAssertion as TDAAssertion,
)
from backend_v2.models.domain.matrix import (
    TheoryGrounding as TheoryGrounding,
)
from backend_v2.models.domain.matrix import (
    _coerce_to_tuple as _coerce_to_tuple,
)
from backend_v2.models.domain.output_profile import (
    OutputProfile as OutputProfile,
)
from backend_v2.models.domain.report_artifact import (
    ReportArtifact as ReportArtifact,
)
from backend_v2.models.domain.step import (
    ALLOWED_INPUT_MODES as ALLOWED_INPUT_MODES,
)
from backend_v2.models.domain.step import (
    ExpectedInput as ExpectedInput,
)
from backend_v2.models.domain.step import (
    QuestionnaireItem as QuestionnaireItem,
)
from backend_v2.models.domain.step import (
    Role as Role,
)
from backend_v2.models.domain.step import (
    Step as Step,
)
from backend_v2.models.domain.step import (
    StepRule as StepRule,
)
from backend_v2.models.domain.synthesis import (
    BaseMatrixXAI as BaseMatrixXAI,
)
from backend_v2.models.domain.synthesis import (
    BaseTDAExtraction as BaseTDAExtraction,
)
from backend_v2.models.domain.synthesis import (
    DistilledEvaluation as DistilledEvaluation,
)
from backend_v2.models.domain.synthesis import (
    MatrixSynthesisGroup as MatrixSynthesisGroup,
)
from backend_v2.models.domain.synthesis import (
    RenderedSynthesisCache as RenderedSynthesisCache,
)
from backend_v2.models.domain.synthesis import (
    SynthesisMetadataDTO as SynthesisMetadataDTO,
)
from backend_v2.models.domain.synthesis import (
    SynthesisStepDataDTO as SynthesisStepDataDTO,
)
from backend_v2.models.domain.system_config import (
    AllowedMCPTool as AllowedMCPTool,
)
from backend_v2.models.domain.system_config import (
    ChatHistoryDTO as ChatHistoryDTO,
)
from backend_v2.models.domain.system_config import (
    ChatMessageDTO as ChatMessageDTO,
)
from backend_v2.models.domain.system_config import (
    DataDictionaryField as DataDictionaryField,
)
from backend_v2.models.domain.system_config import (
    MCPAuditTrace as MCPAuditTrace,
)
from backend_v2.models.domain.system_config import (
    ModelProfile as ModelProfile,
)
from backend_v2.models.domain.system_config import (
    ProviderExtraParamsDTO as ProviderExtraParamsDTO,
)
from backend_v2.models.domain.system_config import (
    SystemConfigMCPGateways as SystemConfigMCPGateways,
)
from backend_v2.models.domain.system_config import (
    SystemConfigModelRegistry as SystemConfigModelRegistry,
)
from backend_v2.models.domain.workflow import (
    Workflow as Workflow,
)
from backend_v2.models.dtos.atom_result import (
    AtomResultDTO as AtomResultDTO,
)
from backend_v2.models.dtos.atom_result import (
    ErrorDetailsDTO as ErrorDetailsDTO,
)
from backend_v2.models.dtos.atom_result import (
    ExecutionMetricsDTO as ExecutionMetricsDTO,
)
from backend_v2.models.dtos.atom_result import (
    ExtensionMetricsDTO as ExtensionMetricsDTO,
)
from backend_v2.models.dtos.atom_result import (
    ExtractedValueDTO as ExtractedValueDTO,
)
from backend_v2.models.dtos.atom_result import (
    HydratedAtomDTO as HydratedAtomDTO,
)
from backend_v2.models.dtos.matrix_scorecard import (
    HumanOverrideDTO as HumanOverrideDTO,
)
from backend_v2.models.dtos.matrix_scorecard import (
    HumanOverrideRequest as HumanOverrideRequest,
)
from backend_v2.models.dtos.matrix_scorecard import (
    MatrixScorecardRowDTO as MatrixScorecardRowDTO,
)
from backend_v2.models.dtos.matrix_scorecard import (
    ScorecardAtomDTO as ScorecardAtomDTO,
)
from backend_v2.models.dtos.matrix_scorecard import (
    TDADlq as TDADlq,
)
from backend_v2.models.dtos.matrix_scorecard import (
    TDAEvaluated as TDAEvaluated,
)
from backend_v2.models.dtos.matrix_scorecard import (
    TDAPending as TDAPending,
)
from backend_v2.models.dtos.matrix_scorecard import (
    TDAStateUnion as TDAStateUnion,
)
from backend_v2.models.dtos.quote_evidence import LLMExtractedQuote as LLMExtractedQuote
from backend_v2.models.dtos.report_data import (
    ReportDataDTO as ReportDataDTO,
)
from backend_v2.models.dtos.synthesis import XaiHighlightItem as XaiHighlightItem
from backend_v2.models.enums import (
    BlockDataType as BlockDataType,
)
from backend_v2.models.enums import (
    CognitiveTier as CognitiveTier,
)
from backend_v2.models.enums import (
    ComponentType as ComponentType,
)
from backend_v2.models.enums import (
    DisplayScale as DisplayScale,
)
from backend_v2.models.enums import (
    ExecutionStatus as ExecutionStatus,
)
from backend_v2.models.enums import (
    LaxCognitiveTier as LaxCognitiveTier,
)
from backend_v2.models.enums import (
    LaxComponentType as LaxComponentType,
)
from backend_v2.models.enums import (
    LaxDisplayScale as LaxDisplayScale,
)
from backend_v2.models.enums import (
    LaxExecutionStatus as LaxExecutionStatus,
)
from backend_v2.models.enums import (
    LaxHistoricalContextMode as LaxHistoricalContextMode,
)
from backend_v2.models.enums import (
    LaxLLMProvider as LaxLLMProvider,
)
from backend_v2.models.enums import (
    LaxPresetView as LaxPresetView,
)
from backend_v2.models.enums import (
    LaxSDUIComponentType as LaxSDUIComponentType,
)
from backend_v2.models.enums import (
    LaxSourcesDisplayMode as LaxSourcesDisplayMode,
)
from backend_v2.models.enums import (
    LaxStepType as LaxStepType,
)
from backend_v2.models.enums import (
    LaxSystemLocale as LaxSystemLocale,
)
from backend_v2.models.enums import (
    LaxTargetBlockType as LaxTargetBlockType,
)
from backend_v2.models.enums import (
    LaxXaiExtensionType as LaxXaiExtensionType,
)
from backend_v2.models.enums import (
    LLMProvider as LLMProvider,
)
from backend_v2.models.enums import (
    PresetView as PresetView,
)
from backend_v2.models.enums import (
    SourcesDisplayMode as SourcesDisplayMode,
)
from backend_v2.models.enums import (
    StepType as StepType,
)
from backend_v2.models.enums import (
    TargetBlockType as TargetBlockType,
)
from backend_v2.models.enums import (
    TargetSpeaker as TargetSpeaker,
)
from backend_v2.models.enums import (
    XaiExtensionType as XaiExtensionType,
)
from backend_v2.models.execution_core import (
    ExecutionCoreFields as ExecutionCoreFields,
)
from backend_v2.models.execution_core import (
    ExecutionMetadata as ExecutionMetadata,
)

__all__ = [
    "ALLOWED_INPUT_MODES",
    "AcceptanceCriterion",
    "AllowedMCPTool",
    "AntiPattern",
    "AtomResultDTO",
    "BaseMatrixXAI",
    "BaseTDAExtraction",
    "BlockDataType",
    "ChatMessageDTO",
    "ChatHistoryDTO",
    "CognitiveTier",
    "ComponentType",
    "ContrastivePairDTO",
    "DataDictionaryField",
    "DataStarvationEvent",
    "ErrorDetailsDTO",
    "EvaluatedMatrixContextDTO",
    "EvidenceRejectionRequest",
    "ExecutionCoreFields",
    "ExecutionCreate",
    "ExecutionMetricsDTO",
    "ExecutionRecord",
    "ExecutionStatus",
    "ExecutionStep",
    "ExecutionStepState",
    "ExecutionSummarySnapshot",
    "ExpectedInput",
    "ExtensionMetricsDTO",
    "ExtractedValueDTO",
    "FrozenContext",
    "HumanOverrideDTO",
    "HumanOverrideRequest",
    "HydratedAtomDTO",
    "I18nText",
    "JobAcceptedDTO",
    "LLMProvider",
    "MCPAuditTrace",
    "MatrixClaim",
    "MatrixRow",
    "MatrixScale",
    "MatrixScorecardRowDTO",
    "MatrixSynthesisGroup",
    "ModelProfile",
    "OutputProfile",
    "ProviderExtraParamsDTO",
    "QuestionnaireItem",
    "RenderedSynthesisCache",
    "ReportArtifact",
    "ReportDataDTO",
    "Role",
    "ScorecardAtomDTO",
    "Step",
    "StepRule",
    "SystemConfigMCPGateways",
    "SystemConfigModelRegistry",
    "TDAAssertion",
    "TheoryGrounding",
    "Workflow",
    "WorkflowInputs",
    "XaiHighlightItem",
]

WorkflowSchemaResponse = dict[str, Any]

# Runtime Pydantic Model Rebuilds for forward references
import backend_v2.models.view.sdui as sdui_mod
from backend_v2.models.dtos.base import DataStarvationEvent
from backend_v2.models.dtos.dag_models import CausalEdge
from backend_v2.models.view.sdui import AnySduiBlock

_sdui_localns = {
    "MatrixScorecardRowDTO": MatrixScorecardRowDTO,
    "LaxXaiExtensionType": LaxXaiExtensionType,
    "AnySduiBlock": AnySduiBlock,
    "MCPAuditTrace": MCPAuditTrace,
}
sdui_mod.SduiRadarChartBlock.model_rebuild(_types_namespace=_sdui_localns)
sdui_mod.SduiScatterPlotBlock.model_rebuild(_types_namespace=_sdui_localns)
sdui_mod.SduiQuadrantMatrixBlock.model_rebuild(_types_namespace=_sdui_localns)
sdui_mod.SduiMatrixTableBlock.model_rebuild(_types_namespace=_sdui_localns)
sdui_mod.SduiMetrics1DBlock.model_rebuild(_types_namespace=_sdui_localns)
sdui_mod.SduiGridBlock.model_rebuild(_types_namespace=_sdui_localns)

RenderedSynthesisCache.model_rebuild(
    _types_namespace={
        "DataStarvationEvent": DataStarvationEvent,
        "AnySduiBlock": AnySduiBlock,
    }
)
ReportDataDTO.model_rebuild(
    _types_namespace={
        "AnySduiBlock": AnySduiBlock,
    }
)
MatrixScorecardRowDTO.model_rebuild(
    _types_namespace={
        "AnySduiBlock": AnySduiBlock,
        "MCPAuditTrace": MCPAuditTrace,
    }
)
ExecutionCreate.model_rebuild()
TDAAssertion.model_rebuild(_types_namespace={"CausalEdge": CausalEdge})

import backend_v2.models.state  # noqa: F401, E402
