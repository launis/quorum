import 'package:flutter/material.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

/// **Dynaaminen I18n-syöttö**
///
/// A compound widget that captures a `default_locale` string alongside
/// an optional `translations` dictionary for multiple languages.
/// Emits pure `Map<String, dynamic>` representations adhering to the
/// De-Generator Policy for the Admin Studio editing.
class I18nTextField extends StatefulWidget {
  final String label;
  final Map<String, dynamic> initialData;
  final ValueChanged<Map<String, dynamic>> onChanged;

  const I18nTextField({
    super.key,
    required this.label,
    required this.initialData,
    required this.onChanged,
  });

  @override
  State<I18nTextField> createState() => _I18nTextFieldState();
}

class _I18nTextFieldState extends State<I18nTextField> {
  late TextEditingController _defaultController;
  late Map<String, String> _translations;
  late String _defaultLocale;

  // Controllers for active inline translations
  late Map<String, TextEditingController> _translationControllers;

  @override
  void initState() {
    super.initState();
    _defaultLocale = widget.initialData['default_locale']?.toString() ?? 'en';

    _translations = {};
    _translationControllers = {};

    if (widget.initialData['translations'] is Map) {
      final t = widget.initialData['translations'] as Map;
      t.forEach((key, value) {
        final langCode = key.toString();
        final text = value.toString();
        _translations[langCode] = text;

        if (langCode != _defaultLocale) {
          final ctrl = TextEditingController(text: text);
          ctrl.addListener(() => _onTranslationChanged(langCode, ctrl.text));
          _translationControllers[langCode] = ctrl;
        }
      });
    }

    _defaultController = TextEditingController(
      text: _translations[_defaultLocale] ?? '',
    );

    _defaultController.addListener(_emitChanges);
  }

  void _onTranslationChanged(String langCode, String newText) {
    if (newText.isEmpty) {
      // Kept in map so user can type, cleared from emitting mapping later
      _translations[langCode] = '';
    } else {
      _translations[langCode] = newText;
    }
    _emitChangesSilent(); // Emit up DAG tree without resetting inputs
  }

  void _emitChangesSilent() {
    if (_defaultController.text.isNotEmpty) {
      _translations[_defaultLocale] = _defaultController.text;
    } else {
      _translations.remove(_defaultLocale);
    }

    // Clean up empty translations before sending
    final safeTranslations = Map<String, String>.from(_translations);
    safeTranslations.removeWhere((k, v) => v.isEmpty);

    widget.onChanged({
      'default_locale': _defaultLocale,
      'translations': safeTranslations,
    });
  }

  @override
  void didUpdateWidget(I18nTextField oldWidget) {
    super.didUpdateWidget(oldWidget);
    final newLocale = widget.initialData['default_locale']?.toString() ?? 'en';
    final newTranslationsMap = widget.initialData['translations'];

    String newDefaultText = '';
    if (newTranslationsMap is Map) {
      newDefaultText = newTranslationsMap[newLocale]?.toString() ?? '';
    }

    // Riverpod parent update
    if (oldWidget.initialData != widget.initialData) {
      _defaultLocale = newLocale;

      if (newTranslationsMap is Map) {
        final newMap = Map<String, String>.from(
          newTranslationsMap.map(
            (k, v) => MapEntry(k.toString(), v.toString()),
          ),
        );

        // Add missing ones from external updates
        for (final entry in newMap.entries) {
          if (entry.key != _defaultLocale) {
            _translations[entry.key] = entry.value;
            if (!_translationControllers.containsKey(entry.key)) {
              final ctrl = TextEditingController(text: entry.value);
              ctrl.addListener(
                () => _onTranslationChanged(entry.key, ctrl.text),
              );
              _translationControllers[entry.key] = ctrl;
            } else if (_translationControllers[entry.key]!.text !=
                entry.value) {
              _translationControllers[entry.key]!
                  .value = _translationControllers[entry.key]!.value.copyWith(
                text: entry.value,
                selection: TextSelection.collapsed(offset: entry.value.length),
              );
            }
          }
        }
        // Remove deleted ones externally
        final keysToRemove =
            _translationControllers.keys
                .where((k) => !newMap.containsKey(k))
                .toList();
        for (final k in keysToRemove) {
          _translationControllers[k]?.dispose();
          _translationControllers.remove(k);
          _translations.remove(k);
        }
      }

      if (_defaultController.text != newDefaultText) {
        _defaultController.value = _defaultController.value.copyWith(
          text: newDefaultText,
          selection: TextSelection.collapsed(offset: newDefaultText.length),
        );
      }
    }
  }

  @override
  void dispose() {
    _defaultController.removeListener(_emitChanges);
    _defaultController.dispose();

    for (final ctrl in _translationControllers.values) {
      ctrl.dispose();
    }

    super.dispose();
  }

  void _emitChanges() {
    _emitChangesSilent();
  }

  void _addTranslation(String langCode, String text) {
    if (langCode == _defaultLocale) {
      _defaultController.text = text;
    } else {
      setState(() {
        _translations[langCode] = text;
        if (!_translationControllers.containsKey(langCode)) {
          final ctrl = TextEditingController(text: text);
          ctrl.addListener(() => _onTranslationChanged(langCode, ctrl.text));
          _translationControllers[langCode] = ctrl;
        } else {
          _translationControllers[langCode]!.text = text;
        }
      });
      _emitChanges();
    }
  }

  void _removeTranslation(String langCode) {
    setState(() {
      _translations.remove(langCode);
      _translationControllers[langCode]?.dispose();
      _translationControllers.remove(langCode);
    });
    _emitChanges();
  }

  void _showAddTranslationDialog() {
    final langController = TextEditingController();

    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: Text(AppLocalizations.of(context)!.i18nAddLanguageVersion),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: langController,
                decoration: InputDecoration(
                  labelText:
                      AppLocalizations.of(context)!.i18nLanguageCodePlaceholder,
                ),
                maxLength: 2,
              ),
              const SizedBox(height: 16),
              Text(
                AppLocalizations.of(context)!.i18nLanguageCodeHelp,
                style: const TextStyle(fontSize: 12, color: Colors.grey),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: Text(AppLocalizations.of(context)!.i18nCancel),
            ),
            FilledButton(
              onPressed: () {
                if (langController.text.isNotEmpty) {
                  _addTranslation(langController.text.toLowerCase().trim(), '');
                  Navigator.of(context).pop();
                }
              },
              child: Text(AppLocalizations.of(context)!.i18nCreate),
            ),
          ],
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 0,
      color: Theme.of(context).colorScheme.surfaceContainerHighest,
      shape: RoundedRectangleBorder(
        side: BorderSide(color: Theme.of(context).colorScheme.outlineVariant),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  widget.label,
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
                TextButton.icon(
                  onPressed: _showAddTranslationDialog,
                  icon: const Icon(Icons.add_circle_outline, size: 16),
                  label: Text(AppLocalizations.of(context)!.i18nAddTranslation),
                ),
              ],
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _defaultController,
              decoration: InputDecoration(
                labelText: AppLocalizations.of(
                  context,
                )!.i18nDefaultFormLabel(_defaultLocale.toUpperCase()),
                border: const OutlineInputBorder(),
                filled: true,
                fillColor: Theme.of(context).colorScheme.surface,
              ),
              maxLines: null,
            ),
            if (_translationControllers.isNotEmpty) ...[
              const SizedBox(height: 16),
              Text(
                AppLocalizations.of(context)!.i18nOtherTranslations,
                style: const TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              ..._translationControllers.entries.map((entry) {
                return Padding(
                  padding: const EdgeInsets.only(bottom: 12.0),
                  child: Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Theme.of(context).colorScheme.surface,
                      border: Border.all(
                        color: Theme.of(context).colorScheme.outlineVariant,
                      ),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Container(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 8,
                                vertical: 4,
                              ),
                              decoration: BoxDecoration(
                                color:
                                    Theme.of(
                                      context,
                                    ).colorScheme.primaryContainer,
                                borderRadius: BorderRadius.circular(4),
                              ),
                              child: Text(
                                entry.key.toUpperCase(),
                                style: TextStyle(
                                  fontSize: 12,
                                  fontWeight: FontWeight.bold,
                                  color:
                                      Theme.of(
                                        context,
                                      ).colorScheme.onPrimaryContainer,
                                ),
                              ),
                            ),
                            IconButton(
                              icon: const Icon(
                                Icons.delete_outline,
                                size: 20,
                                color: Colors.red,
                              ),
                              onPressed: () => _removeTranslation(entry.key),
                              tooltip:
                                  AppLocalizations.of(
                                    context,
                                  )!.i18nDeleteTranslation,
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        TextField(
                          controller: entry.value,
                          decoration: InputDecoration(
                            hintText: AppLocalizations.of(
                              context,
                            )!.i18nTranslateToPlaceholder(
                              entry.key.toUpperCase(),
                            ),
                            border: InputBorder.none,
                            isDense: true,
                            contentPadding: EdgeInsets.zero,
                          ),
                          maxLines: null,
                        ),
                      ],
                    ),
                  ),
                );
              }),
            ],
          ],
        ),
      ),
    );
  }
}
