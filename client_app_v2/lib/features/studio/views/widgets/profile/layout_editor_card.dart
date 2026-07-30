import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';
import 'package:client_app/features/studio/views/widgets/i18n_text_field.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/features/studio/views/widgets/profile/synthesis_editor_card.dart';
import 'package:client_app/core/theme/app_spacing.dart';

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
              return _LayoutBlockEditorItem(
                index: index,
                layout: layouts[index],
                layouts: layouts,
                onChanged: onChanged,
                allowedBlockIds: allowedBlockIds,
                promptBlocksState: promptBlocksState,
              );
            },
          ),
      ],
    );
  }
}

class _LayoutBlockEditorItem extends HookConsumerWidget {
  final int index;
  final OutputLayoutBlock layout;
  final List<OutputLayoutBlock> layouts;
  final Function(List<OutputLayoutBlock>) onChanged;
  final Set<String> allowedBlockIds;
  final AsyncValue<List<dynamic>> promptBlocksState;

  const _LayoutBlockEditorItem({
    required this.index,
    required this.layout,
    required this.layouts,
    required this.onChanged,
    required this.allowedBlockIds,
    required this.promptBlocksState,
  });

  void updateLayout(OutputLayoutBlock updated) {
    final newList = List<OutputLayoutBlock>.from(layouts);
    newList[index] = updated;
    onChanged(newList);
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final activeTab = useState<int>(0);

    return Container(
      margin: const EdgeInsets.only(bottom: AppSpacing.s12),
      padding: AppSpacing.p12,
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surfaceContainer,
        borderRadius: BorderRadius.circular(AppSpacing.s8),
        border: Border.all(color: Theme.of(context).colorScheme.outlineVariant),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              CircleAvatar(
                radius: AppSpacing.s12,
                child: Text(
                  '${index + 1}',
                  style: const TextStyle(fontSize: 12),
                ),
              ),
              const SizedBox(width: AppSpacing.s12),
              Expanded(
                child: SegmentedButton<int>(
                  segments: const [
                    ButtonSegment(
                      value: 0,
                      label: Text(
                        'Basic Info',
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    ButtonSegment(
                      value: 1,
                      label: Text(
                        'Data & Blocks',
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    ButtonSegment(
                      value: 2,
                      label: Text(
                        'Terminology',
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ],
                  selected: {activeTab.value},
                  onSelectionChanged: (Set<int> newSelection) {
                    activeTab.value = newSelection.first;
                  },
                ),
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
          AppSpacing.h16,
          if (activeTab.value == 0) _buildPart1(context, l10n),
          if (activeTab.value == 1) _buildPart2(context, l10n),
          if (activeTab.value == 2) _buildPart3(context, l10n),
        ],
      ),
    );
  }

  Widget _buildPart1(BuildContext context, AppLocalizations l10n) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Row(
          children: [
            Expanded(
              child: DropdownButtonFormField<PresetView>(
                initialValue: layout.presetView,
                isExpanded: true,
                decoration: InputDecoration(
                  labelText: l10n.presetViewLabel,
                  isDense: true,
                ),
                items: [
                  DropdownMenuItem(
                    value: PresetView.metrics1d,
                    child: Text(
                      l10n.preset1dTable,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  DropdownMenuItem(
                    value: PresetView.compare2d,
                    child: Text(
                      l10n.preset2dGrid,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  DropdownMenuItem(
                    value: PresetView.complex3d,
                    child: const Text(
                      '3D: Radar (Spider)',
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  DropdownMenuItem(
                    value: PresetView.matrix3d,
                    child: const Text(
                      '3D: Matrix (Bubble)',
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  DropdownMenuItem(
                    value: PresetView.textOnly,
                    child: Text(
                      l10n.presetTextOnly,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  DropdownMenuItem(
                    value: PresetView.defaultView,
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
            const SizedBox(width: AppSpacing.s12),
            Expanded(
              child: DropdownButtonFormField<TextDeliveryMode>(
                initialValue: layout.textDeliveryMode,
                isExpanded: true,
                decoration: InputDecoration(
                  labelText: l10n.textDeliveryModeLabel,
                  isDense: true,
                ),
                items: [
                  DropdownMenuItem(
                    value: TextDeliveryMode.full,
                    child: Text(
                      l10n.textModeFull,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  DropdownMenuItem(
                    value: TextDeliveryMode.titlesOnly,
                    child: Text(
                      l10n.textModeTitlesOnly,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  DropdownMenuItem(
                    value: TextDeliveryMode.none,
                    child: Text(
                      l10n.textModeNone,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
                onChanged: (val) {
                  if (val != null) {
                    updateLayout(layout.copyWith(textDeliveryMode: val));
                  }
                },
              ),
            ),
          ],
        ),
        AppSpacing.h12,
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
        AppSpacing.h12,
        I18nTextField(
          label: l10n.layoutBlockDescriptionLabel,
          initialData:
              layout.description ?? const I18nText(defaultLocale: 'en'),
          onChanged: (val) {
            final isEmpty =
                val.translations.isEmpty ||
                val.translations.values.every((v) => v.trim().isEmpty);
            updateLayout(layout.copyWith(description: isEmpty ? null : val));
          },
        ),
      ],
    );
  }

  Widget _buildPart2(BuildContext context, AppLocalizations l10n) {
    final blocksList = List<String>.from(layout.targetBlocks);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        SwitchListTile(
          title: Text(l10n.sectionSynthesisToggleLabel),
          subtitle: Text(l10n.sectionSynthesisToggleDesc),
          value: layout.isSynthesisEnabled,
          onChanged: (val) {
            updateLayout(layout.copyWith(isSynthesisEnabled: val));
          },
          controlAffinity: ListTileControlAffinity.leading,
          contentPadding: EdgeInsets.zero,
        ),
        AppSpacing.h12,
        SwitchListTile(
          title: Text(l10n.sectionCustomSynthesisLabel),
          subtitle: Text(l10n.sectionCustomSynthesisDesc),
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
              top: AppSpacing.s8,
              left: AppSpacing.s4,
              right: AppSpacing.s4,
              bottom: AppSpacing.s12,
            ),
            child: SynthesisEditorCard(
              synthesis: layout.synthesis,
              isGlobal: false,
              onChanged: (val) {
                updateLayout(layout.copyWith(synthesis: val));
              },
            ),
          ),
        AppSpacing.h12,
        TextFormField(
          initialValue: layout.steps.join(', '),
          decoration: InputDecoration(
            labelText: l10n.studioStepsTitle,
            isDense: true,
            hintText: 'step_1, step_2',
            border: const OutlineInputBorder(),
          ),
          onChanged: (val) {
            final stepsList = val
                .split(',')
                .map((s) => s.trim())
                .where((s) => s.isNotEmpty)
                .toList();
            updateLayout(layout.copyWith(steps: stepsList));
          },
        ),
        AppSpacing.h16,
        Align(
          alignment: Alignment.centerLeft,
          child: Text(
            l10n.targetComponentsTitle,
            style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 13),
          ),
        ),
        AppSpacing.h8,
        promptBlocksState.when(
          data: (rawBlocks) {
            final blocks = rawBlocks.cast<PromptBlock>();
            final targetBlocks = blocks.where((b) {
              final isAllowed =
                  allowedBlockIds.isEmpty || allowedBlockIds.contains(b.id);
              if (!isAllowed) return false;
              final isMatrix = b.categoryId == 'matrix';
              final extensions = b.outputExtensions;
              return isMatrix || extensions.isNotEmpty;
            }).toList();

            final int requiredDropdowns = switch (layout.presetView) {
              PresetView.metrics1d => 1,
              PresetView.compare2d => 2,
              PresetView.complex3d => 3,
              PresetView.matrix3d => 3,
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
                  padding: const EdgeInsets.only(bottom: AppSpacing.s8),
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
                    autovalidateMode: AutovalidateMode.onUserInteraction,
                    validator: (val) {
                      if (val != null && val != '*') {
                        final occurrenceCount = blocksList
                            .where((b) => b == val)
                            .length;
                        if (occurrenceCount > 1) {
                          try {
                            return (l10n as dynamic).duplicateComponentError;
                          } catch (e) {
                            return 'Sama komponentti valittu useasti / Duplicate component';
                          }
                        }
                      }
                      return null;
                    },
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
    );
  }

  Widget _buildPart3(BuildContext context, AppLocalizations l10n) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        _DictionaryMapEditor(
          title: 'Matrix Column Labels',
          map: layout.matrixColumnLabels,
          onChanged: (newMap) {
            updateLayout(layout.copyWith(matrixColumnLabels: newMap));
          },
        ),
      ],
    );
  }
}

class _DictionaryMapEditor extends StatelessWidget {
  final String title;
  final Map<String, I18nText> map;
  final Function(Map<String, I18nText>) onChanged;

  const _DictionaryMapEditor({
    required this.title,
    required this.map,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              title,
              style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 13),
            ),
            FilledButton.icon(
              onPressed: () {
                final newMap = Map<String, I18nText>.from(map);
                newMap['new_key_${newMap.length}'] = const I18nText(
                  defaultLocale: 'en',
                );
                onChanged(newMap);
              },
              icon: const Icon(Icons.add),
              label: const Text('Add Term'),
            ),
          ],
        ),
        AppSpacing.h8,
        if (map.isEmpty)
          const Padding(
            padding: AppSpacing.p8,
            child: Text('No terms defined.'),
          )
        else
          ...map.entries.map((entry) {
            return Padding(
              padding: const EdgeInsets.only(bottom: AppSpacing.s8),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Expanded(
                    flex: 1,
                    child: TextFormField(
                      initialValue: entry.key,
                      decoration: const InputDecoration(
                        labelText: 'Key',
                        isDense: true,
                      ),
                      onChanged: (newKey) {
                        final newMap = <String, I18nText>{};
                        for (final e in map.entries) {
                          if (e.key == entry.key) {
                            newMap[newKey] = e.value;
                          } else {
                            newMap[e.key] = e.value;
                          }
                        }
                        onChanged(newMap);
                      },
                    ),
                  ),
                  const SizedBox(width: AppSpacing.s8),
                  Expanded(
                    flex: 2,
                    child: I18nTextField(
                      label: 'Value',
                      initialData: entry.value,
                      onChanged: (newVal) {
                        final newMap = Map<String, I18nText>.from(map);
                        newMap[entry.key] = newVal;
                        onChanged(newMap);
                      },
                    ),
                  ),
                  IconButton(
                    icon: Icon(
                      Icons.delete_outline,
                      color: Theme.of(context).colorScheme.error,
                    ),
                    onPressed: () {
                      final newMap = Map<String, I18nText>.from(map);
                      newMap.remove(entry.key);
                      onChanged(newMap);
                    },
                  ),
                ],
              ),
            );
          }),
      ],
    );
  }
}
