import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/views/widgets/i18n_text_field.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:uuid/uuid.dart';

/// LayoutEditorCard for configuring matrix synthesis groups.
class LayoutEditorCard extends ConsumerWidget {
  final List<MatrixSynthesisGroup> groups;
  final Function(List<MatrixSynthesisGroup>) onChanged;
  final Set<String> allowedBlockIds;
  final AsyncValue<List<dynamic>> promptBlocksState;

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
        id: 'grp_${const Uuid().v4().replaceAll('-', '').substring(0, 16)}',
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
            Text(
              l10n.layoutBlocksTitle,
              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
            ),
            FilledButton.icon(
              onPressed: _addGroup,
              icon: const Icon(Icons.add_box),
              label: Text(l10n.addLayoutBlockBtn),
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
    final colorScheme = Theme.of(context).colorScheme;

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
          radius: 12,
          child: Text('${index + 1}', style: const TextStyle(fontSize: 11)),
        ),
        title: Text(
          group.title.translations['en'] ??
              group.title.translations.values.firstOrNull ??
              'Group #${index + 1}',
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        trailing: IconButton(
          icon: Icon(Icons.delete_outline, color: colorScheme.error),
          onPressed: onDelete,
        ),
        childrenPadding: AppSpacing.p12,
        children: [
          I18nTextField(
            label: 'Group Title',
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
