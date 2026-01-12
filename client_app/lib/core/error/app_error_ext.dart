import 'package:client_app/core/error/app_error.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

extension AppErrorExt on AppError {
  String message(AppLocalizations l10n) {
    return when(
      unknown: (err, stack) => l10n.errorUnknown,
      network: (err) => l10n.errorNetwork,
      server: (msg, code) => msg ?? l10n.errorServer,
      unauthorized: () => l10n.errorUnauthorized,
      notFound: (msg) => l10n.errorNotFound,
      validation: (reason) {
        switch (reason) {
          case ValidationErrorReason.emptyInput:
            return l10n.errorValidationEmpty;
          case ValidationErrorReason.invalidEmail:
            return l10n.fieldRequired; // Use more specific if available
          case ValidationErrorReason.demoteLastAdmin:
            return l10n.demoteLastAdminError;
          default:
            return l10n.errorValidation;
        }
      },
      validationMissing:
          (fields) => l10n.errorValidationMissing(fields.join(', ')),
      cancelled: () => l10n.cancel,
    );
  }
}
