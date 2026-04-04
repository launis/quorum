import 'package:flutter/material.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/views/widgets/i18n_text_field.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

class SynthesisEditorCard extends StatelessWidget {
  final SynthesisConfigDTO? synthesis;
  final Function(SynthesisConfigDTO?) onChanged;

  const SynthesisEditorCard({
    super.key,
    required this.synthesis,
    required this.onChanged,
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
            I18nTextField(
              label: AppLocalizations.of(context)!.synPreambleLabel,
              initialData: syn.preambleText,
              onChanged: (val) {
                final isEmpty =
                    val.translations.isEmpty ||
                    val.translations.values.every((v) => v.trim().isEmpty);
                onChanged(syn.copyWith(preambleText: isEmpty ? null : val));
              },
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
              value: syn.includeHistoricalSummary,
              onChanged: (val) {
                onChanged(syn.copyWith(includeHistoricalSummary: val));
              },
            ),
            SwitchListTile(
              title: Text(AppLocalizations.of(context)!.synOmitEmpty),
              value: syn.omitEmptySections,
              onChanged: (val) {
                onChanged(syn.copyWith(omitEmptySections: val));
              },
            ),
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
          ],
        ),
      ),
    );
  }
}
