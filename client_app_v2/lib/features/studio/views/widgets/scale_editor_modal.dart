import 'package:flutter/material.dart';
import 'package:client_app/features/studio/views/widgets/i18n_text_field.dart';
import 'package:client_app/utils/safe_cast.dart';

class ScaleEditorModal extends StatefulWidget {
  final Map<String, dynamic> initialScale;

  const ScaleEditorModal({super.key, required this.initialScale});

  @override
  State<ScaleEditorModal> createState() => _ScaleEditorModalState();
}

class _ScaleEditorModalState extends State<ScaleEditorModal> {
  late Map<String, dynamic> _editableScale;

  @override
  void initState() {
    super.initState();
    // Deepish copy of the scale
    _editableScale = Map<String, dynamic>.from(widget.initialScale);
    if (_editableScale['claims'] == null) {
      _editableScale['claims'] = [];
    }
  }

  void _save() {
    Navigator.of(context).pop(_editableScale);
  }

  void _addClaim() {
    setState(() {
      final claims = SafeCast.safeList(_editableScale['claims']);
      claims.add({
        'label': {
          'default_locale': 'en',
          'translations': <String, dynamic>{'en': ''},
        },
        'ai_description': 'CRITICAL MANDATE: ',
      });
      _editableScale['claims'] = claims;
    });
  }

  void _removeClaim(int index) {
    setState(() {
      final claims = SafeCast.safeList(_editableScale['claims']);
      claims.removeAt(index);
      _editableScale['claims'] = claims;
    });
  }

  @override
  Widget build(BuildContext context) {
    final claims = SafeCast.safeList(_editableScale['claims']);

    return Dialog(
      insetPadding: const EdgeInsets.all(16),
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Edit Scale Grade'),
          leading: IconButton(
            icon: const Icon(Icons.close),
            onPressed: () => Navigator.of(context).pop(),
          ),
          actions: [
            FilledButton.icon(
              onPressed: _save,
              icon: const Icon(Icons.check),
              label: const Text('Apply'),
            ),
            const SizedBox(width: 8),
          ],
        ),
        body: SingleChildScrollView(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              TextFormField(
                initialValue: _editableScale['score']?.toString(),
                decoration: const InputDecoration(
                  labelText: 'Grade Score (int, e.g., 5)',
                  border: OutlineInputBorder(),
                ),
                keyboardType: TextInputType.number,
                onChanged: (val) {
                  _editableScale['score'] = int.tryParse(val) ?? 0;
                },
              ),
              const SizedBox(height: 16),
              I18nTextField(
                label: 'Grade Name (Optional, e.g. "Excellent")',
                initialData: SafeCast.safeMap(_editableScale['name']),
                onChanged: (val) {
                  _editableScale['name'] = val;
                },
              ),
              const SizedBox(height: 16),
              TextFormField(
                initialValue: SafeCast.safeString(_editableScale['ai_label']),
                decoration: const InputDecoration(
                  labelText: 'Grade AI Label (e.g. CATASTROPHIC FAILURE)',
                  border: OutlineInputBorder(),
                ),
                onChanged: (val) {
                  _editableScale['ai_label'] = val.trim();
                },
              ),
              const SizedBox(height: 16),
              TextFormField(
                initialValue: SafeCast.safeString(
                  _editableScale['ai_description'],
                ),
                decoration: const InputDecoration(
                  labelText: 'Grade AI Rules (Strict Evaluation Directives)',
                  border: OutlineInputBorder(),
                  alignLabelWithHint: true,
                ),
                maxLines: 6,
                onChanged: (val) {
                  _editableScale['ai_description'] = val.trim();
                },
              ),
              const SizedBox(height: 24),
              const Text(
                'Claims (Evaluative Guidelines)',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              ...claims.asMap().entries.map((entry) {
                final index = entry.key;
                final claim = SafeCast.safeMap(entry.value);
                final claimLabel = SafeCast.safeMap(
                  claim['label'] ??
                      {
                        'default_locale': 'en',
                        'translations': <String, dynamic>{'en': ''},
                      },
                );

                return Card(
                  margin: const EdgeInsets.only(bottom: 16.0),
                  color: Theme.of(context).colorScheme.surface,
                  child: Padding(
                    padding: const EdgeInsets.all(12.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              'Claim ${index + 1}',
                              style: const TextStyle(
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            IconButton(
                              icon: const Icon(Icons.delete, color: Colors.red),
                              onPressed: () => _removeClaim(index),
                              tooltip: 'Remove Claim',
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        TextFormField(
                          initialValue: SafeCast.safeString(
                            claim['ai_description'],
                          ),
                          decoration: const InputDecoration(
                            labelText: 'Claim AI Rule (MANDATORY ENGLISH)',
                            helperText:
                                "MUST be in English. Use strict commanding language (e.g., 'CRITICAL EVALUATION DIRECTIVE:').",
                            helperStyle: TextStyle(
                              color: Colors.red,
                              fontWeight: FontWeight.bold,
                            ),
                            border: OutlineInputBorder(),
                            alignLabelWithHint: true,
                          ),
                          maxLines: 3,
                          onChanged: (val) {
                            setState(() {
                              claim['ai_description'] = val;
                              claims[index] = claim;
                            });
                          },
                        ),
                        const SizedBox(height: 16),
                        I18nTextField(
                          label: 'Claim Translation (UI Screen/PDF)',
                          initialData: claimLabel,
                          onChanged: (val) {
                            setState(() {
                              claim['label'] = val;
                              claims[index] = claim;
                            });
                          },
                        ),
                      ],
                    ),
                  ),
                );
              }),
              const SizedBox(height: 8),
              Align(
                alignment: Alignment.centerLeft,
                child: OutlinedButton.icon(
                  onPressed: _addClaim,
                  icon: const Icon(Icons.add),
                  label: const Text('Add Claim'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
