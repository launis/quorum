import 'package:flutter/material.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/base_block_card.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

/// Dedicated configuration card for matrixSummaryTableBlock.
class MatrixSummaryTableCard extends StatelessWidget {
  final OutputProfile payload;
  final void Function(OutputProfile) updatePayload;
  final Widget? dragHandle;

  const MatrixSummaryTableCard({
    super.key,
    required this.payload,
    required this.updatePayload,
    this.dragHandle,
  });

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final isIncluded = payload.targetBlockOrder.contains(
      TargetBlockType.matrixSummaryTableBlock,
    );

    return BaseBlockCard(
      blockType: TargetBlockType.matrixSummaryTableBlock,
      title: l10n.blockMatrixSummaryTitle,
      subtitle: l10n.blockMatrixSummarySubtitle,
      icon: Icons.table_chart_outlined,
      isIncluded: isIncluded,
      dragHandle: dragHandle,
      onToggle: (enabled) {
        final newOrder = List<TargetBlockType>.from(payload.targetBlockOrder);
        if (enabled) {
          if (!newOrder.contains(TargetBlockType.matrixSummaryTableBlock)) {
            newOrder.add(TargetBlockType.matrixSummaryTableBlock);
          }
        } else {
          newOrder.remove(TargetBlockType.matrixSummaryTableBlock);
        }
        updatePayload(payload.copyWith(targetBlockOrder: newOrder));
      },
      body: Padding(
        padding: const EdgeInsets.symmetric(vertical: AppSpacing.s8),
        child: Text(
          l10n.blockMatrixSummarySubtitle,
          style: Theme.of(context).textTheme.bodySmall,
        ),
      ),
    );
  }
}
