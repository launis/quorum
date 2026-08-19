import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/views/widgets/i18n_text_field.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/theme/app_spacing.dart';

/// Legacy LayoutEditorCard preserved for backward compatibility and compact layout list editing.
class LayoutEditorCard extends ConsumerWidget {
  final List<OutputLayoutBlock> layouts;
  final Function(List<OutputLayoutBlock>) onChanged;
  final Set<String> allowedBlockIds;
  final AsyncValue<List<dynamic>> promptBlocksState;

  const LayoutEditorCard({
    super.key,
    required this.layouts,
    required this.onChanged,
    required this.allowedBlockIds,
    required this.promptBlocksState,
  });

  void _addLayout() {
    final newList = List<OutputLayoutBlock>.from(layouts);
    newList.add(
      const OutputLayoutBlock(
        presetView: PresetView.metrics1d,
        title: I18nText(defaultLocale: 'en'),
        textDeliveryMode: TextDeliveryMode.full,
        targetBlocks: [],
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
              onPressed: _addLayout,
              icon: const Icon(Icons.add_box),
              label: Text(l10n.addLayoutBlockBtn),
            ),
          ],
        ),
        const Divider(),
        if (layouts.isEmpty)
          Padding(
            padding: AppSpacing.p16,
            child: Text(l10n.noLayoutBlocksDefined),
          )
        else
          ListView.builder(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            itemCount: layouts.length,
            itemBuilder: (context, index) {
              return _CompactLayoutBlockItem(
                index: index,
                layout: layouts[index],
                onUpdate: (updated) {
                  final newList = List<OutputLayoutBlock>.from(layouts);
                  newList[index] = updated;
                  onChanged(newList);
                },
                onDelete: () {
                  final newList = List<OutputLayoutBlock>.from(layouts);
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

class _CompactLayoutBlockItem extends StatelessWidget {
  final int index;
  final OutputLayoutBlock layout;
  final ValueChanged<OutputLayoutBlock> onUpdate;
  final VoidCallback onDelete;

  const _CompactLayoutBlockItem({
    required this.index,
    required this.layout,
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
          layout.title?.translations['en'] ??
              layout.title?.translations.values.firstOrNull ??
              'Layout #${index + 1} (${layout.presetView.name})',
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        trailing: IconButton(
          icon: Icon(Icons.delete_outline, color: colorScheme.error),
          onPressed: onDelete,
        ),
        childrenPadding: AppSpacing.p12,
        children: [
          DropdownButtonFormField<PresetView>(
            initialValue: layout.presetView,
            isExpanded: true,
            decoration: const InputDecoration(
              labelText: 'Preset View',
              border: OutlineInputBorder(),
              isDense: true,
            ),
            items: PresetView.values.map((pv) {
              return DropdownMenuItem(value: pv, child: Text(pv.name));
            }).toList(),
            onChanged: (val) {
              if (val != null) {
                onUpdate(layout.copyWith(presetView: val));
              }
            },
          ),
          const SizedBox(height: AppSpacing.s12),
          I18nTextField(
            label: 'Layout Title',
            initialData: layout.title,
            onChanged: (val) {
              onUpdate(
                layout.copyWith(title: val.translations.isEmpty ? null : val),
              );
            },
          ),
        ],
      ),
    );
  }
}
