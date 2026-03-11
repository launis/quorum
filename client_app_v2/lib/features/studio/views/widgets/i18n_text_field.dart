import 'package:flutter/material.dart';

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

  @override
  void initState() {
    super.initState();
    _defaultLocale = widget.initialData['default_locale']?.toString() ?? 'fi';

    _translations = {};
    if (widget.initialData['translations'] is Map) {
      final t = widget.initialData['translations'] as Map;
      t.forEach((key, value) {
        _translations[key.toString()] = value.toString();
      });
    }

    _defaultController = TextEditingController(
      text: _translations[_defaultLocale] ?? '',
    );

    _defaultController.addListener(_emitChanges);
  }

  @override
  void didUpdateWidget(I18nTextField oldWidget) {
    super.didUpdateWidget(oldWidget);
    // Only update if the underlying default locale text genuinely changed from parent
    final newLocale = widget.initialData['default_locale']?.toString() ?? 'fi';
    final newTranslationsMap = widget.initialData['translations'];

    String newDefaultText = '';
    if (newTranslationsMap is Map) {
      newDefaultText = newTranslationsMap[newLocale]?.toString() ?? '';
    }

    if (oldWidget.initialData != widget.initialData) {
      _defaultLocale = newLocale;
      _translations.clear();
      if (newTranslationsMap is Map) {
        newTranslationsMap.forEach((key, value) {
          _translations[key.toString()] = value.toString();
        });
      }

      if (_defaultController.text != newDefaultText) {
        _defaultController.value = _defaultController.value.copyWith(
          text: newDefaultText,
          selection: TextSelection.collapsed(
            offset: newDefaultText.length,
          ), // Keep cursor cursor at the end
        );
      }
    }
  }

  @override
  void dispose() {
    _defaultController.removeListener(_emitChanges);
    _defaultController.dispose();
    super.dispose();
  }

  void _emitChanges() {
    if (_defaultController.text.isNotEmpty) {
      _translations[_defaultLocale] = _defaultController.text;
    } else {
      _translations.remove(_defaultLocale);
    }

    widget.onChanged({
      'default_locale': _defaultLocale,
      'translations': _translations,
    });
  }

  void _addTranslation(String langCode, String text) {
    if (langCode == _defaultLocale) {
      _defaultController.text = text;
    } else {
      setState(() {
        _translations[langCode] = text;
      });
      _emitChanges();
    }
  }

  void _removeTranslation(String langCode) {
    setState(() {
      _translations.remove(langCode);
    });
    _emitChanges();
  }

  void _showAddTranslationDialog() {
    final langController = TextEditingController();
    final textController = TextEditingController();

    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('Add Translation'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: langController,
                decoration: const InputDecoration(
                  labelText: 'Language Code (e.g., en, sv)',
                ),
                maxLength: 2,
              ),
              const SizedBox(height: 16),
              TextField(
                controller: textController,
                decoration: const InputDecoration(labelText: 'Translated Text'),
                maxLines: 3,
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('Cancel'),
            ),
            FilledButton(
              onPressed: () {
                if (langController.text.isNotEmpty &&
                    textController.text.isNotEmpty) {
                  _addTranslation(
                    langController.text.toLowerCase(),
                    textController.text,
                  );
                  Navigator.of(context).pop();
                }
              },
              child: const Text('Save'),
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
                  label: const Text('Add Translation'),
                ),
              ],
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _defaultController,
              decoration: InputDecoration(
                labelText:
                    'Default Form (${_defaultLocale.toUpperCase()} usually expected)',
                border: const OutlineInputBorder(),
                filled: true,
              ),
              maxLines: null,
            ),
            if (_translations.keys
                .where((k) => k != _defaultLocale)
                .isNotEmpty) ...[
              const SizedBox(height: 16),
              const Text(
                'Other Translations:',
                style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              ..._translations.entries
                  .where((entry) => entry.key != _defaultLocale)
                  .map((entry) {
                    return Padding(
                      padding: const EdgeInsets.only(bottom: 8.0),
                      child: Row(
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
                          const SizedBox(width: 12),
                          Expanded(child: Text(entry.value)),
                          IconButton(
                            icon: const Icon(
                              Icons.delete_outline,
                              size: 20,
                              color: Colors.red,
                            ),
                            onPressed: () => _removeTranslation(entry.key),
                          ),
                        ],
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
