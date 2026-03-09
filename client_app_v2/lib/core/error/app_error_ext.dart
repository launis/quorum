import 'package:client_app/core/error/app_error.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

extension AppErrorExt on AppError {
  /// Converts [AppError] to a localized user-facing message.
  ///
  /// **NEVER show raw backend messages to users.**
  /// Always map error_code to localized strings.
  String message(AppLocalizations l10n) {
    final err = this;
    if (err is UnknownAppError) return l10n.errorUnknown;
    if (err is NetworkAppError) return l10n.errorNetwork;
    if (err is ServerAppError) return l10n.errorServer;
    if (err is UnauthorizedAppError) return l10n.errorUnauthorized;
    if (err is NotFoundAppError) return l10n.errorNotFound;
    if (err is CancelledAppError) return l10n.cancel;
    if (err is ValidationAppError) {
      switch (err.reason) {
        case ValidationErrorReason.emptyInput:
          return l10n.errorValidationEmpty;
        case ValidationErrorReason.invalidEmail:
          return l10n.fieldRequired;
        case ValidationErrorReason.demoteLastAdmin:
          return l10n.demoteLastAdminError;
        default:
          return l10n.errorValidation;
      }
    }
    if (err is ValidationMissingAppError)
      return l10n.errorValidationMissing(err.fields.join(', '));
    if (err is ApiAppError) return _localizeErrorCode(err.errorCode, l10n);
    return l10n.errorUnknown;
  }

  /// Maps backend error_code to localized string.
  ///
  /// Add new error codes here as they are defined in the backend.
  static String _localizeErrorCode(String errorCode, AppLocalizations l10n) {
    return switch (errorCode) {
      // Workflow errors
      'WORKFLOW_NOT_FOUND' => l10n.errorNotFound,
      'WORKFLOW_EXECUTION_FAILED' => l10n.errorServer,
      'MISSING_WORKFLOW_ID' => l10n.fieldRequired,

      // Auth errors
      'AUTH_TOKEN_EXPIRED' => l10n.errorUnauthorized,
      'PERMISSION_DENIED' => l10n.errorUnauthorized,

      // Validation errors
      'INVALID_JSON_PAYLOAD' => l10n.errorValidation,
      'UNSUPPORTED_CONTENT_TYPE' => l10n.errorValidation,

      // Knowledge Base
      'KNOWLEDGE_INGESTION_FAILED' => l10n.errorKnowledgeIngestionFailed,
      'KNOWLEDGE_RESET_FAILED' => l10n.errorKnowledgeResetFailed,
      'KNOWLEDGE_RETRIEVAL_FAILED' => l10n.errorKnowledgeRetrievalFailed,

      // New Standardized Error Codes (Feb 16)
      'VALIDATION_FAILED' => l10n.errValidationFailed,
      'AUTHENTICATION_FAILED' => l10n.errAuthenticationFailed,
      'SERVICE_UNAVAILABLE' => l10n.errServiceUnavailable,
      'AGENT_EXECUTION_CRITICAL' => l10n.errAgentExecutionCritical,
      'KNOWLEDGE_NOT_INGESTED' => l10n.errKnowledgeNotIngested,

      _ => l10n.errorUnknown,
    };
  }
}
