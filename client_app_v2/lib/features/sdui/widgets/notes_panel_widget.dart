import 'package:flutter/material.dart';
import 'package:flutter_markdown_plus/flutter_markdown_plus.dart';

/// Render a structured markdown justification block array.
class NotesPanelWidget extends StatelessWidget {
  final Map<String, String> notes;
  final String locale;

  const NotesPanelWidget({
    super.key,
    required this.notes,
    required this.locale,
  });

  @override
  Widget build(BuildContext context) {
    if (notes.isEmpty) return const SizedBox.shrink();

    return Container(
      margin: const EdgeInsets.only(top: 16.0),
      clipBehavior: Clip.antiAlias,
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: const [
          BoxShadow(
            color: Colors.black12,
            blurRadius: 10,
            offset: Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
            decoration: const BoxDecoration(
              color: Color(0xFFF5F5F7),
              border: Border(bottom: BorderSide(color: Colors.black12)),
            ),
            child: Row(
              children: const [Icon(Icons.notes, color: Color(0xFF424242))],
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(20.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children:
                  notes.entries.map((entry) {
                    return Padding(
                      padding: const EdgeInsets.only(bottom: 24.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            entry.key, // Node / Edge ID
                            style: const TextStyle(
                              fontSize: 14,
                              fontWeight: FontWeight.bold,
                              color: Color(0xFF1976D2),
                            ),
                          ),
                          const SizedBox(height: 8),
                          // Markdown content rendered natively
                          MarkdownBody(
                            data: entry.value,
                            styleSheet: MarkdownStyleSheet(
                              p: const TextStyle(
                                fontSize: 14,
                                height: 1.6,
                                color: Color(0xFF333333),
                              ),
                              listBullet: const TextStyle(
                                color: Color(0xFF333333),
                              ),
                            ),
                          ),
                        ],
                      ),
                    );
                  }).toList(),
            ),
          ),
        ],
      ),
    );
  }
}
