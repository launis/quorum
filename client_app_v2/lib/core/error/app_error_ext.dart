import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:dio/dio.dart';

extension AppExceptionX on AppException {
  /// Converts [AppException] to a localized user-facing actionable hint.
  ///
  /// **NEVER show raw backend messages to users.**
  /// Always map error_code to localized strings.
  String toLocalizedHint(AppLocalizations l10n) {
    if (this.errorCode == 'NETWORK_FATAL') return l10n.errorNetwork;
    if (this.errorCode == 'UNAUTHORIZED' || this.status == 401) {
      return l10n.errorUnauthorized;
    }
    if (this.errorCode == 'CANCELLED') return l10n.cancel;
    if (this.errorCode == 'TIMEOUT' && this.detail.isNotEmpty)
      return this.detail;

    // Map specific structured payloads or error codes
    final locCode = _localizeErrorCode(this.errorCode, l10n);
    if (locCode != l10n.errorUnknown) {
      // For validation errors, the backend provides highly specific 'detail' strings (e.g. which fields failed)
      if (this.errorCode == 'VALIDATION_FAILED' &&
          this.detail.isNotEmpty &&
          this.detail != 'Unknown error') {
        return '$locCode\n\n${this.detail}';
      }
      return locCode;
    }

    // Fallback status code mapping
    if (this.status == 404) {
      return '${l10n.errorNotFound}\n\n${l10n.actionHintContactSupport}';
    }
    if (this.status >= 500) return l10n.errorServer;

    return l10n.errorUnknown;
  }

  /// Extracts a localized hint from a generic error object (e.g., [DioException] or [AppException]).
  ///
  /// The [ErrorInterceptor] usually wraps [AppException] inside [DioException.error].
  static String extractLocalizedHint(Object? error, AppLocalizations l10n) {
    if (error == null) return l10n.errorUnknown;

    if (error is AppException) {
      return error.toLocalizedHint(l10n);
    }

    if (error is DioException) {
      if (error.error is AppException) {
        return (error.error as AppException).toLocalizedHint(l10n);
      }
      // Exhaustive mapping for remaining DioExceptionTypes if not wrapped by interceptor
      return switch (error.type) {
        DioExceptionType.connectionTimeout ||
        DioExceptionType.receiveTimeout ||
        DioExceptionType.sendTimeout ||
        DioExceptionType.connectionError ||
        DioExceptionType.badCertificate =>
          l10n.errorNetwork,
        DioExceptionType.cancel => l10n.cancel,
        DioExceptionType.badResponse => l10n.errorServer,
        DioExceptionType.unknown => l10n.errorUnknown,
      };
    }

    return l10n.errorUnknown;
  }

  /// Maps backend error_code to localized string.
  ///
  /// Add new error codes here as they are defined in the backend.
  static String _localizeErrorCode(String errorCode, AppLocalizations l10n) {
    return switch (errorCode) {
      // General
      'INTERNAL_SERVER_ERROR' =>
        '${l10n.errorServer}\n\n${l10n.actionHintTryAgainLater}',
      'UNKNOWN_ERROR' => l10n.errorUnknown,

      // Workflow errors
      'WORKFLOW_NOT_FOUND' => l10n.errorNotFound,
      'WORKFLOW_EXECUTION_FAILED' => l10n.errorServer,
      'MISSING_WORKFLOW_ID' => l10n.fieldRequired,
      'WORKFLOW_CLONE_FAILED' => l10n.workflowCloneErrorMissingDep,

      // Auth errors
      'AUTH_TOKEN_EXPIRED' => l10n.errorUnauthorized,
      'PERMISSION_DENIED' => l10n.errorUnauthorized,
      'AUTHENTICATION_FAILED' =>
        '${l10n.errAuthenticationFailed}\n\n${l10n.actionHintLoginAgain}',

      // Validation errors
      'INVALID_JSON_PAYLOAD' => l10n.errorValidation,
      'UNSUPPORTED_CONTENT_TYPE' => l10n.errorValidation,
      'VALIDATION_FAILED' =>
        '${l10n.errValidationFailed}\n\n${l10n.actionHintCheckInput}',

      // Knowledge Base
      'KNOWLEDGE_INGESTION_FAILED' => l10n.errorKnowledgeIngestionFailed,
      'KNOWLEDGE_RESET_FAILED' => l10n.errorKnowledgeResetFailed,
      'KNOWLEDGE_RETRIEVAL_FAILED' => l10n.errorKnowledgeRetrievalFailed,
      'KNOWLEDGE_NOT_INGESTED' =>
        '${l10n.errKnowledgeNotIngested}\n\n${l10n.actionHintRunIngestion}',

      // Workflow & Resource Protection
      'RESOURCE_IN_USE' => l10n.errorResourceInUse,

      // Operational
      'SERVICE_UNAVAILABLE' =>
        '${l10n.errServiceUnavailable}\n\n${l10n.actionHintTryAgainLater}',
      'AGENT_EXECUTION_CRITICAL' =>
        '${l10n.errAgentExecutionCritical}\n\n${l10n.actionHintContactSupport}',
      'TOOL_EXECUTION_FAILED' =>
        '${l10n.toolExecutionFailed}\n\n${l10n.actionHintToolFailed}',
      'URL_INVALID' => '${l10n.errorValidation}\n\n${l10n.actionHintCheckUrl}',
      'FETCH_FAILED' =>
        '${l10n.errorNetwork}\n\n${l10n.actionHintCheckConnection}',
      'DATA_CORRUPTION' =>
        '${l10n.errDataCorruptionDesc}\n\n${l10n.actionHintRunAgain}',

      _ => l10n.errorUnknown,
    };
  }
}
