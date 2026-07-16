import 'package:flutter/material.dart';
import 'dart:async';
import 'package:client_app/l10n/gen/app_localizations.dart';

import 'package:client_app/shared/models/i18n_text.dart';

/// **Dynaaminen I18n-syöttö**
///
/// A compound widget that captures a `default_locale` string alongside
/// an optional `translations` dictionary for multiple languages.
/// Emits pure `I18nText` representations adhering to the
/// Strict Freezed Pydantic-parity policy for the Admin Studio editing.
class I18nTextField extends StatefulWidget {
  final String label;
  final I18nText? initialData;
  final void Function(I18nText) onChanged;

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
  late FocusNode _defaultFocusNode;
  late Map<String, String> _translations;
  late String _defaultLocale;
  Timer? _debounceTimer;

  // Controllers for active inline translations
  late Map<String, TextEditingController> _translationControllers;
  late Map<String, FocusNode> _translationFocusNodes;

  @override
  void initState() {
    super.initState();
    _translations = {};
    _translationControllers = {};
    _translationFocusNodes = {};
    _defaultFocusNode = FocusNode();

    if (widget.initialData != null) {
      _defaultLocale = widget.initialData!.defaultLocale;
      final t = widget.initialData!.translations;
      t.forEach((key, value) {
        final langCode = key.toString();
        final text = value.toString();
        _translations[langCode] = text;

        if (langCode != _defaultLocale) {
          _setupTranslationController(langCode, text);
        }
      });
    } else {
      _defaultLocale = 'en';
    }

    _defaultController = TextEditingController(
      text: _translations[_defaultLocale] ?? '',
    );

    _defaultController.addListener(_onDefaultControllerChanged);
    _defaultFocusNode.addListener(() {
      if (!_defaultFocusNode.hasFocus) _forceEmit();
    });
  }

  void _setupTranslationController(String langCode, String text) {
    final ctrl = TextEditingController(text: text);
    final fn = FocusNode();
    ctrl.addListener(() => _onTranslationChanged(langCode, ctrl.text));
    fn.addListener(() {
      if (!fn.hasFocus) _forceEmit();
    });
    _translationControllers[langCode] = ctrl;
    _translationFocusNodes[langCode] = fn;
  }

  void _onDefaultControllerChanged() {
    _scheduleEmit();
  }

  void _onTranslationChanged(String langCode, String newText) {
    if (newText.isEmpty) {
      // Kept in map so user can type, cleared from emitting mapping later
      _translations[langCode] = '';
    } else {
      _translations[langCode] = newText;
    }
    _scheduleEmit();
  }

  void _scheduleEmit() {
    _debounceTimer?.cancel();
    _debounceTimer = Timer(const Duration(milliseconds: 600), () {
      _emitChangesSilent();
    });
  }

  void _forceEmit() {
    _debounceTimer?.cancel();
    _emitChangesSilent();
  }

  void _emitChangesSilent() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted) return;
      if (_defaultController.text.isNotEmpty) {
        _translations[_defaultLocale] = _defaultController.text;
      } else {
        _translations.remove(_defaultLocale);
      }

      // Clean up empty translations before sending
      final safeTranslations = Map<String, String>.from(_translations);
      safeTranslations.removeWhere((k, v) => v.isEmpty);

      widget.onChanged(
        I18nText(defaultLocale: _defaultLocale, translations: safeTranslations),
      );
    });
  }

  @override
  void didUpdateWidget(covariant I18nTextField oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.initialData != oldWidget.initialData) {
      final newLocale = widget.initialData?.defaultLocale ?? 'en';
      final newTranslationsStringMap = widget.initialData?.translations ?? {};
      String newDefaultText = newTranslationsStringMap[newLocale] ?? '';

      // Riverpod parent update
      _defaultLocale = newLocale;

      // Add missing ones from external updates
      for (final entry in newTranslationsStringMap.entries) {
        if (entry.key != _defaultLocale) {
          _translations[entry.key] = entry.value;
          if (!_translationControllers.containsKey(entry.key)) {
            _setupTranslationController(entry.key, entry.value);
          } else if (_translationControllers[entry.key]!.text != entry.value) {
            _translationControllers[entry.key]!
                .value = _translationControllers[entry.key]!.value.copyWith(
              text: entry.value,
              selection: TextSelection.collapsed(offset: entry.value.length),
            );
          }
        }
      }
      // Remove deleted ones externally
      final keysToRemove = _translationControllers.keys
          .where((k) => !newTranslationsStringMap.containsKey(k))
          .toList();
      for (final k in keysToRemove) {
        _translationControllers[k]?.dispose();
        _translationControllers.remove(k);
        _translationFocusNodes[k]?.dispose();
        _translationFocusNodes.remove(k);
        _translations.remove(k);
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
    _debounceTimer?.cancel();
    _defaultController.removeListener(_onDefaultControllerChanged);
    _defaultController.dispose();
    _defaultFocusNode.dispose();

    for (final ctrl in _translationControllers.values) {
      ctrl.dispose();
    }
    for (final fn in _translationFocusNodes.values) {
      fn.dispose();
    }

    super.dispose();
  }

  void _addTranslation(String langCode, String text) {
    if (langCode == _defaultLocale) {
      _defaultController.text = text;
    } else {
      setState(() {
        _translations[langCode] = text;
        if (!_translationControllers.containsKey(langCode)) {
          _setupTranslationController(langCode, text);
        } else {
          _translationControllers[langCode]!.text = text;
        }
      });
      _forceEmit();
    }
  }

  void _removeTranslation(String langCode) {
    setState(() {
      _translations.remove(langCode);
      _translationControllers[langCode]?.dispose();
      _translationControllers.remove(langCode);
      _translationFocusNodes[langCode]?.dispose();
      _translationFocusNodes.remove(langCode);
    });
    _forceEmit();
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
                  labelText: AppLocalizations.of(
                    context,
                  )!.i18nLanguageCodePlaceholder,
                ),
                maxLength: 2,
              ),
              const SizedBox(height: 16),
              Text(
                AppLocalizations.of(context)!.i18nLanguageCodeHelp,
                style: TextStyle(
                  fontSize: 12,
                  color: Theme.of(context).colorScheme.onSurfaceVariant,
                ),
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
                Expanded(
                  child: Text(
                    widget.label,
                    style: const TextStyle(fontWeight: FontWeight.bold),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                const SizedBox(width: 8),
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
              focusNode: _defaultFocusNode,
              decoration: InputDecoration(
                labelText: AppLocalizations.of(
                  context,
                )!.i18nDefaultFormLabel(_defaultLocale.toUpperCase()),
                border: const OutlineInputBorder(),
                filled: true,
                fillColor: Theme.of(context).colorScheme.surface,
              ),
              minLines: 1,
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
                                color: Theme.of(
                                  context,
                                ).colorScheme.primaryContainer,
                                borderRadius: BorderRadius.circular(4),
                              ),
                              child: Text(
                                entry.key.toUpperCase(),
                                style: TextStyle(
                                  fontSize: 12,
                                  fontWeight: FontWeight.bold,
                                  color: Theme.of(
                                    context,
                                  ).colorScheme.onPrimaryContainer,
                                ),
                              ),
                            ),
                            IconButton(
                              icon: Icon(
                                Icons.delete_outline,
                                size: 20,
                                color: Theme.of(context).colorScheme.error,
                              ),
                              onPressed: () => _removeTranslation(entry.key),
                              tooltip: AppLocalizations.of(
                                context,
                              )!.i18nDeleteTranslation,
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        TextField(
                          controller: entry.value,
                          focusNode: _translationFocusNodes[entry.key],
                          decoration: InputDecoration(
                            hintText: AppLocalizations.of(context)!
                                .i18nTranslateToPlaceholder(
                                  entry.key.toUpperCase(),
                                ),
                            border: InputBorder.none,
                            isDense: true,
                            contentPadding: EdgeInsets.zero,
                          ),
                          minLines: 1,
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
