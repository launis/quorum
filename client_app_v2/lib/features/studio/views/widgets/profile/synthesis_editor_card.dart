import 'package:flutter/material.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/studio/views/widgets/i18n_text_field.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

class SynthesisEditorCard extends StatelessWidget {
  final SynthesisConfigDTO? synthesis;
  final Function(SynthesisConfigDTO?) onChanged;
  final bool isGlobal;

  const SynthesisEditorCard({
    super.key,
    required this.synthesis,
    required this.onChanged,
    this.isGlobal = true,
  });

  @override
  Widget build(BuildContext context) {
    final syn = synthesis ?? const SynthesisConfigDTO();

    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(
        side: BorderSide(color: Theme.of(context).colorScheme.outlineVariant),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              AppLocalizations.of(context)!.synConfigTitle,
              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
            ),
            const Divider(),
            const SizedBox(height: 16),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                TextFormField(
                  initialValue: syn.systemPrompt ?? '',
                  maxLines: 4,
                  minLines: 2,
                  decoration: InputDecoration(
                    labelText:
                        'Järjestelmäkehote / Kognitiivinen suunnitelma (PAKOLLINEN ENGLANTI)',
                    border: OutlineInputBorder(
                      borderSide: BorderSide(
                        color: Theme.of(context).colorScheme.outlineVariant,
                      ),
                    ),
                    filled: true,
                    fillColor: Theme.of(context)
                        .colorScheme
                        .surfaceContainerHighest
                        .withValues(alpha: 0.2),
                  ),
                  onChanged: (val) {
                    onChanged(
                      syn.copyWith(
                        systemPrompt: val.trim().isEmpty ? null : val,
                      ),
                    );
                  },
                ),
                const SizedBox(height: 16),
                I18nTextField(
                  label: 'Osion Väliotsikko (Preamble Text)',
                  initialData: syn.preambleText,
                  onChanged: (val) {
                    if (val.translations.isEmpty) {
                      onChanged(syn.copyWith(preambleText: null));
                    } else {
                      onChanged(syn.copyWith(preambleText: val));
                    }
                  },
                ),
                const SizedBox(height: 6),
                Text(
                  AppLocalizations.of(context)!.adminAiDescriptionHint,
                  style: TextStyle(
                    color: Theme.of(context).colorScheme.error,
                    fontWeight: FontWeight.bold,
                    fontSize: 12,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  'BEST PRACTICE: Käytä englanninkielisiä komentosanoja (ROLE:, TASK:, RULE:, CONTEXT:). ÄLÄ KOSKAAN käännä näitä sanoja suomeksi ohjeen sisällä.',
                  style: TextStyle(
                    fontStyle: FontStyle.italic,
                    fontSize: 12,
                    color: Theme.of(context).colorScheme.onSurfaceVariant,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            TextFormField(
              initialValue: syn.lengthConstraint?.toString() ?? '',
              decoration: InputDecoration(
                labelText: AppLocalizations.of(context)!.synMaxLengthLabel,
                border: const OutlineInputBorder(),
                helperText: AppLocalizations.of(context)!.synMaxLengthHelper,
              ),
              keyboardType: TextInputType.number,
              onChanged: (val) {
                final parsed =
                    int.tryParse(val) ??
                    (val.isEmpty ? null : syn.lengthConstraint);
                onChanged(syn.copyWith(lengthConstraint: parsed));
              },
            ),
            const SizedBox(height: 16),
            SwitchListTile(
              title: Text(AppLocalizations.of(context)!.synEnablePii),
              subtitle: Text(AppLocalizations.of(context)!.synEnablePiiHelper),
              value: syn.enablePiiMasking,
              onChanged: (val) {
                onChanged(syn.copyWith(enablePiiMasking: val));
              },
            ),
            SwitchListTile(
              title: Text(AppLocalizations.of(context)!.synIncludeHistory),
              value:
                  syn.historicalContextMode ==
                  HistoricalContextMode.slidingWindow3,
              onChanged: (val) {
                onChanged(
                  syn.copyWith(
                    historicalContextMode: val
                        ? HistoricalContextMode.slidingWindow3
                        : HistoricalContextMode.disabled,
                  ),
                );
              },
            ),
            SwitchListTile(
              title: Text(AppLocalizations.of(context)!.synOmitEmpty),
              value: syn.omitEmptySections,
              onChanged: (val) {
                onChanged(syn.copyWith(omitEmptySections: val));
              },
            ),
            if (isGlobal) ...[
              const SizedBox(height: 16),
              Text(
                AppLocalizations.of(context)!.synAllowedExports,
                style: const TextStyle(fontWeight: FontWeight.w600),
              ),
              Wrap(
                spacing: 8.0,
                children: ['pdf', 'raw_json', 'docx'].map((exportType) {
                  final isSelected = syn.allowedExports.contains(exportType);
                  return FilterChip(
                    label: Text(exportType.toUpperCase()),
                    selected: isSelected,
                    onSelected: (bool selected) {
                      final exports = List<String>.from(syn.allowedExports);
                      if (selected) {
                        if (!exports.contains(exportType)) {
                          exports.add(exportType);
                        }
                      } else {
                        exports.remove(exportType);
                      }
                      onChanged(syn.copyWith(allowedExports: exports));
                    },
                  );
                }).toList(),
              ),
              const SizedBox(height: 16),
              const Text(
                'Näytettävät Sarakkeet (Visible Columns)',
                style: TextStyle(fontWeight: FontWeight.w600),
              ),
              const SizedBox(height: 8),
              ...[
                'label',
                'score',
                'distribution',
                'row_explanation',
                'quotes',
              ].map((col) {
                final String colTitle = switch (col) {
                  'label' => 'Otsikko (label)',
                  'score' => 'Pisteet (score)',
                  'distribution' => 'Jakauma (distribution)',
                  'row_explanation' => 'Selite (row_explanation)',
                  'quotes' => 'Lainaukset (quotes)',
                  _ => col,
                };
                return Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    CheckboxListTile(
                      title: Text(colTitle),
                      value: syn.matrixVisibleColumns.contains(col),
                      onChanged: (val) {
                        final masterOrder = [
                          'label',
                          'score',
                          'distribution',
                          'row_explanation',
                          'quotes',
                        ];
                        final list = List<String>.from(
                          syn.matrixVisibleColumns,
                        );
                        if (val == true) {
                          if (!list.contains(col)) list.add(col);
                        } else {
                          list.remove(col);
                        }
                        list.sort((a, b) {
                          final indexA = masterOrder.indexOf(a);
                          final indexB = masterOrder.indexOf(b);
                          if (indexA == -1 || indexB == -1) return 0;
                          return indexA.compareTo(indexB);
                        });
                        onChanged(syn.copyWith(matrixVisibleColumns: list));
                      },
                      controlAffinity: ListTileControlAffinity.leading,
                      dense: true,
                      contentPadding: EdgeInsets.zero,
                    ),
                    if (col == 'quotes' &&
                        syn.matrixVisibleColumns.contains(col))
                      Padding(
                        padding: const EdgeInsets.only(left: 32.0, bottom: 8.0),
                        child: Text(
                          '*(Tip: saves space by replacing the standard explanation)*',
                          style: TextStyle(
                            fontSize: 12,
                            fontStyle: FontStyle.italic,
                            color: Theme.of(
                              context,
                            ).colorScheme.onSurfaceVariant,
                          ),
                        ),
                      ),
                  ],
                );
              }),
            ],
          ],
        ),
      ),
    );
  }
}
