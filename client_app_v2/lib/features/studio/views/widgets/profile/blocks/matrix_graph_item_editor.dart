import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';
import 'package:client_app/features/studio/views/widgets/i18n_text_field.dart';

import 'package:client_app/l10n/gen/app_localizations.dart';

/// Single item editor within MatrixGraphsBlockCard for configuring a single graph layout.
class MatrixGraphItemEditor extends StatelessWidget {
  final int index;
  final OutputLayoutBlock layout;
  final ValueChanged<OutputLayoutBlock> onUpdate;
  final VoidCallback onDelete;
  final Set<String> allowedBlockIds;
  final AsyncValue<List<PromptBlock>> promptBlocksState;

  const MatrixGraphItemEditor({
    super.key,
    required this.index,
    required this.layout,
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
    final selectableBlocks = allowedBlockIds.isEmpty
        ? blocks
        : blocks.where((b) => allowedBlockIds.contains(b.id)).toList();

    final targetBlocks = List<String>.from(layout.targetBlocks);
    final requiredAxes = _requiredAxesCount(layout.presetView);

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
          layout.title?.translations['en'] ??
              layout.title?.translations.values.firstOrNull ??
              l10n.graphTitleDefault(index + 1, layout.presetView.name),
          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
        ),
        trailing: IconButton(
          icon: Icon(Icons.delete_outline, color: colorScheme.error, size: 20),
          onPressed: onDelete,
        ),
        childrenPadding: AppSpacing.p12,
        children: [
          SegmentedButton<PresetView>(
            segments: [
              ButtonSegment(
                value: PresetView.metrics1d,
                label: Text(l10n.presetView1d, overflow: TextOverflow.ellipsis),
              ),
              ButtonSegment(
                value: PresetView.compare2d,
                label: Text(l10n.presetView2d, overflow: TextOverflow.ellipsis),
              ),
              ButtonSegment(
                value: PresetView.matrix3d,
                label: Text(l10n.presetView3d, overflow: TextOverflow.ellipsis),
              ),
              ButtonSegment(
                value: PresetView.textOnly,
                label: Text(
                  l10n.presetViewTextOnly,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
            selected: {
              [
                    PresetView.metrics1d,
                    PresetView.compare2d,
                    PresetView.matrix3d,
                    PresetView.textOnly,
                  ].contains(layout.presetView)
                  ? layout.presetView
                  : PresetView.metrics1d,
            },
            onSelectionChanged: (selected) {
              onUpdate(layout.copyWith(presetView: selected.first));
            },
          ),
          const SizedBox(height: AppSpacing.s12),
          I18nTextField(
            label: l10n.graphTitleLabel,
            initialData: layout.title,
            onChanged: (val) {
              onUpdate(
                layout.copyWith(title: val.translations.isEmpty ? null : val),
              );
            },
          ),
          if (requiredAxes > 0) ...[
            const SizedBox(height: AppSpacing.s12),
            for (int axisIdx = 0; axisIdx < requiredAxes; axisIdx++) ...[
              _buildAxisDropdown(
                context,
                l10n: l10n,
                axisIdx: axisIdx,
                targetBlocks: targetBlocks,
                selectableBlocks: selectableBlocks,
              ),
              const SizedBox(height: AppSpacing.s8),
            ],
          ],
        ],
      ),
    );
  }

  int _requiredAxesCount(PresetView preset) {
    return switch (preset) {
      PresetView.metrics1d => 1,
      PresetView.compare2d => 2,
      PresetView.matrix3d => 3,
      PresetView.textOnly => 0,
      _ => 1,
    };
  }

  Widget _buildAxisDropdown(
    BuildContext context, {
    required AppLocalizations l10n,
    required int axisIdx,
    required List<String> targetBlocks,
    required List<PromptBlock> selectableBlocks,
  }) {
    final axisLabels = [
      l10n.axisXPrimary,
      l10n.axisYComparison,
      l10n.axisZDepth,
    ];
    final currentVal = axisIdx < targetBlocks.length
        ? targetBlocks[axisIdx]
        : null;
    final otherSelected = List<String>.from(targetBlocks)..remove(currentVal);

    return DropdownButtonFormField<String?>(
      initialValue: currentVal,
      isExpanded: true,
      decoration: InputDecoration(
        labelText: axisLabels[axisIdx],
        border: const OutlineInputBorder(),
        isDense: true,
      ),
      items: [
        DropdownMenuItem<String?>(
          value: null,
          child: Text(l10n.selectBlockHint),
        ),
        ...selectableBlocks.map((block) {
          final isDuplicate = otherSelected.contains(block.id);
          final label = block.label.translations['en'] ?? block.slug;
          return DropdownMenuItem<String?>(
            value: block.id,
            enabled: !isDuplicate,
            child: Text(
              isDuplicate
                  ? l10n.alreadySelectedOnOtherAxis(label)
                  : '$label (${block.id})',
              style: TextStyle(
                color: isDuplicate ? Theme.of(context).disabledColor : null,
              ),
            ),
          );
        }),
      ],
      onChanged: (val) {
        final newTargets = List<String>.from(targetBlocks);
        while (newTargets.length <= axisIdx) {
          newTargets.add('');
        }
        if (val != null && val.isNotEmpty) {
          newTargets[axisIdx] = val;
        } else {
          newTargets.removeAt(axisIdx);
        }
        onUpdate(
          layout.copyWith(
            targetBlocks: newTargets.where((s) => s.isNotEmpty).toList(),
          ),
        );
      },
    );
  }
}
