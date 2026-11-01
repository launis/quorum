import 'package:flutter/material.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/features/execution/models/atom_result_dto.dart';
import 'package:client_app/features/execution/providers/hydrated_reference_provider.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

/// Dumb Painter renderer for hydrated TDA atom results mapped to SDUI card variants.
class SduiNodeRenderer extends ConsumerWidget {
  final String executionId;
  final AtomResultDTO result;

  const SduiNodeRenderer({
    super.key,
    required this.executionId,
    required this.result,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final hydratedAtom = ref.watch(
      hydratedReferenceProvider(executionId, result.tdaId),
    );

    if (hydratedAtom == null) {
      throw AppException.validation(
        'Fail-Fast: Missing hydrated reference for TDA ${result.tdaId}',
      );
    }

    return switch (hydratedAtom.sduiComponent) {
      SDUIComponentType.booleanCard => _buildBooleanCard(
        context,
        hydratedAtom.resolvedClaim,
      ),
      SDUIComponentType.extractedValueCard => _buildExtractedValueCard(
        context,
        hydratedAtom.resolvedClaim,
      ),
      SDUIComponentType.errorCard => _buildErrorCard(
        context,
        hydratedAtom.resolvedClaim,
      ),
      SDUIComponentType.nACard => _buildNACard(
        context,
        hydratedAtom.resolvedClaim,
        result.shortCircuitReasonTdaIds,
      ),
    };
  }

  Widget _buildBooleanCard(BuildContext context, String claim) {
    final colorScheme = Theme.of(context).colorScheme;
    final isPassed = result.status == ExecutionStatus.passed;
    return LayoutBuilder(
      builder: (context, constraints) {
        return Card(
          child: Padding(
            padding: AppSpacing.p16,
            child: Row(
              children: [
                Icon(
                  isPassed ? Icons.check_circle : Icons.error,
                  color: isPassed ? colorScheme.primary : colorScheme.error,
                ),
                AppSpacing.w16,
                Expanded(
                  child: Text(
                    claim,
                    overflow: TextOverflow.ellipsis,
                    maxLines: 2,
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildExtractedValueCard(BuildContext context, String claim) {
    final extracted = result.extractedData;
    final hasUnit = extracted?.unit != null && extracted!.unit!.isNotEmpty;
    final formattedValue = extracted != null
        ? (hasUnit
              ? '${extracted.value} ${extracted.unit}'
              : '${extracted.value}')
        : null;

    return LayoutBuilder(
      builder: (context, constraints) {
        return Card(
          child: Padding(
            padding: AppSpacing.p16,
            child: Row(
              children: [
                const Icon(Icons.info),
                AppSpacing.w16,
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(claim, overflow: TextOverflow.ellipsis),
                      if (formattedValue != null) ...[
                        AppSpacing.h8,
                        Text(
                          formattedValue,
                          style: Theme.of(context).textTheme.titleMedium,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ],
                    ],
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildErrorCard(BuildContext context, String claim) {
    final theme = Theme.of(context);
    final onErrorContainer = theme.colorScheme.onErrorContainer;
    final errorTextStyle = theme.textTheme.bodyMedium?.copyWith(
      color: onErrorContainer,
    );

    return LayoutBuilder(
      builder: (context, constraints) {
        return Card(
          color: theme.colorScheme.errorContainer,
          child: Padding(
            padding: AppSpacing.p16,
            child: Row(
              children: [
                Icon(Icons.warning, color: onErrorContainer),
                AppSpacing.w16,
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        claim,
                        style: errorTextStyle,
                        overflow: TextOverflow.ellipsis,
                      ),
                      if (result.errorDetails != null) ...[
                        AppSpacing.h8,
                        Text(
                          result.errorDetails!.message,
                          style: errorTextStyle,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ],
                    ],
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildNACard(
    BuildContext context,
    String claim,
    List<String> cascadeReasons,
  ) {
    final theme = Theme.of(context);
    return LayoutBuilder(
      builder: (context, constraints) {
        return Card(
          color: theme.colorScheme.surfaceContainerHighest,
          child: Padding(
            padding: AppSpacing.p16,
            child: Row(
              children: [
                const Icon(Icons.block),
                AppSpacing.w16,
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        claim,
                        overflow: TextOverflow.ellipsis,
                        style: theme.textTheme.bodyMedium?.copyWith(
                          fontStyle: FontStyle.italic,
                        ),
                      ),
                      if (cascadeReasons.isNotEmpty) ...[
                        AppSpacing.h8,
                        Text(
                          AppLocalizations.of(
                            context,
                          )!.lblNaCascadeReason(cascadeReasons.join(', ')),
                          overflow: TextOverflow.ellipsis,
                          style: theme.textTheme.bodySmall?.copyWith(
                            color: theme.colorScheme.onSurfaceVariant,
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}
