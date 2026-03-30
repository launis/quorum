import 'package:flutter/material.dart';
import 'package:client_app/features/studio/views/widgets/i18n_text_field.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

class ScaleEditorModal extends StatefulWidget {
  final MatrixScale initialScale;

  const ScaleEditorModal({super.key, required this.initialScale});

  @override
  State<ScaleEditorModal> createState() => _ScaleEditorModalState();
}

class _ScaleEditorModalState extends State<ScaleEditorModal> {
  late MatrixScale _editableScale;

  @override
  void initState() {
    super.initState();
    _editableScale = widget.initialScale.copyWith();
  }

  void _save() {
    Navigator.of(context).pop(_editableScale);
  }

  void _addClaim() {
    setState(() {
      final claims = List<MatrixClaim>.from(_editableScale.claims);
      claims.add(
        const MatrixClaim(
          label: I18nText(defaultLocale: 'en', translations: {'en': ''}),
          aiDescription: 'CRITICAL MANDATE: ',
        ),
      );
      _editableScale = _editableScale.copyWith(claims: claims);
    });
  }

  void _removeClaim(int index) {
    setState(() {
      final claims = List<MatrixClaim>.from(_editableScale.claims);
      claims.removeAt(index);
      _editableScale = _editableScale.copyWith(claims: claims);
    });
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final claims = _editableScale.claims;

    return Dialog(
      insetPadding: const EdgeInsets.all(16),
      child: Scaffold(
        appBar: AppBar(
          title: Text(l10n.editDimension),
          leading: IconButton(
            icon: const Icon(Icons.close),
            onPressed: () => Navigator.of(context).pop(),
          ),
          actions: [
            FilledButton.icon(
              onPressed: _save,
              icon: const Icon(Icons.check),
              label: Text(l10n.save),
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
                initialValue: _editableScale.score.toString(),
                decoration: const InputDecoration(
                  labelText: 'Grade Score (int, e.g., 5)',
                  border: OutlineInputBorder(),
                ),
                keyboardType: TextInputType.number,
                onChanged: (val) {
                  final parsed = int.tryParse(val);
                  if (parsed != null) {
                    _editableScale = _editableScale.copyWith(score: parsed);
                  }
                },
              ),
              const SizedBox(height: 16),
              I18nTextField(
                label: 'Grade Name (Optional, e.g. "Excellent")',
                initialData:
                    _editableScale.name ??
                    const I18nText(
                      defaultLocale: 'en',
                      translations: {'en': ''},
                    ),
                onChanged: (val) {
                  _editableScale = _editableScale.copyWith(name: val);
                },
              ),
              const SizedBox(height: 16),
              TextFormField(
                initialValue: _editableScale.aiLabel,
                decoration: const InputDecoration(
                  labelText: 'Grade AI Label (e.g. CATASTROPHIC FAILURE)',
                  border: OutlineInputBorder(),
                ),
                onChanged: (val) {
                  _editableScale = _editableScale.copyWith(aiLabel: val.trim());
                },
              ),
              const SizedBox(height: 16),
              const Text(
                'Claims (Evaluative Guidelines)',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              ...claims.asMap().entries.map((entry) {
                final index = entry.key;
                final claim = entry.value;

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
                              icon: Icon(
                                Icons.delete,
                                color: Theme.of(context).colorScheme.error,
                              ),
                              onPressed: () => _removeClaim(index),
                              tooltip: 'Remove Claim',
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        TextFormField(
                          initialValue: claim.aiDescription,
                          decoration: InputDecoration(
                            labelText: 'Claim AI Rule (MANDATORY ENGLISH)',
                            helperText:
                                "MUST be in English. Use strict commanding language (e.g., 'CRITICAL EVALUATION DIRECTIVE:').",
                            helperStyle: TextStyle(
                              color: Theme.of(context).colorScheme.error,
                              fontWeight: FontWeight.bold,
                            ),
                            border: const OutlineInputBorder(),
                            alignLabelWithHint: true,
                          ),
                          maxLines: 3,
                          onChanged: (val) {
                            setState(() {
                              final newClaims = List<MatrixClaim>.from(
                                _editableScale.claims,
                              );
                              newClaims[index] = claim.copyWith(
                                aiDescription: val,
                              );
                              _editableScale = _editableScale.copyWith(
                                claims: newClaims,
                              );
                            });
                          },
                        ),
                        const SizedBox(height: 16),
                        I18nTextField(
                          label: 'Claim Translation (UI Screen/PDF)',
                          initialData: claim.label,
                          onChanged: (val) {
                            setState(() {
                              final newClaims = List<MatrixClaim>.from(
                                _editableScale.claims,
                              );
                              newClaims[index] = claim.copyWith(label: val);
                              _editableScale = _editableScale.copyWith(
                                claims: newClaims,
                              );
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
                  label: Text(l10n.matrixAddCriterion),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
