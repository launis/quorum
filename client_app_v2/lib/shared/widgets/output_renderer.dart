import 'package:flutter/material.dart';
import 'package:flutter_markdown_plus/flutter_markdown_plus.dart';

class OutputRenderer extends StatelessWidget {
  final String markdownContent;

  const OutputRenderer({super.key, required this.markdownContent});

  @override
  Widget build(BuildContext context) {
    return MarkdownBody(
      data: markdownContent,
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
      ),
    );
  }
}
