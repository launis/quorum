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
