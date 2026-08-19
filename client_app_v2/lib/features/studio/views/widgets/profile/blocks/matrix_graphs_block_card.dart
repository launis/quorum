import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/base_block_card.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/matrix_graph_item_editor.dart';

/// Collection Builder card for matrix graph entries in payload.layouts.
class MatrixGraphsBlockCard extends StatelessWidget {
  final OutputProfile payload;
  final void Function(OutputProfile) updatePayload;
  final Set<String> allowedBlockIds;
  final AsyncValue<List<PromptBlock>> promptBlocksState;
  final Widget? dragHandle;

  const MatrixGraphsBlockCard({
    super.key,
    required this.payload,
    required this.updatePayload,
    required this.allowedBlockIds,
    required this.promptBlocksState,
    this.dragHandle,
  });

  @override
  Widget build(BuildContext context) {
    final isIncluded = payload.targetBlockOrder.contains(
      TargetBlockType.matrixGraphsBlock,
    );

    final graphLayouts = payload.layouts
        .where((l) => l.presetView != PresetView.matrixSummary)
        .toList();

    return BaseBlockCard(
      blockType: TargetBlockType.matrixGraphsBlock,
      title: 'Matrix Visualizations & Graphs',
      subtitle:
          '1D Metrics, 2D Comparisons, 3D Matrices, and Text-Only matrix presentations',
      icon: Icons.bar_chart_outlined,
      isIncluded: isIncluded,
      dragHandle: dragHandle,
      onToggle: (enabled) {
        final newOrder = List<TargetBlockType>.from(payload.targetBlockOrder);
        if (enabled) {
          if (!newOrder.contains(TargetBlockType.matrixGraphsBlock)) {
            newOrder.add(TargetBlockType.matrixGraphsBlock);
          }
        } else {
          newOrder.remove(TargetBlockType.matrixGraphsBlock);
        }
        updatePayload(payload.copyWith(targetBlockOrder: newOrder));
      },
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          if (graphLayouts.isEmpty)
            Padding(
              padding: const EdgeInsets.symmetric(vertical: AppSpacing.s12),
              child: Text(
                'No graph layouts defined yet. Click "+ Add Graph" below to add a 1D, 2D, or 3D visualization.',
                style: Theme.of(context).textTheme.bodySmall,
              ),
            )
          else
            ...graphLayouts.asMap().entries.map((entry) {
              final idx = entry.key;
              final layout = entry.value;

              return MatrixGraphItemEditor(
                key: ValueKey('graph_item_${idx}_${layout.presetView.name}'),
                index: idx,
                layout: layout,
                allowedBlockIds: allowedBlockIds,
                promptBlocksState: promptBlocksState,
                onUpdate: (updatedLayout) {
                  final newLayouts = List<OutputLayoutBlock>.from(
                    payload.layouts,
                  );
                  final targetIdx = newLayouts.indexOf(layout);
                  if (targetIdx >= 0) {
                    newLayouts[targetIdx] = updatedLayout;
                  }
                  updatePayload(payload.copyWith(layouts: newLayouts));
                },
                onDelete: () {
                  final newLayouts = List<OutputLayoutBlock>.from(
                    payload.layouts,
                  );
                  newLayouts.remove(layout);
                  updatePayload(payload.copyWith(layouts: newLayouts));
                },
              );
            }),
          const SizedBox(height: AppSpacing.s8),
          Align(
            alignment: Alignment.centerLeft,
            child: FilledButton.tonalIcon(
              onPressed: () {
                final newLayouts = List<OutputLayoutBlock>.from(
                  payload.layouts,
                );
                newLayouts.add(
                  const OutputLayoutBlock(
                    presetView: PresetView.metrics1d,
                    targetBlocks: [],
                  ),
                );
                updatePayload(payload.copyWith(layouts: newLayouts));
              },
              icon: const Icon(Icons.add),
              label: const Text('Add Graph'),
            ),
          ),
        ],
      ),
    );
  }
}
