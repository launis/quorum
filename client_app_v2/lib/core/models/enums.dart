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
  pollingMaxAttempts(300); // 10 minutes max for Riverpod report polling

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
}

/// Static UI Renderer presets for report blocks.
/// STRICT PARITY MANDATE: Must precisely match backend Pydantic Literals.
enum PresetView {
  @JsonValue('1d_metrics')
  metrics1d,
  @JsonValue('2d_compare')
  compare2d,
  @JsonValue('3d_complex')
  complex3d,
  @JsonValue('3d_matrix')
  matrix3d,
  @JsonValue('text_only')
  textOnly,
  @JsonValue('default')
  defaultView,
}

/// Execution Routing Modes mapping (Epic 35)
/// STRICT PARITY MANDATE: Must match backend Pydantic string equivalents.
enum RoutingMode {
  @JsonValue('standard')
  standard,
  @JsonValue('dynamic_routing')
  dynamicRouting,
  @JsonValue('parallel_routing')
  parallelRouting,
}

/// Epic 42: Strictness evaluation evidence type
@JsonEnum()
enum EvidenceType {
  @JsonValue('EXPLICIT_QUOTE')
  explicitQuote,
  @JsonValue('IMPLIED_INTENT')
  impliedIntent,
  @JsonValue('NO_EVIDENCE')
  noEvidence,
}

/// Epic 43: Multi-Engine Scoring Strategies
@JsonEnum()
enum ScoringStrategy {
  @JsonValue('WATERFALL')
  waterfall,
  @JsonValue('DAMPENING')
  dampening,
  @JsonValue('AVERAGE')
  average,
  @JsonValue('WEIGHTED_AVERAGE')
  weightedAverage,
}

/// Epic 46: Strictness Level Enums
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

/// Epic 48: Aggregation constraint for TDA Assertions
@JsonEnum()
enum AggregationMode {
  @JsonValue('EXISTS')
  exists,
  @JsonValue('ALL_MUST_COMPLY')
  allMustComply,
}

/// Epic 55: Execution Personas
@JsonEnum()
enum ExecutionPersona {
  @JsonValue('DETERMINISTIC_PARSER')
  deterministicParser,
  @JsonValue('GENERATIVE_ASSISTANT')
  generativeAssistant,
  @JsonValue('XAI_REPORTER')
  xaiReporter,
  @JsonValue('COACH')
  coach,
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

  /// Categories allowed for Protocol Blocks.
  static final List<String> protocolCategories = ['instruction', 'system_rule'];

  /// Categories allowed for Criteria Blocks.
  static final List<String> criteriaCategories = [
    'matrix',
    'system_rule',
    'runtime_variables',
    'task_definition',
    'instruction',
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
    }
  }
}
