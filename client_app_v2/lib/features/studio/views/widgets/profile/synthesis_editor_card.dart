import 'package:flutter/material.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/views/widgets/i18n_text_field.dart';

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
            const Text(
              "Synthesis & Export Configuration",
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
            ),
            const Divider(),
            const SizedBox(height: 16),
            I18nTextField(
              label: "Preamble Text",
              initialData: syn.preambleText,
              onChanged: (val) {
                onChanged(syn.copyWith(preambleText: val));
              },
            ),
            const SizedBox(height: 16),
            TextFormField(
              initialValue: syn.lengthConstraint?.toString() ?? '',
              decoration: const InputDecoration(
                labelText: "Max Length Constraint",
                border: OutlineInputBorder(),
                helperText: "Leave empty for no limit",
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
              title: const Text("Enable PII Masking"),
              subtitle: const Text("Ensure PII is masked before LLM call"),
              value: syn.enablePiiMasking,
              onChanged: (val) {
                onChanged(syn.copyWith(enablePiiMasking: val));
              },
            ),
            SwitchListTile(
              title: const Text("Include Historical Summary"),
              value: syn.includeHistoricalSummary,
              onChanged: (val) {
                onChanged(syn.copyWith(includeHistoricalSummary: val));
              },
            ),
            SwitchListTile(
              title: const Text("Omit Empty Sections"),
              value: syn.omitEmptySections,
              onChanged: (val) {
                onChanged(syn.copyWith(omitEmptySections: val));
              },
            ),
            const SizedBox(height: 16),
            const Text(
              "Allowed Exports",
              style: TextStyle(fontWeight: FontWeight.w600),
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
