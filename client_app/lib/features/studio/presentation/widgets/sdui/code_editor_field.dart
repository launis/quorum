import 'package:flutter/material.dart';

/// **CodeEditorField**
/// 
/// A specialized text field for editing code snippets.
/// Features:
/// - Monospaced font
/// - Darker background
/// - Expands vertically
class CodeEditorField extends StatelessWidget {
  final String label;
  final String? initialValue;
  final ValueChanged<String> onChanged;

  const CodeEditorField({
    super.key,
    required this.label,
    this.initialValue,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    // Basic syntax highlighting or smarter editing could be added here.
    // For now, it's a styled TextFormField.
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (label.isNotEmpty)
          Padding(
            padding: const EdgeInsets.only(bottom: 8.0),
            child: Text(label, style: Theme.of(context).textTheme.labelMedium),
          ),
        TextFormField(
          initialValue: initialValue,
          maxLines: null, // Expands
          minLines: 5,
          style: const TextStyle(
            fontFamily: 'Courier New', // Fallback mono
            fontFamilyFallback: ['monospace', 'Courier'],
             // In a real app we might use GoogleFonts.robotoMono() via dependency
          ),
          decoration: const InputDecoration(
            filled: true,
            // We rely on Theme for actual colors, but can hint opacity
            fillColor: Color(0xFF1E1E1E), // Dark background override usually desired for code
            border: OutlineInputBorder(),
          ),
          onChanged: onChanged,
        ),
      ],
    );
  }
}
