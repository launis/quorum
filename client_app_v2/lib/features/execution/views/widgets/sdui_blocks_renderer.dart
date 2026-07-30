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
        if (block is SduiAccordionBlock) {
          return _buildAccordion(context, block);
        }
        if (block is SduiHeaderBlock) {
          return _buildHeader(context, block);
        }

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

  Widget _buildAccordion(BuildContext context, SduiAccordionBlock block) {
    Color headerColor;
    Color bgColor;
    IconData? icon;

    switch (block.severity) {
      case 'success':
        headerColor = Colors.green.shade800;
        bgColor = Colors.green.shade50;
        icon = Icons.build;
        break;
      case 'warning':
        headerColor = Colors.orange.shade800;
        bgColor = Colors.orange.shade50;
        icon = Icons.warning;
        break;
      case 'error':
        headerColor = Colors.red.shade800;
        bgColor = Colors.red.shade50;
        icon = Icons.error;
        break;
      case 'info':
      default:
        headerColor = Colors.blue.shade800;
        bgColor = Colors.blue.shade50;
        icon = Icons.info;
        break;
    }

    if (block.iconName == 'lightbulb') icon = Icons.lightbulb;
    if (block.iconName == 'balance') icon = Icons.balance;

    return Card(
      elevation: 2,
      margin: const EdgeInsets.symmetric(vertical: 8.0),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
      color: bgColor,
      child: ExpansionTile(
        initiallyExpanded: true,
        leading: Icon(icon, color: headerColor),
        title: Text(
          block.title,
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            color: headerColor,
          ),
        ),
        children: [
          Container(
            color: Colors.white,
            padding: const EdgeInsets.all(12.0),
            child: SduiBlocksRenderer(blocks: block.children),
          ),
        ],
      ),
    );
  }

  Widget _buildHeader(BuildContext context, SduiHeaderBlock block) {
    return Card(
      elevation: 2,
      margin: const EdgeInsets.symmetric(vertical: 16.0),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: const BorderSide(color: Colors.green, width: 2),
      ),
      color: Colors.grey.shade50,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              block.title,
              style: Theme.of(
                context,
              ).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 12),
            if (block.badges.isNotEmpty)
              Wrap(
                alignment: WrapAlignment.center,
                spacing: 8,
                runSpacing: 8,
                children: block.badges
                    .map(
                      (b) => Chip(
                        label: Text(
                          b,
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 12,
                            color: Colors.indigo,
                          ),
                        ),
                        backgroundColor: Colors.indigo.shade50,
                        side: BorderSide(color: Colors.indigo.shade200),
                      ),
                    )
                    .toList(),
              ),
            const SizedBox(height: 16),
            if (block.metadataLines.isNotEmpty)
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: block.metadataLines
                    .map(
                      (line) => Padding(
                        padding: const EdgeInsets.only(bottom: 4.0),
                        child: OutputRenderer(markdownContent: line),
                      ),
                    )
                    .toList(),
              ),
            if (block.costs != null || block.tokens != null) ...[
              const Divider(height: 24, thickness: 1),
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (block.costs != null)
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'Meta Costs',
                            style: TextStyle(fontWeight: FontWeight.bold),
                          ),
                          Text(
                            block.costs!,
                            style: const TextStyle(fontSize: 12),
                          ),
                        ],
                      ),
                    ),
                  if (block.tokens != null)
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'Meta Tokens',
                            style: TextStyle(fontWeight: FontWeight.bold),
                          ),
                          ...block.tokens!.entries.map(
                            (e) => Text(
                              '${e.key}: ${e.value}',
                              style: const TextStyle(fontSize: 12),
                            ),
                          ),
                        ],
                      ),
                    ),
                ],
              ),
            ],
            if (block.customPrefaceMd != null &&
                block.customPrefaceMd!.isNotEmpty) ...[
              const SizedBox(height: 24),
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.white,
                  border: Border.all(color: Colors.blue, width: 2),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: OutputRenderer(markdownContent: block.customPrefaceMd!),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
