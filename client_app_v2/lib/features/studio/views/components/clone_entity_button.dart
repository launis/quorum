import 'package:client_app/core/error/app_error_ext.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/state/mutation.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';

/// A standardized button for cloning Admin Studio entities securely.
/// Enforces Riverpod 3.0 Mutation side-effects, I18n No-String Mandate,
/// and Dual-Reporting Telemetry for the Zero-Latency PC illusion.
class CloneEntityButton extends HookConsumerWidget {
  final Future<Object?> Function() onClone;

  const CloneEntityButton({super.key, required this.onClone});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;

    final mutationParams = useMutation<Object?>(
      onSuccess: (_) {
        if (!context.mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(l10n.msgEntityClonedSuccess),
            behavior: SnackBarBehavior.floating,
          ),
        );
      },
      onError: (error) {
        // Dual-Reporting: Log to telemetry endpoint FIRST
        ref
            .read(loggerServiceProvider)
            .error('CloneEntityButton', 'Clone operation failed', error);

        if (!context.mounted) return;
        // Then show the actionable hint to the user
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              l10n.msgEntityCloneFailed(
                AppExceptionX.extractLocalizedHint(error, l10n),
              ),
            ),
            backgroundColor: Theme.of(context).colorScheme.error,
            behavior: SnackBarBehavior.floating,
          ),
        );
      },
    );

    if (mutationParams.isLoading) {
      return const Padding(
        padding: AppSpacing.p12,
        child: SizedBox(
          width: AppSpacing.s24,
          height: AppSpacing.s24,
          child: CircularProgressIndicator(strokeWidth: AppSpacing.s2),
        ),
      );
    }

    return IconButton(
      icon: const Icon(Icons.copy),
      tooltip: l10n.tooltipDuplicate,
      onPressed: () => mutationParams.mutate(() => onClone()),
    );
  }
}
