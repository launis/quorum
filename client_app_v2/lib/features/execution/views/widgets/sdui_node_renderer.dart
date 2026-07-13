import 'package:flutter/material.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/features/execution/models/atom_result_dto.dart';
import 'package:client_app/features/execution/providers/hydrated_reference_provider.dart';

// Phase 3, Step 1: Create SduiNodeRenderer (ConsumerWidget)
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
    // Phase 3, Step 1: Use O(1) ref.watch on hydratedReferenceProvider
    final hydratedAtom = ref.watch(
      hydratedReferenceProvider(executionId, result.tdaId),
    );

    if (hydratedAtom == null) {
      // Phase 3, Step 1: No SizedBox.shrink() (Fail-Fast Boundary)
      throw AppException.validation(
        'Fail-Fast: Missing hydrated reference for TDA ${result.tdaId}',
      );
    }

    // Phase 3, Step 1: Use Dart 3 switch expression on hydratedAtom.sduiComponent
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
      ),
      // Any other type not explicitly handled here will cause a compile-time error
      // due to Dart 3 exhaustive switch, enforcing strict alignment with the enum.
    };
  }

  // Phase 3, Step 1: Follow Macro-Breakpoint standard with LayoutBuilder
  Widget _buildBooleanCard(BuildContext context, String claim) {
    return LayoutBuilder(
      builder: (context, constraints) {
        return Card(
          child: Padding(
            padding: AppSpacing.p16,
            child: Row(
              children: [
                Icon(
                  result.status == ExecutionStatus.passed
                      ? Icons.check_circle
                      : Icons.error,
                  color: result.status == ExecutionStatus.passed
                      ? Theme.of(context).colorScheme.primary
                      : Theme.of(context).colorScheme.error,
                ),
                AppSpacing.w16,
                // Phase 3, Step 1: Wrap dynamic text in Expanded + TextOverflow.ellipsis
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
                      if (result.extractedData != null) ...[
                        AppSpacing.h8,
                        Text(
                          '${result.extractedData!.value} ${result.extractedData!.unit ?? ''}',
                          style: Theme.of(context).textTheme.titleMedium,
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
    return LayoutBuilder(
      builder: (context, constraints) {
        return Card(
          color: Theme.of(context).colorScheme.errorContainer,
          child: Padding(
            padding: AppSpacing.p16,
            child: Row(
              children: [
                Icon(
                  Icons.warning,
                  color: Theme.of(context).colorScheme.onErrorContainer,
                ),
                AppSpacing.w16,
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        claim,
                        style: TextStyle(
                          color: Theme.of(context).colorScheme.onErrorContainer,
                        ),
                        overflow: TextOverflow.ellipsis,
                      ),
                      if (result.errorDetails != null) ...[
                        AppSpacing.h8,
                        Text(
                          result.errorDetails!.message,
                          style: TextStyle(
                            color: Theme.of(
                              context,
                            ).colorScheme.onErrorContainer,
                          ),
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

  Widget _buildNACard(BuildContext context, String claim) {
    return LayoutBuilder(
      builder: (context, constraints) {
        return Card(
          color: Theme.of(context).colorScheme.surfaceContainerHighest,
          child: Padding(
            padding: AppSpacing.p16,
            child: Row(
              children: [
                const Icon(Icons.block),
                AppSpacing.w16,
                Expanded(
                  child: Text(
                    claim,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(fontStyle: FontStyle.italic),
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
