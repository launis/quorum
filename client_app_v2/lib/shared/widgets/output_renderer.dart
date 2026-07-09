import 'package:flutter/material.dart';
import 'package:flutter_markdown_plus/flutter_markdown_plus.dart';

class OutputRenderer extends StatelessWidget {
  final String markdownContent;

  const OutputRenderer({super.key, required this.markdownContent});

  @override
  Widget build(BuildContext context) {
    String renderedContent = markdownContent;

    // Backend now provides translated roles, so no dynamic replacement is needed here
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
