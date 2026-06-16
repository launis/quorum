import 'package:flutter/material.dart';
import 'package:flutter_markdown_plus/flutter_markdown_plus.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

class OutputRenderer extends StatelessWidget {
  final String markdownContent;

  const OutputRenderer({super.key, required this.markdownContent});

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    String renderedContent = markdownContent;

    if (l10n != null) {
      renderedContent = renderedContent
          .replaceAll('ROLE_ARCHITECT', l10n.roleArchitect)
          .replaceAll('ROLE_DRIVER', l10n.roleDriver)
          .replaceAll('ROLE_NAVIGATOR', l10n.roleNavigator)
          .replaceAll('ROLE_PASSENGER', l10n.rolePassenger);
    }

    // Clean up possible HTML <br> tags coming from raw text extractions
    renderedContent = renderedContent.replaceAll(
      RegExp(r'<br\s*\/?>', caseSensitive: false),
      ' ',
    );

    return MarkdownBody(
      data: renderedContent,
      selectable: true,
      styleSheet: MarkdownStyleSheet(
        h1: Theme.of(
          context,
        ).textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.bold),
        h2: Theme.of(
          context,
        ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
        p: Theme.of(context).textTheme.bodyMedium?.copyWith(height: 1.5),
        code: const TextStyle(
          backgroundColor: Color(0xFFEEEEEE),
          fontFamily: 'monospace',
        ),
        codeblockDecoration: BoxDecoration(
          color: const Color(0xFFEEEEEE),
          borderRadius: BorderRadius.circular(4),
        ),
        blockquote: Theme.of(context).textTheme.bodyMedium?.copyWith(
          fontStyle: FontStyle.italic,
          color: Colors.grey[700],
        ),
        blockquoteDecoration: BoxDecoration(
          border: Border(
            left: BorderSide(color: Theme.of(context).primaryColor, width: 4.0),
          ),
          color: Colors.grey[50],
        ),
        blockquotePadding: const EdgeInsets.symmetric(
          horizontal: 16.0,
          vertical: 8.0,
        ),
        listBullet: Theme.of(context).textTheme.bodyMedium,
        listIndent: 24.0,
        tableBorder: TableBorder.all(color: Colors.grey[300]!),
        tableHead: Theme.of(
          context,
        ).textTheme.bodyMedium?.copyWith(fontWeight: FontWeight.bold),
        tableBody: Theme.of(context).textTheme.bodyMedium,
      ),
    );
  }
}
