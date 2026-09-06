import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/base_block_card.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/matrix_graph_item_editor.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:uuid/uuid.dart';

/// Collection Builder card for matrix synthesis group entries in payload.matrixSynthesisGroups.
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
    final l10n = AppLocalizations.of(context)!;
    final isIncluded = payload.targetBlockOrder.contains(
      TargetBlockType.matrixGraphsBlock,
    );

    final groups = payload.matrixSynthesisGroups;

    return BaseBlockCard(
      blockType: TargetBlockType.matrixGraphsBlock,
      title: l10n.blockMatrixGraphsTitle,
      subtitle: l10n.blockMatrixGraphsSubtitle,
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
          if (groups.isEmpty)
            Padding(
              padding: const EdgeInsets.symmetric(vertical: AppSpacing.s12),
              child: Text(
                l10n.noGraphLayoutsDefined,
                style: Theme.of(context).textTheme.bodySmall,
              ),
            )
          else
            ReorderableListView(
              buildDefaultDragHandles: false,
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              onReorder: (oldIndex, newIndex) {
                final newGroups = List<MatrixSynthesisGroup>.from(
                  payload.matrixSynthesisGroups,
                );
                if (newIndex > oldIndex) {
                  newIndex -= 1;
                }
                final item = newGroups.removeAt(oldIndex);
                newGroups.insert(newIndex, item);
                updatePayload(
                  payload.copyWith(matrixSynthesisGroups: newGroups),
                );
              },
              children: groups.asMap().entries.map((entry) {
                final idx = entry.key;
                final group = entry.value;

                return MatrixGraphItemEditor(
                  key: ValueKey(group.id),
                  index: idx,
                  group: group,
                  allowedBlockIds: allowedBlockIds,
                  promptBlocksState: promptBlocksState,
                  dragHandle: ReorderableDragStartListener(
                    index: idx,
                    child: const IconButton(
                      icon: Icon(Icons.drag_handle, size: 20),
                      onPressed: null,
                    ),
                  ),
                  onMoveUp: idx > 0
                      ? () {
                          final newGroups = List<MatrixSynthesisGroup>.from(
                            payload.matrixSynthesisGroups,
                          );
                          final item = newGroups.removeAt(idx);
                          newGroups.insert(idx - 1, item);
                          updatePayload(
                            payload.copyWith(matrixSynthesisGroups: newGroups),
                          );
                        }
                      : null,
                  onMoveDown: idx < groups.length - 1
                      ? () {
                          final newGroups = List<MatrixSynthesisGroup>.from(
                            payload.matrixSynthesisGroups,
                          );
                          final item = newGroups.removeAt(idx);
                          newGroups.insert(idx + 1, item);
                          updatePayload(
                            payload.copyWith(matrixSynthesisGroups: newGroups),
                          );
                        }
                      : null,
                  onUpdate: (updatedGroup) {
                    final newGroups = List<MatrixSynthesisGroup>.from(
                      payload.matrixSynthesisGroups,
                    );
                    final targetIdx = newGroups.indexWhere(
                      (g) => g.id == group.id,
                    );
                    if (targetIdx >= 0) {
                      newGroups[targetIdx] = updatedGroup;
                    }
                    updatePayload(
                      payload.copyWith(matrixSynthesisGroups: newGroups),
                    );
                  },
                  onDelete: () {
                    final newGroups = List<MatrixSynthesisGroup>.from(
                      payload.matrixSynthesisGroups,
                    );
                    newGroups.removeWhere((g) => g.id == group.id);
                    updatePayload(
                      payload.copyWith(matrixSynthesisGroups: newGroups),
                    );
                  },
                );
              }).toList(),
            ),
          AppSpacing.h8,
          Align(
            alignment: Alignment.centerLeft,
            child: FilledButton.tonalIcon(
              onPressed: () {
                final newGroups = List<MatrixSynthesisGroup>.from(
                  payload.matrixSynthesisGroups,
                );
                final newIndex = newGroups.length + 1;
                newGroups.add(
                  MatrixSynthesisGroup(
                    id: 'grp_${const Uuid().v4().replaceAll('-', '').substring(0, 16)}',
                    title: I18nText(
                      translations: {
                        'en': 'Group $newIndex',
                        'fi': 'Ryhmä $newIndex',
                      },
                    ),
                    targetBlocks: const [],
                  ),
                );
                updatePayload(
                  payload.copyWith(matrixSynthesisGroups: newGroups),
                );
              },
              icon: const Icon(Icons.add),
              label: Text(l10n.addGraphButton),
            ),
          ),
        ],
      ),
    );
  }
}
