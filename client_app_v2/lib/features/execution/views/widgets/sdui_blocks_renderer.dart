import 'package:flutter/material.dart';
import 'package:client_app/shared/models/sdui_block_dto.dart';
import 'package:client_app/shared/widgets/output_renderer.dart';

class SduiBlocksRenderer extends StatelessWidget {
  final List<SduiBlockDTO> blocks;

  const SduiBlocksRenderer({super.key, required this.blocks});

  @override
  Widget build(BuildContext context) {
    if (blocks.isEmpty) return const SizedBox.shrink();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      mainAxisSize: MainAxisSize.min,
      children: blocks.map((block) {
        String? text;
        if (block is SduiMarkdownBlock) {
          text = block.text;
        } else if (block is SduiParagraphBlock) {
          text = block.text;
        }

        if (text != null && text.isNotEmpty) {
          return Padding(
            padding: const EdgeInsets.only(bottom: 8.0),
            child: OutputRenderer(markdownContent: text),
          );
        }
        return const SizedBox.shrink();
      }).toList(),
    );
  }
}
