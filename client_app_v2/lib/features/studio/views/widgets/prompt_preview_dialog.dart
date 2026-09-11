import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/features/studio/models/step_simulation.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

/// Pure formatting utilities for prompt and schema rendering.
class PromptPreviewFormatter {
  const PromptPreviewFormatter._();

  /// Formats strongly-typed LLM messages into clean, delimited text.
  static String formatMessages(List<LlmMessageDto> messages) {
    if (messages.isEmpty) return '';
    final buffer = StringBuffer();
    for (final msg in messages) {
      buffer.writeln('--- Role: ${msg.role} ---');
      buffer.writeln(msg.content);
      buffer.writeln();
    }
    return buffer.toString().trim();
  }

  /// Legacy adaptor for dynamic messages (used during transitions or raw maps).
  static String formatMessagesFromRaw(dynamic messages) {
    if (messages == null) return '';
    if (messages is List) {
      final buffer = StringBuffer();
      for (final msg in messages) {
        if (msg is Map) {
          final role = msg['role']?.toString();
          final content = msg['content'];
          if (role != null) {
            buffer.writeln('--- Role: $role ---');
          }
          if (content is String) {
            buffer.writeln(content);
          } else if (content != null) {
            buffer.writeln(const JsonEncoder.withIndent('  ').convert(content));
          }
          buffer.writeln();
        } else if (msg is LlmMessageDto) {
          buffer.writeln('--- Role: ${msg.role} ---');
          buffer.writeln(msg.content);
          buffer.writeln();
        } else {
          buffer.writeln(msg.toString());
        }
      }
      return buffer.toString().trim();
    }
    if (messages is Map) {
      return const JsonEncoder.withIndent('  ').convert(messages);
    }
    return messages.toString();
  }

  /// Formats raw tool/schema dynamic object or fallback string.
  static String formatSchema(dynamic tools, String? fallback) {
    if (tools != null) {
      if (tools is Map || tools is List) {
        return const JsonEncoder.withIndent('  ').convert(tools);
      }
      final s = tools.toString().trim();
      if (s.isNotEmpty) return s;
    }
    if (fallback != null && fallback.isNotEmpty) {
      return fallback;
    }
    return '';
  }
}

/// Public reusable 3-tab Prompt Preview Dialog.
class PromptPreviewDialog extends StatefulWidget {
  final String staticContent;
  final String dynamicContent;
  final String schemaContent;

  const PromptPreviewDialog({
    super.key,
    required this.staticContent,
    required this.dynamicContent,
    required this.schemaContent,
  });

  @override
  State<PromptPreviewDialog> createState() => _PromptPreviewDialogState();
}

class _PromptPreviewDialogState extends State<PromptPreviewDialog>
    with SingleTickerProviderStateMixin {
  late final TabController _tabController;
  Timer? _copyTimer;
  bool _isCopied = false;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
  }

  @override
  void dispose() {
    _copyTimer?.cancel();
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _copyActiveContent() async {
    final text = switch (_tabController.index) {
      0 => widget.staticContent,
      1 => widget.dynamicContent,
      2 => widget.schemaContent,
      _ => widget.schemaContent,
    };
    final copyText = text.isNotEmpty
        ? text
        : (widget.schemaContent.isNotEmpty
              ? widget.schemaContent
              : widget.staticContent);

    if (copyText.isEmpty) return;

    await Clipboard.setData(ClipboardData(text: copyText));
    if (!mounted) return;

    _copyTimer?.cancel();
    setState(() => _isCopied = true);
    _copyTimer = Timer(const Duration(seconds: 2), () {
      if (mounted) {
        setState(() => _isCopied = false);
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);

    return Dialog(
      insetPadding: AppSpacing.p16,
      child: ConstrainedBox(
        constraints: const BoxConstraints(
          minWidth: 600,
          maxWidth: 1000,
          minHeight: 500,
          maxHeight: 800,
        ),
        child: Scaffold(
          appBar: AppBar(
            title: Text(l10n.previewPromptTitle),
            leading: IconButton(
              icon: const Icon(Icons.close),
              onPressed: () => Navigator.of(context).pop(),
            ),
            actions: [
              TextButton.icon(
                onPressed: _copyActiveContent,
                icon: Icon(
                  _isCopied ? Icons.check : Icons.copy,
                  size: 18,
                  color: _isCopied ? theme.colorScheme.primary : null,
                ),
                label: Text(
                  _isCopied ? l10n.copiedToClipboard : l10n.copyToClipboardBtn,
                  style: TextStyle(
                    color: _isCopied ? theme.colorScheme.primary : null,
                  ),
                ),
              ),
              AppSpacing.w16,
            ],
            bottom: TabBar(
              controller: _tabController,
              isScrollable: true,
              tabs: [
                Tab(text: l10n.previewPromptStaticTab),
                Tab(text: l10n.previewPromptDynamicTab),
                Tab(text: l10n.previewPromptSchemaTab),
              ],
            ),
          ),
          body: TabBarView(
            controller: _tabController,
            children: [
              _buildContentPane(context, widget.staticContent),
              _buildContentPane(context, widget.dynamicContent),
              _buildContentPane(context, widget.schemaContent),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildContentPane(BuildContext context, String content) {
    final theme = Theme.of(context);
    return Padding(
      padding: AppSpacing.p16,
      child: Container(
        width: double.infinity,
        padding: AppSpacing.p16,
        decoration: BoxDecoration(
          color: theme.colorScheme.surfaceContainerLowest,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: theme.colorScheme.outlineVariant),
        ),
        child: content.isEmpty
            ? Center(
                child: Text(
                  '---',
                  style: theme.textTheme.bodyMedium?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                ),
              )
            : SingleChildScrollView(
                child: SelectableText(
                  content,
                  style: theme.textTheme.bodySmall?.copyWith(
                    fontFamily: 'monospace',
                    fontFamilyFallback: const ['Courier', 'Consolas'],
                  ),
                ),
              ),
      ),
    );
  }
}
