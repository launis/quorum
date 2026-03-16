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
    
    // Map specific structured payloads or error codes
    final locCode = _localizeErrorCode(this.errorCode, l10n);
    if (locCode != l10n.errorUnknown) {
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
      // Fallbacks if not wrapped correctly
      if (error.type == DioExceptionType.connectionTimeout || 
          error.type == DioExceptionType.connectionError) {
        return l10n.errorNetwork;
      }
      return l10n.errorUnknown; 
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
      'URL_INVALID' => '${l10n.errorValidation}\n\n${l10n.actionHintCheckUrl}',
      'FETCH_FAILED' =>
        '${l10n.errorNetwork}\n\n${l10n.actionHintCheckConnection}',

      _ => l10n.errorUnknown,
    };
  }
}

