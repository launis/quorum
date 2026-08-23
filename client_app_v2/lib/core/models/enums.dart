/// Enums for Client App V2.
/// Strict definition of allowed types to enforce the No-String Mandate.

import 'package:freezed_annotation/freezed_annotation.dart';

/// Global concurrency limits for DAG Execution to prevent API Rate Limits.
/// Mirrors the backend SystemConcurrency enum.
enum SystemConcurrency {
  maxConcurrentWorkflows(1),
  maxConcurrentLlmSteps(2),
  llmMaxRetries(10),
  llmDefaultTimeoutSeconds(120),

  // Frontend specific overrides
  pollingMaxAttempts(300), // 10 minutes max for Riverpod report polling
  dashboardRefreshRateSeconds(10),
  sseTimeoutSeconds(600),
  rehydrationDelayMs(500);

  final int value;
  const SystemConcurrency(this.value);
}

/// Supported XAI Output Extensions for global visibility.
enum XaiExtensionType {
  @JsonValue('citation')
  citation,
  @JsonValue('justification')
  justification,
  @JsonValue('falsification')
  falsification,
  @JsonValue('theory_link')
  theoryLink,
  @JsonValue('risk_flag')
  riskFlag,
  @JsonValue('coaching')
  coaching,
  @JsonValue('missing_context')
  missingContext,
  @JsonValue('remediation_steps')
  remediationSteps,
  @JsonValue('emotional_sentiment')
  emotionalSentiment,
  @JsonValue('confidence')
  confidence,
  @JsonValue('source_id')
  sourceId,
  @JsonValue('contextual_override')
  contextualOverride,
  @JsonValue('variance_validation')
  varianceValidation,
  @JsonValue('authenticity_evaluation')
  authenticityEvaluation,
}

/// Static UI Renderer presets for report blocks.
/// STRICT PARITY MANDATE: Must precisely match backend Pydantic Literals.
enum PresetView {
  @JsonValue('1d_metrics')
  metrics1d,
  @JsonValue('2d_compare')
  compare2d,

  @JsonValue('3d_matrix')
  matrix3d,
  @JsonValue('text_only')
  textOnly,
  @JsonValue('default')
  defaultView,
  @JsonValue('matrix_summary')
  matrixSummary,
}

/// Execution Routing Modes mapping
/// STRICT PARITY MANDATE: Must match backend Pydantic string equivalents.
enum RoutingMode {
  @JsonValue('standard')
  standard,
  @JsonValue('dynamic_routing')
  dynamicRouting,
  @JsonValue('parallel_routing')
  parallelRouting,
}

/// Strictness evaluation evidence type
@JsonEnum()
enum EvidenceType {
  @JsonValue('EXPLICIT_QUOTE')
  explicitQuote,
  @JsonValue('IMPLIED_INTENT')
  impliedIntent,
  @JsonValue('NO_EVIDENCE')
  noEvidence,
}

/// Multi-Engine Scoring Strategies
@JsonEnum()
enum ScoringStrategy {
  @JsonValue('WATERFALL')
  waterfall,
  @JsonValue('AVERAGE')
  average,
  @JsonValue('WEIGHTED_AVERAGE')
  weightedAverage,
  @JsonValue('PURE_MATH')
  pureMath,
}

/// Strictness Level Enums
@JsonEnum()
enum StrictnessLevel {
  @JsonValue(0)
  fullFlexibility,
  @JsonValue(15)
  lenient,
  @JsonValue(50)
  balanced,
  @JsonValue(85)
  strict,
  @JsonValue(100)
  absolute,
}

extension StrictnessLevelExtension on StrictnessLevel {
  int get value {
    switch (this) {
      case StrictnessLevel.fullFlexibility:
        return 0;
      case StrictnessLevel.lenient:
        return 15;
      case StrictnessLevel.balanced:
        return 50;
      case StrictnessLevel.strict:
        return 85;
      case StrictnessLevel.absolute:
        return 100;
    }
  }

  static StrictnessLevel fromInt(int value) {
    return StrictnessLevel.values.firstWhere(
      (e) => e.value == value,
      orElse: () => StrictnessLevel.balanced,
    );
  }
}

/// Aggregation constraint for TDA Assertions
@JsonEnum()
enum AggregationMode {
  @JsonValue('EXISTS')
  exists,
  @JsonValue('ALL_MUST_COMPLY')
  allMustComply,
}

/// Decoupled evaluation track for TDA Assertions: extractive logic vs cognitive judgement.
@JsonEnum()
enum EvaluationTrack {
  @JsonValue('EXTRACTIVE_SENSOR')
  extractiveSensor,
  @JsonValue('COGNITIVE_JUDGEMENT')
  cognitiveJudgement,
}

/// Allowed groupings of PromptBlockCategory values for different dropdown selectors.
class PromptBlockCategoryGroups {
  /// Categories allowed for Role Blocks.
  static final List<String> roleCategories = ['agent_role'];

  /// Categories allowed for Execution Persona Blocks.
  static final List<String> personaCategories = ['execution_persona'];

  /// Categories allowed for Protocol Blocks.
  static final List<String> protocolCategories = ['protocol'];

  /// Categories allowed for Criteria Blocks.
  static final List<String> criteriaCategories = [
    'matrix',
    'system_rule',
    'runtime_variables',
    'task_definition',
    'protocol',
    'criteria',
    'text',
  ];
}

extension XaiExtensionTypeValue on XaiExtensionType {
  String get backendValue {
    switch (this) {
      case XaiExtensionType.citation:
        return 'citation';
      case XaiExtensionType.justification:
        return 'justification';
      case XaiExtensionType.falsification:
        return 'falsification';
      case XaiExtensionType.theoryLink:
        return 'theory_link';
      case XaiExtensionType.riskFlag:
        return 'risk_flag';
      case XaiExtensionType.coaching:
        return 'coaching';
      case XaiExtensionType.missingContext:
        return 'missing_context';
      case XaiExtensionType.remediationSteps:
        return 'remediation_steps';
      case XaiExtensionType.emotionalSentiment:
        return 'emotional_sentiment';
      case XaiExtensionType.confidence:
        return 'confidence';
      case XaiExtensionType.sourceId:
        return 'source_id';
      case XaiExtensionType.contextualOverride:
        return 'contextual_override';
      case XaiExtensionType.varianceValidation:
        return 'variance_validation';
      case XaiExtensionType.authenticityEvaluation:
        return 'authenticity_evaluation';
    }
  }
}

/// SDUI Block Types supported by the frontend.
@JsonEnum()
enum SduiBlockType {
  @JsonValue('hero_insight')
  heroInsight,
  @JsonValue('paragraph')
  paragraph,
  @JsonValue('bullet_list')
  bulletList,
  @JsonValue('alert_box')
  alertBox,
  @JsonValue('markdown')
  markdown,
  @JsonValue('warning_card')
  warningCard,
  @JsonValue('quote_card')
  quoteCard,
  @JsonValue('n_a_card')
  nACard,
  @JsonValue('grid')
  grid,
  @JsonValue('accordion')
  accordion,

  @JsonValue('3d_matrix')
  matrix3d,
  @JsonValue('audit_trail')
  auditTrail,
  @JsonValue('metadata')
  metadata,
  @JsonValue('score_card')
  scoreCard,
  @JsonValue('2d_compare')
  compare2d,
  @JsonValue('matrix_summary')
  matrixSummary,
  @JsonValue('1d_metrics')
  metrics1d,
}

/// UI intent mapping for SDUI visual rendering.
/// STRICT PARITY MANDATE: Must precisely match backend VisualIntent.
@JsonEnum()
enum VisualIntent {
  @JsonValue('success')
  success,
  @JsonValue('warning')
  warning,
  @JsonValue('error')
  error,
  @JsonValue('critical_override')
  criticalOverride,
  @JsonValue('info')
  info,
  @JsonValue('NEUTRAL')
  neutral,
}

@JsonEnum()
enum AlertSeverity {
  @JsonValue('info')
  info,
  @JsonValue('warning')
  warning,
  @JsonValue('critical_override')
  criticalOverride,
  @JsonValue('success')
  success,
  @JsonValue('error')
  error,
}

@JsonEnum()
enum UiVariant {
  @JsonValue('default')
  defaultVariant,
  @JsonValue('success')
  success,
  @JsonValue('warning')
  warning,
  @JsonValue('error')
  error,
  @JsonValue('neutral')
  neutral,
}

/// Execution lifecycle status.
@JsonEnum()
enum ExecutionStatus {
  @JsonValue('PASSED')
  passed,
  @JsonValue('FAILED')
  failed,
  @JsonValue('N_A')
  nA,
  @JsonValue('SYSTEM_ERROR')
  systemError,
  @JsonValue('BLOCKED')
  blocked,
  @JsonValue('PENDING')
  pending,
  @JsonValue('RUNNING')
  running,
  @JsonValue('QUEUED')
  queued,
}

/// SDUI Component types mapped from backend.
@JsonEnum()
enum SDUIComponentType {
  @JsonValue('boolean_card')
  booleanCard,
  @JsonValue('extracted_value_card')
  extractedValueCard,
  @JsonValue('error_card')
  errorCard,
  @JsonValue('n_a_card')
  nACard,
}

/// Text delivery mode for output layouts.
@JsonEnum()
enum TextDeliveryMode {
  @JsonValue('full')
  full,
  @JsonValue('titles_only')
  titlesOnly,
  @JsonValue('none')
  none,
}

/// Historical context mode for synthesis.
@JsonEnum()
enum HistoricalContextMode {
  @JsonValue('DISABLED')
  disabled,
  @JsonValue('SLIDING_WINDOW_3')
  slidingWindow3,
}

/// Display scale configuration for matrix score rendering.
@JsonEnum()
enum DisplayScale {
  @JsonValue('original')
  original,
  @JsonValue('custom')
  custom,
  @JsonValue('normalized_100')
  normalized100,
}

/// Global systemic UI constraints and bounds.
enum SystemUiConstraints {
  maxExtensionItemsSliderMin(1),
  maxExtensionItemsSliderMax(20),
  maxExtensionItemsAbsoluteMax(100),
  maxExtensionItemsDefault(3),
  tdaConceptMinLength(10);

  const SystemUiConstraints(this.value);
  final int value;
}

/// Explicit layout hydration target blocks for SDUI.
@JsonEnum()
enum TargetBlockType {
  @JsonValue('global_score_block')
  globalScoreBlock,
  @JsonValue('penalties_block')
  penaltiesBlock,
  @JsonValue('audit_trail_block')
  auditTrailBlock,
  @JsonValue('jargon_ratio_block')
  jargonRatioBlock,
  @JsonValue('printable_sources_block')
  printableSourcesBlock,
  @JsonValue('grouped_extensions_block')
  groupedExtensionsBlock,
  @JsonValue('executive_summary_block')
  executiveSummaryBlock,
  @JsonValue('metadata_block')
  metadataBlock,
  @JsonValue('synthesis_text_block')
  synthesisTextBlock,
  @JsonValue('matrix_graphs_block')
  matrixGraphsBlock,
  @JsonValue('matrix_summary_table_block')
  matrixSummaryTableBlock,
  @JsonValue('variance_validation_block')
  varianceValidationBlock,
  @JsonValue('authenticity_evaluation_block')
  authenticityEvaluationBlock,
}
