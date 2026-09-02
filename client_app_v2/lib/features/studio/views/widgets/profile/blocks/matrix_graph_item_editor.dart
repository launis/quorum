import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';
import 'package:client_app/features/studio/views/widgets/i18n_text_field.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

/// Single item editor within MatrixGraphsBlockCard for configuring a MatrixSynthesisGroup.
/// Clearly separates visual chart geometry/axes from LLM narrative synthesis directives.
class MatrixGraphItemEditor extends StatelessWidget {
  final int index;
  final MatrixSynthesisGroup group;
  final ValueChanged<MatrixSynthesisGroup> onUpdate;
  final VoidCallback onDelete;
  final Set<String> allowedBlockIds;
  final AsyncValue<List<PromptBlock>> promptBlocksState;

  const MatrixGraphItemEditor({
    super.key,
    required this.index,
    required this.group,
    required this.onUpdate,
    required this.onDelete,
    required this.allowedBlockIds,
    required this.promptBlocksState,
  });

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final blocks = promptBlocksState.value ?? [];

    // Filter strictly to matrix category prompt blocks
    final matrixBlocks = blocks.where((b) {
      final isCategoryMatrix = b is MatrixPromptBlock;
      if (allowedBlockIds.isEmpty) {
        return isCategoryMatrix;
      }
      return isCategoryMatrix && allowedBlockIds.contains(b.id);
    }).toList();

    final targetBlocks = List<String>.from(group.targetBlocks);
    final currentViewType = group.viewType;

    // Slot capacity per view type
    final int maxSlots = switch (currentViewType) {
      PresetView.metrics1d => 1,
      PresetView.compare2d => 2,
      PresetView.matrix3d => 3,
      PresetView.textOnly => 1,
      _ => 1,
    };

    return Card(
      elevation: 0,
      margin: const EdgeInsets.only(bottom: AppSpacing.s8),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppSpacing.s8),
        side: BorderSide(color: colorScheme.outlineVariant),
      ),
      child: ExpansionTile(
        initiallyExpanded: index == 0,
        leading: CircleAvatar(
          radius: 12,
          child: Text('${index + 1}', style: const TextStyle(fontSize: 11)),
        ),
        title: Text(
          group.title.translations['en'] ??
              group.title.translations.values.firstOrNull ??
              'Group ${index + 1}',
          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
        ),
        trailing: IconButton(
          icon: Icon(Icons.delete_outline, color: colorScheme.error, size: 20),
          onPressed: onDelete,
        ),
        childrenPadding: AppSpacing.p12,
        children: [
          I18nTextField(
            label: l10n.graphTitleLabel,
            initialData: group.title,
            onChanged: (val) {
              onUpdate(group.copyWith(title: val));
            },
          ),
          AppSpacing.h16,

          // SECTION 1: VISUAL CHART CONFIGURATION
          Container(
            padding: AppSpacing.p12,
            decoration: BoxDecoration(
              color: colorScheme.surfaceContainerLow,
              borderRadius: BorderRadius.circular(AppSpacing.s8),
              border: Border.all(color: colorScheme.outlineVariant),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Row(
                  children: [
                    Icon(
                      Icons.bar_chart_outlined,
                      size: 18,
                      color: colorScheme.primary,
                    ),
                    AppSpacing.w8,
                    Text(
                      l10n.groupVisualChartTitle,
                      style: theme.textTheme.labelMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: colorScheme.primary,
                      ),
                    ),
                  ],
                ),
                AppSpacing.h8,
                Text(
                  'Näkymätyyppi (View Type)',
                  style: theme.textTheme.labelSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: AppSpacing.s4),
                SegmentedButton<PresetView>(
                  segments: const [
                    ButtonSegment(
                      value: PresetView.metrics1d,
                      label: Text('1D Mittari'),
                      icon: Icon(Icons.speed),
                    ),
                    ButtonSegment(
                      value: PresetView.compare2d,
                      label: Text('2D Vertailu'),
                      icon: Icon(Icons.scatter_plot),
                    ),
                    ButtonSegment(
                      value: PresetView.matrix3d,
                      label: Text('3D Tutka'),
                      icon: Icon(Icons.radar),
                    ),
                    ButtonSegment(
                      value: PresetView.textOnly,
                      label: Text('Teksti'),
                      icon: Icon(Icons.article_outlined),
                    ),
                  ],
                  selected: {currentViewType},
                  onSelectionChanged: (newSelection) {
                    final selectedType = newSelection.first;
                    final newLimit = switch (selectedType) {
                      PresetView.metrics1d => 1,
                      PresetView.compare2d => 2,
                      PresetView.matrix3d => 3,
                      PresetView.textOnly => 1,
                      _ => 1,
                    };

                    final trimmedTargets = targetBlocks.length > newLimit
                        ? targetBlocks.sublist(0, newLimit)
                        : targetBlocks;

                    onUpdate(
                      group.copyWith(
                        viewType: selectedType,
                        targetBlocks: trimmedTargets,
                      ),
                    );
                  },
                ),
                AppSpacing.h12,
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      l10n.selectBlockHint,
                      style: theme.textTheme.labelSmall?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    Text(
                      '${targetBlocks.length} / $maxSlots valittu',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: targetBlocks.length == maxSlots
                            ? colorScheme.primary
                            : colorScheme.outline,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: AppSpacing.s8),
                if (matrixBlocks.isEmpty)
                  Padding(
                    padding: const EdgeInsets.symmetric(
                      vertical: AppSpacing.s8,
                    ),
                    child: Text(
                      'Ei matriiseja valittavissa työnkulussa.',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: colorScheme.error,
                      ),
                    ),
                  )
                else
                  Wrap(
                    spacing: AppSpacing.s8,
                    runSpacing: AppSpacing.s4,
                    children: matrixBlocks.map((block) {
                      final isSelected = targetBlocks.contains(block.id);
                      final canSelectMore = targetBlocks.length < maxSlots;
                      final label =
                          block.label.translations['en'] ?? block.slug;

                      return FilterChip(
                        label: Text('$label (${block.id})'),
                        selected: isSelected,
                        onSelected: (selected) {
                          final newTargets = List<String>.from(targetBlocks);
                          if (selected) {
                            if (maxSlots == 1) {
                              newTargets.clear();
                              newTargets.add(block.id);
                            } else if (canSelectMore) {
                              newTargets.add(block.id);
                            }
                          } else {
                            newTargets.remove(block.id);
                          }
                          onUpdate(group.copyWith(targetBlocks: newTargets));
                        },
                      );
                    }).toList(),
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
