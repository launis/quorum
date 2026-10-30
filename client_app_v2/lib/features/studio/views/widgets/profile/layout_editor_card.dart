import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';
import 'package:client_app/features/studio/views/widgets/i18n_text_field.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/utils/json_converters.dart';

/// LayoutEditorCard for configuring matrix synthesis groups.
class LayoutEditorCard extends ConsumerWidget {
  final List<MatrixSynthesisGroup> groups;
  final ValueChanged<List<MatrixSynthesisGroup>> onChanged;
  final Set<String> allowedBlockIds;
  final AsyncValue<List<PromptBlock>> promptBlocksState;

  const LayoutEditorCard({
    super.key,
    required this.groups,
    required this.onChanged,
    required this.allowedBlockIds,
    required this.promptBlocksState,
  });

  void _addGroup() {
    final newList = List<MatrixSynthesisGroup>.from(groups);
    final nextIdx = newList.length + 1;
    newList.add(
      MatrixSynthesisGroup(
        id: generateOpaqueUuid7('grp'),
        title: I18nText(
          translations: {'en': 'Group $nextIdx', 'fi': 'Ryhmä $nextIdx'},
        ),
        targetBlocks: const [],
      ),
    );
    onChanged(newList);
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Expanded(
              child: Text(
                l10n.layoutBlocksTitle,
                style: Theme.of(
                  context,
                ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
                overflow: TextOverflow.ellipsis,
              ),
            ),
            AppSpacing.w16,
            Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                FilledButton.icon(
                  onPressed: _addGroup,
                  icon: const Icon(Icons.add_box),
                  label: Text(l10n.addLayoutBlockBtn),
                ),
              ],
            ),
          ],
        ),
        const Divider(),
        if (groups.isEmpty)
          Padding(
            padding: AppSpacing.p16,
            child: Text(l10n.noLayoutBlocksDefined),
          )
        else
          ListView.builder(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            itemCount: groups.length,
            itemBuilder: (context, index) {
              return _CompactMatrixGroupItem(
                index: index,
                group: groups[index],
                onUpdate: (updated) {
                  final newList = List<MatrixSynthesisGroup>.from(groups);
                  newList[index] = updated;
                  onChanged(newList);
                },
                onDelete: () {
                  final newList = List<MatrixSynthesisGroup>.from(groups);
                  newList.removeAt(index);
                  onChanged(newList);
                },
              );
            },
          ),
      ],
    );
  }
}

class _CompactMatrixGroupItem extends StatelessWidget {
  final int index;
  final MatrixSynthesisGroup group;
  final ValueChanged<MatrixSynthesisGroup> onUpdate;
  final VoidCallback onDelete;

  const _CompactMatrixGroupItem({
    required this.index,
    required this.group,
    required this.onUpdate,
    required this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Card(
      elevation: 0,
      margin: const EdgeInsets.only(bottom: AppSpacing.s12),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppSpacing.s8),
        side: BorderSide(color: colorScheme.outlineVariant),
      ),
      child: ExpansionTile(
        initiallyExpanded: index == 0,
        leading: CircleAvatar(
          radius: AppSpacing.s12,
          child: Text(
            (index + 1).toString(),
            style: theme.textTheme.labelSmall,
          ),
        ),
        title: Text(
          group.title.get(
            Localizations.localeOf(context).languageCode,
            fallback: 'en',
          ),
          style: theme.textTheme.bodyMedium?.copyWith(
            fontWeight: FontWeight.bold,
          ),
          overflow: TextOverflow.ellipsis,
        ),
        trailing: IconButton(
          icon: Icon(Icons.delete_outline, color: colorScheme.error),
          tooltip: l10n.deleteButton,
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
        ],
      ),
    );
  }
}
