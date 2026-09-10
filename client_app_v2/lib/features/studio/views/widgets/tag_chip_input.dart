import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

/// Desktop-class keyboard-first chip input with Dual-Shield FormField architecture.
/// Prevents uncommitted state loss on save or focus loss and enforces bounded chip layout.
class TagChipInput extends StatefulWidget {
  final List<String> initialTags;
  final ValueChanged<List<String>>? onChanged;
  final FormFieldSetter<List<String>>? onSaved;
  final FormFieldValidator<List<String>>? validator;
  final String? labelText;
  final String? helperText;
  final String? hintText;
  final bool enabled;

  const TagChipInput({
    super.key,
    this.initialTags = const [],
    this.onChanged,
    this.onSaved,
    this.validator,
    this.labelText,
    this.helperText,
    this.hintText,
    this.enabled = true,
  });

  @override
  State<TagChipInput> createState() => TagChipInputState();
}

class TagChipInputState extends State<TagChipInput> {
  late final TextEditingController _controller;
  late final FocusNode _focusNode;
  late List<String> _tags;
  String? _duplicateError;

  /// Public synchronous probe for uncommitted keystroke buffer.
  bool get hasPendingBuffer => _controller.text.trim().isNotEmpty;

  @override
  void initState() {
    super.initState();
    _tags = List<String>.from(widget.initialTags);
    _controller = TextEditingController();
    _focusNode = FocusNode();
    _focusNode.addListener(_handleFocusChange);
  }

  @override
  void didUpdateWidget(TagChipInput oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.initialTags != widget.initialTags) {
      _tags = List<String>.from(widget.initialTags);
    }
  }

  @override
  void dispose() {
    _focusNode.removeListener(_handleFocusChange);
    _focusNode.dispose();
    _controller.dispose();
    super.dispose();
  }

  void _handleFocusChange() {
    if (!_focusNode.hasFocus) {
      _commitPendingText();
    }
  }

  bool _commitPendingText([FormFieldState<List<String>>? field]) {
    final rawText = _controller.text;
    final token = rawText.replaceAll(',', '').trim();
    if (token.isEmpty) {
      _controller.clear();
      return true;
    }

    final l10n = AppLocalizations.of(context);
    final exists = _tags.any((t) => t.toLowerCase() == token.toLowerCase());
    if (exists) {
      setState(() {
        _duplicateError =
            l10n?.scaleAnchorDuplicateError ?? 'Keyword already added.';
      });
      return false;
    }

    setState(() {
      _tags.add(token);
      _duplicateError = null;
      _controller.clear();
    });

    field?.didChange(_tags);
    widget.onChanged?.call(List<String>.unmodifiable(_tags));
    return true;
  }

  void _removeTag(String tag, FormFieldState<List<String>>? field) {
    setState(() {
      _tags.remove(tag);
      _duplicateError = null;
    });
    field?.didChange(_tags);
    widget.onChanged?.call(List<String>.unmodifiable(_tags));
  }

  KeyEventResult _handleKeyEvent(
    FocusNode node,
    KeyEvent event,
    FormFieldState<List<String>> field,
  ) {
    if (event is KeyDownEvent &&
        event.logicalKey == LogicalKeyboardKey.backspace &&
        _controller.text.isEmpty &&
        _tags.isNotEmpty) {
      _removeTag(_tags.last, field);
      return KeyEventResult.handled;
    }
    return KeyEventResult.ignored;
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);

    return FormField<List<String>>(
      initialValue: _tags,
      onSaved: (value) {
        _commitPendingText();
        widget.onSaved?.call(_tags);
      },
      validator: (value) {
        final commitSuccess = _commitPendingText();
        if (!commitSuccess && _duplicateError != null) {
          return _duplicateError;
        }
        return widget.validator?.call(_tags);
      },
      builder: (field) {
        final errorText = _duplicateError ?? field.errorText;

        return InputDecorator(
          decoration: InputDecoration(
            labelText: widget.labelText,
            helperText: widget.helperText,
            errorText: errorText,
            border: const OutlineInputBorder(),
            contentPadding: const EdgeInsets.symmetric(
              horizontal: 12,
              vertical: 8,
            ),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              if (_tags.isNotEmpty)
                Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: Wrap(
                    spacing: AppSpacing.s8,
                    runSpacing: AppSpacing.s4,
                    children: _tags.map((tag) {
                      return Tooltip(
                        message: tag,
                        child: InputChip(
                          label: ConstrainedBox(
                            constraints: const BoxConstraints(maxWidth: 240),
                            child: Text(tag, overflow: TextOverflow.ellipsis),
                          ),
                          onDeleted: widget.enabled
                              ? () => _removeTag(tag, field)
                              : null,
                        ),
                      );
                    }).toList(),
                  ),
                ),
              Focus(
                onKeyEvent: (node, event) =>
                    _handleKeyEvent(node, event, field),
                child: TextField(
                  controller: _controller,
                  focusNode: _focusNode,
                  enabled: widget.enabled,
                  decoration: InputDecoration(
                    hintText:
                        widget.hintText ??
                        l10n?.scaleAnchorChipPlaceholder ??
                        'Type word and press Enter...',
                    isDense: true,
                    border: InputBorder.none,
                    contentPadding: EdgeInsets.zero,
                  ),
                  onChanged: (val) {
                    if (val.endsWith(',') && val.trim().length > 1) {
                      _commitPendingText(field);
                    }
                  },
                  onSubmitted: (_) {
                    _commitPendingText(field);
                    _focusNode.requestFocus();
                  },
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}
