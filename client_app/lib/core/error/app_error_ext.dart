import 'package:client_app/core/error/app_error.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

extension AppErrorExt on AppError {
  /// Converts [AppError] to a localized user-facing message.
  ///
  /// **NEVER show raw backend messages to users.**
  /// Always map error_code to localized strings.
  String message(AppLocalizations l10n) {
    return when(
      unknown: (err, stack) => l10n.errorUnknown,
      network: (err) => l10n.errorNetwork,
      server: (msg, code) => l10n.errorServer,
      unauthorized: () => l10n.errorUnauthorized,
      notFound: (msg) => l10n.errorNotFound,
      validation: (reason) {
        switch (reason) {
          case ValidationErrorReason.emptyInput:
            return l10n.errorValidationEmpty;
          case ValidationErrorReason.invalidEmail:
            return l10n.fieldRequired;
          case ValidationErrorReason.demoteLastAdmin:
            return l10n.demoteLastAdminError;
          default:
            return l10n.errorValidation;
        }
      },
      validationMissing:
          (fields) => l10n.errorValidationMissing(fields.join(', ')),
      cancelled: () => l10n.cancel,
      // RFC 7807 API errors - map error_code to localized strings
      api: (errorCode, detail, status, instance) {
        return _localizeErrorCode(errorCode, l10n);
      },
    );
  }

  /// Maps backend error_code to localized string.
  ///
  /// Add new error codes here as they are defined in the backend.
  static String _localizeErrorCode(String errorCode, AppLocalizations l10n) {
    return switch (errorCode) {
      // Execution errors
      'EXECUTION_NOT_FOUND' => l10n.errorNotFound,
      'EXECUTION_FETCH_FAILED' => l10n.errorServer,

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
      'INTERNAL_SERVER_ERROR' => l10n.errInternalServerError,
      'RESOURCE_NOT_FOUND' => l10n.errResourceNotFound,
      'AUTHENTICATION_FAILED' => l10n.errAuthenticationFailed,
      'PERMISSION_DENIED' => l10n.errPermissionDenied,
      'SERVICE_UNAVAILABLE' => l10n.errServiceUnavailable,
      'AGENT_EXECUTION_CRITICAL' => l10n.errAgentExecutionCritical,
      'WORKFLOW_EXECUTION_FAILED' => l10n.errWorkflowExecutionFailed,
      'KNOWLEDGE_NOT_INGESTED' => l10n.errKnowledgeNotIngested,

      _ => l10n.errorUnknown,
    };
  }
}
