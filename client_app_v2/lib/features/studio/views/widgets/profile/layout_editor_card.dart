import 'package:flutter/material.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';
import 'package:client_app/features/studio/views/widgets/i18n_text_field.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/features/studio/views/widgets/profile/synthesis_editor_card.dart';

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
        presetView: '1d_metrics',
        title: I18nText(defaultLocale: 'en'),
        showText: true,
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
            padding: const EdgeInsets.all(16.0),
            child: Text(l10n.noLayoutBlocksDefined),
          )
        else
          ListView.builder(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            itemCount: layouts.length,
            itemBuilder: (context, index) {
              return _buildLayoutEditor(context, l10n, index, layouts[index]);
            },
          ),
      ],
    );
  }

  Widget _buildLayoutEditor(
    BuildContext context,
    AppLocalizations l10n,
    int index,
    OutputLayoutBlock layout,
  ) {
    final blocksList = List<String>.from(layout.targetBlocks);

    String currentPreset = layout.presetView;
    if (![
      '1d_metrics',
      '2d_compare',
      '3d_complex',
      'text_only',
      'default',
    ].contains(currentPreset)) {
      currentPreset = '1d_metrics';
    }

    final bool showText = layout.showText;

    void updateLayout(OutputLayoutBlock updated) {
      final newList = List<OutputLayoutBlock>.from(layouts);
      newList[index] = updated;
      onChanged(newList);
    }

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surfaceContainer,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Theme.of(context).colorScheme.outlineVariant),
      ),
      child: Column(
        children: [
          Row(
            children: [
              CircleAvatar(
                radius: 12,
                child: Text(
                  '${index + 1}',
                  style: const TextStyle(fontSize: 12),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: DropdownButtonFormField<String>(
                  initialValue: currentPreset,
                  isExpanded: true,
                  decoration: InputDecoration(
                    labelText: l10n.presetViewLabel,
                    isDense: true,
                  ),
                  items: [
                    DropdownMenuItem(
                      value: '1d_metrics',
                      child: Text(
                        l10n.preset1dTable,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    DropdownMenuItem(
                      value: '2d_compare',
                      child: Text(
                        l10n.preset2dGrid,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    DropdownMenuItem(
                      value: '3d_complex',
                      child: Text(
                        l10n.preset3dRadar,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    DropdownMenuItem(
                      value: 'text_only',
                      child: Text(
                        l10n.presetTextOnly,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    DropdownMenuItem(
                      value: 'default',
                      child: Text(
                        l10n.presetAutomatic,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ],
                  onChanged: (val) {
                    if (val != null) {
                      updateLayout(layout.copyWith(presetView: val));
                    }
                  },
                ),
              ),
              const SizedBox(width: 12),
              Row(
                children: [
                  Text(l10n.showTextLabel),
                  Switch(
                    value: showText,
                    onChanged: (val) {
                      updateLayout(layout.copyWith(showText: val));
                    },
                  ),
                ],
              ),
              IconButton(
                icon: Icon(
                  Icons.delete_outline,
                  color: Theme.of(context).colorScheme.error,
                ),
                onPressed: () {
                  final newList = List<OutputLayoutBlock>.from(layouts);
                  newList.removeAt(index);
                  onChanged(newList);
                },
              ),
            ],
          ),
          const SizedBox(height: 12),
          I18nTextField(
            label: l10n.layoutBlockTitleLabel,
            initialData: layout.title ?? const I18nText(defaultLocale: 'en'),
            onChanged: (val) {
              final isEmpty =
                  val.translations.isEmpty ||
                  val.translations.values.every((v) => v.trim().isEmpty);
              updateLayout(layout.copyWith(title: isEmpty ? null : val));
            },
          ),
          const SizedBox(height: 12),
          SwitchListTile(
            title: const Text(
              'Käytä osiokohtaista synteesiä (Section-Level Synthesis)',
            ),
            subtitle: const Text(
              'Ohittaa globaalin raporttisynteesin asetukset tälle osiolle',
            ),
            value: layout.synthesis != null,
            onChanged: (val) {
              if (val) {
                updateLayout(
                  layout.copyWith(synthesis: const SynthesisConfigDTO()),
                );
              } else {
                updateLayout(layout.copyWith(synthesis: null));
              }
            },
            controlAffinity: ListTileControlAffinity.leading,
            contentPadding: EdgeInsets.zero,
          ),
          if (layout.synthesis != null)
            Padding(
              padding: const EdgeInsets.only(
                top: 8.0,
                left: 4.0,
                right: 4.0,
                bottom: 12.0,
              ),
              child: SynthesisEditorCard(
                synthesis: layout.synthesis,
                onChanged: (val) {
                  updateLayout(layout.copyWith(synthesis: val));
                },
              ),
            ),
          const SizedBox(height: 12),
          Align(
            alignment: Alignment.centerLeft,
            child: Text(
              l10n.targetComponentsTitle,
              style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 13),
            ),
          ),
          const SizedBox(height: 8),
          promptBlocksState.when(
            data: (rawBlocks) {
              final blocks = rawBlocks.cast<PromptBlock>();

              final targetBlocks = blocks.where((b) {
                final isAllowed =
                    allowedBlockIds.isEmpty ||
                    allowedBlockIds.contains(b.id) ||
                    allowedBlockIds.contains(b.slug);
                if (!isAllowed) return false;

                final isMatrix = b.categoryId == 'matrix';
                final extensions = b.outputExtensions;
                return isMatrix || extensions.isNotEmpty;
              }).toList();

              final int requiredDropdowns = switch (currentPreset) {
                '1d_metrics' => 1,
                '2d_compare' => 2,
                '3d_complex' => 3,
                _ => 1,
              };

              final List<Widget> dropdowns = [];
              for (int i = 0; i < requiredDropdowns; i++) {
                String? selectedValue;
                if (i < blocksList.length) {
                  final val = blocksList[i];
                  if (val == '*' || targetBlocks.any((b) => b.id == val)) {
                    selectedValue = val;
                  }
                }

                final String axisLabel = switch (i) {
                  0 => l10n.componentXAxisLabel,
                  1 => l10n.componentYAxisLabel,
                  2 => l10n.componentZAxisLabel,
                  _ => l10n.componentGenericLabel('${i + 1}'),
                };

                dropdowns.add(
                  Padding(
                    padding: const EdgeInsets.only(bottom: 8.0),
                    child: DropdownButtonFormField<String>(
                      initialValue: selectedValue,
                      isExpanded: true,
                      decoration: InputDecoration(
                        labelText: axisLabel,
                        isDense: true,
                        border: const OutlineInputBorder(),
                      ),
                      hint: Text(l10n.selectComponentHint),
                      items: [
                        DropdownMenuItem(
                          value: '*',
                          child: Text(
                            l10n.selectAllComponentsLabel,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                        ...targetBlocks.map((block) {
                          final blockId = block.id;
                          final localeCode = Localizations.localeOf(
                            context,
                          ).languageCode;
                          final i18nVal = block.label.get(localeCode);
                          final blockName = i18nVal.isNotEmpty
                              ? i18nVal
                              : blockId;

                          return DropdownMenuItem(
                            value: blockId,
                            child: Text(
                              blockName,
                              overflow: TextOverflow.ellipsis,
                            ),
                          );
                        }),
                      ],
                      onChanged: (val) {
                        if (val != null) {
                          while (blocksList.length <= i) {
                            blocksList.add('');
                          }
                          blocksList[i] = val;
                          updateLayout(
                            layout.copyWith(
                              targetBlocks: blocksList
                                  .where((b) => b.isNotEmpty)
                                  .toList(),
                            ),
                          );
                        }
                      },
                    ),
                  ),
                );
              }

              return Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: dropdowns,
              );
            },
            loading: () => const Align(
              alignment: Alignment.centerLeft,
              child: CircularProgressIndicator(),
            ),
            error: (e, _) =>
                Text(l10n.studioViewsErrorLoadingBlocks(e.toString())),
          ),
        ],
      ),
    );
  }
}
