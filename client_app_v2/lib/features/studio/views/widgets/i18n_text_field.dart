import 'package:flutter/material.dart';
import 'dart:async';
import 'package:client_app/l10n/gen/app_localizations.dart';

import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/shared/models/i18n_text.dart';

/// **Dynamic I18n Input**
///
/// A compound widget that captures translations dictionary for multiple languages.
/// Emits pure `I18nText` representations adhering to the
/// Strict Freezed Pydantic-parity policy for Admin Studio editing.
class I18nTextField extends StatefulWidget {
  final String label;
  final I18nText? initialData;
  final void Function(I18nText) onChanged;
  final Widget? leadingInput;
  final Widget? bottomInput;

  const I18nTextField({
    super.key,
    required this.label,
    required this.initialData,
    required this.onChanged,
    this.leadingInput,
    this.bottomInput,
  });

  @override
  State<I18nTextField> createState() => _I18nTextFieldState();
}

class _I18nTextFieldState extends State<I18nTextField> {
  late TextEditingController _defaultController;
  late FocusNode _defaultFocusNode;
  late Map<String, String> _translations;
  Timer? _debounceTimer;

  // Controllers for active inline translations
  late Map<String, TextEditingController> _translationControllers;
  late Map<String, FocusNode> _translationFocusNodes;
  late Map<String, VoidCallback> _translationFocusListeners;

  @override
  void initState() {
    super.initState();
    _translations = {};
    _translationControllers = {};
    _translationFocusNodes = {};
    _translationFocusListeners = {};
    _defaultFocusNode = FocusNode();

    if (widget.initialData != null) {
      final t = widget.initialData!.translations;
      t.forEach((key, value) {
        final langCode = key.toString();
        final text = value.toString();
        _translations[langCode] = text;

        if (langCode != 'en') {
          _setupTranslationController(langCode, text);
        }
      });
    }

    _defaultController = TextEditingController(text: _translations['en'] ?? '');

    _defaultController.addListener(_onDefaultControllerChanged);
    _defaultFocusNode.addListener(_onDefaultFocusChange);
  }

  void _onDefaultFocusChange() {
    if (!_defaultFocusNode.hasFocus) _forceEmit();
  }

  void _setupTranslationController(String langCode, String text) {
    final ctrl = TextEditingController(text: text);
    final fn = FocusNode();
    ctrl.addListener(() => _onTranslationChanged(langCode, ctrl.text));

    void listener() {
      if (!fn.hasFocus) _forceEmit();
    }

    fn.addListener(listener);

    _translationControllers[langCode] = ctrl;
    _translationFocusNodes[langCode] = fn;
    _translationFocusListeners[langCode] = listener;
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
        _translations['en'] = _defaultController.text;
      } else {
        _translations.remove('en');
      }

      // Clean up empty translations before sending
      final safeTranslations = Map<String, String>.from(_translations);
      safeTranslations.removeWhere((k, v) => v.isEmpty);

      widget.onChanged(I18nText(translations: safeTranslations));
    });
  }

  @override
  void didUpdateWidget(covariant I18nTextField oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.initialData != oldWidget.initialData) {
      final newTranslationsStringMap = widget.initialData?.translations ?? {};
      final String newDefaultText = newTranslationsStringMap['en'] ?? '';

      // Add missing ones from external updates
      for (final entry in newTranslationsStringMap.entries) {
        if (entry.key != 'en') {
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
        final fn = _translationFocusNodes[k];
        final listener = _translationFocusListeners[k];
        if (fn != null) {
          if (listener != null) fn.removeListener(listener);
          if (fn.hasFocus) fn.unfocus();
          fn.dispose();
        }
        _translationFocusNodes.remove(k);
        _translationFocusListeners.remove(k);
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
    _defaultFocusNode.removeListener(_onDefaultFocusChange);

    if (_defaultFocusNode.hasFocus) _defaultFocusNode.unfocus();

    _defaultController.dispose();
    _defaultFocusNode.dispose();

    for (final ctrl in _translationControllers.values) {
      ctrl.dispose();
    }
    for (final entry in _translationFocusNodes.entries) {
      final key = entry.key;
      final fn = entry.value;
      final listener = _translationFocusListeners[key];
      if (listener != null) fn.removeListener(listener);
      if (fn.hasFocus) fn.unfocus();
      fn.dispose();
    }

    super.dispose();
  }

  void _addTranslation(String langCode, String text) {
    if (langCode == 'en') {
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
      final fn = _translationFocusNodes[langCode];
      final listener = _translationFocusListeners[langCode];
      if (fn != null) {
        if (listener != null) fn.removeListener(listener);
        if (fn.hasFocus) fn.unfocus();
        fn.dispose();
      }
      _translationFocusNodes.remove(langCode);
      _translationFocusListeners.remove(langCode);
    });
    _forceEmit();
  }

  void _showAddTranslationDialog() {
    final langController = TextEditingController();

    showDialog<void>(
      context: context,
      builder: (context) {
        final theme = Theme.of(context);
        final l10n = AppLocalizations.of(context)!;
        return AlertDialog(
          title: Text(l10n.i18nAddLanguageVersion),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: langController,
                decoration: InputDecoration(
                  labelText: l10n.i18nLanguageCodePlaceholder,
                ),
                maxLength: 2,
              ),
              AppSpacing.h16,
              Text(
                l10n.i18nLanguageCodeHelp,
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
            ],
          ),
          actions: [
            TextButton(
              style: TextButton.styleFrom(
                enabledMouseCursor: SystemMouseCursors.click,
              ),
              onPressed: () => Navigator.of(context).pop(),
              child: Text(l10n.i18nCancel),
            ),
            FilledButton(
              style: FilledButton.styleFrom(
                enabledMouseCursor: SystemMouseCursors.click,
              ),
              onPressed: () {
                final normalizedCode = langController.text.toLowerCase().trim();
                if (normalizedCode.isNotEmpty) {
                  _addTranslation(normalizedCode, '');
                  Navigator.of(context).pop();
                }
              },
              child: Text(l10n.i18nCreate),
            ),
          ],
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final l10n = AppLocalizations.of(context)!;

    return Card(
      elevation: 0,
      color: theme.colorScheme.surfaceContainerHighest,
      shape: RoundedRectangleBorder(
        side: BorderSide(color: theme.colorScheme.outlineVariant),
        borderRadius: BorderRadius.circular(AppSpacing.s12),
      ),
      child: Padding(
        padding: AppSpacing.p16,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Text(
                    widget.label,
                    style: theme.textTheme.bodyMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                AppSpacing.w8,
                Flexible(
                  child: TextButton.icon(
                    style: TextButton.styleFrom(
                      enabledMouseCursor: SystemMouseCursors.click,
                    ),
                    onPressed: _showAddTranslationDialog,
                    icon: const Icon(
                      Icons.add_circle_outline,
                      size: AppSpacing.s16,
                    ),
                    label: Text(
                      l10n.i18nAddTranslation,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ),
              ],
            ),
            AppSpacing.h12,
            if (widget.leadingInput != null)
              LayoutBuilder(
                builder: (context, constraints) {
                  final isNarrow = constraints.maxWidth < 400;
                  final defaultField = TextField(
                    controller: _defaultController,
                    focusNode: _defaultFocusNode,
                    decoration: InputDecoration(
                      labelText: l10n.i18nDefaultFormLabel('EN'),
                      border: const OutlineInputBorder(),
                      filled: true,
                      fillColor: theme.colorScheme.surface,
                    ),
                    minLines: 1,
                    maxLines: null,
                  );

                  if (isNarrow) {
                    return Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        widget.leadingInput!,
                        AppSpacing.h8,
                        defaultField,
                      ],
                    );
                  }

                  return Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      widget.leadingInput!,
                      AppSpacing.w12,
                      Expanded(child: defaultField),
                    ],
                  );
                },
              )
            else
              TextField(
                controller: _defaultController,
                focusNode: _defaultFocusNode,
                decoration: InputDecoration(
                  labelText: l10n.i18nDefaultFormLabel('EN'),
                  border: const OutlineInputBorder(),
                  filled: true,
                  fillColor: theme.colorScheme.surface,
                ),
                minLines: 1,
                maxLines: null,
              ),
            if (_translationControllers.isNotEmpty) ...[
              AppSpacing.h16,
              Text(
                l10n.i18nOtherTranslations,
                style: theme.textTheme.bodySmall?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
                overflow: TextOverflow.ellipsis,
              ),
              AppSpacing.h8,
              ..._translationControllers.entries.map((entry) {
                return Padding(
                  padding: const EdgeInsets.only(bottom: AppSpacing.s12),
                  child: Container(
                    padding: AppSpacing.p12,
                    decoration: BoxDecoration(
                      color: theme.colorScheme.surface,
                      border: Border.all(
                        color: theme.colorScheme.outlineVariant,
                      ),
                      borderRadius: BorderRadius.circular(AppSpacing.s8),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Flexible(
                              child: Container(
                                padding: const EdgeInsets.symmetric(
                                  horizontal: AppSpacing.s8,
                                  vertical: AppSpacing.s4,
                                ),
                                decoration: BoxDecoration(
                                  color: theme.colorScheme.primaryContainer,
                                  borderRadius: BorderRadius.circular(
                                    AppSpacing.s4,
                                  ),
                                ),
                                child: Text(
                                  entry.key.toUpperCase(),
                                  style: theme.textTheme.bodySmall?.copyWith(
                                    fontWeight: FontWeight.bold,
                                    color: theme.colorScheme.onPrimaryContainer,
                                  ),
                                  overflow: TextOverflow.ellipsis,
                                ),
                              ),
                            ),
                            IconButton(
                              mouseCursor: SystemMouseCursors.click,
                              icon: Icon(
                                Icons.delete_outline,
                                size: AppSpacing.s16,
                                color: theme.colorScheme.error,
                              ),
                              onPressed: () => _removeTranslation(entry.key),
                              tooltip: l10n.i18nDeleteTranslation,
                            ),
                          ],
                        ),
                        AppSpacing.h8,
                        TextField(
                          controller: entry.value,
                          focusNode: _translationFocusNodes[entry.key],
                          decoration: InputDecoration(
                            hintText: l10n.i18nTranslateToPlaceholder(
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
            if (widget.bottomInput != null) ...[
              AppSpacing.h16,
              SizedBox(width: double.infinity, child: widget.bottomInput!),
            ],
          ],
        ),
      ),
    );
  }
}
