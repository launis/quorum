/// Enums for Client App V2.
/// Strict definition of allowed types to enforce the No-String Mandate.

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
