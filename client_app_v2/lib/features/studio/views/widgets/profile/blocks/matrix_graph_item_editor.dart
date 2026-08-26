import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';
import 'package:client_app/features/studio/views/widgets/i18n_text_field.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

/// Single item editor within MatrixGraphsBlockCard for configuring a MatrixSynthesisGroup.
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
    final selectableBlocks = allowedBlockIds.isEmpty
        ? blocks
        : blocks.where((b) => allowedBlockIds.contains(b.id)).toList();

    final targetBlocks = List<String>.from(group.targetBlocks);

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
          const SizedBox(height: AppSpacing.s12),
          Text(
            l10n.selectBlockHint,
            style: theme.textTheme.labelMedium?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: AppSpacing.s8),
          Wrap(
            spacing: AppSpacing.s8,
            runSpacing: AppSpacing.s4,
            children: selectableBlocks.map((block) {
              final isSelected = targetBlocks.contains(block.id);
              final label = block.label.translations['en'] ?? block.slug;
              return FilterChip(
                label: Text('$label (${block.id})'),
                selected: isSelected,
                onSelected: (selected) {
                  final newTargets = List<String>.from(targetBlocks);
                  if (selected) {
                    if (!newTargets.contains(block.id)) {
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
          const SizedBox(height: AppSpacing.s12),
          TextFormField(
            initialValue: group.synthesisDirective ?? '',
            decoration: const InputDecoration(
              labelText: 'Synthesis Directive (Optional)',
              border: OutlineInputBorder(),
              isDense: true,
            ),
            maxLines: 2,
            onChanged: (val) {
              onUpdate(
                group.copyWith(
                  synthesisDirective: val.trim().isEmpty ? null : val.trim(),
                ),
              );
            },
          ),
        ],
      ),
    );
  }
}
