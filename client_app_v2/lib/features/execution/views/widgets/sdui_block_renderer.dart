import 'package:flutter/material.dart';
import 'package:client_app/features/execution/models/report_data_dto.dart';

class SDUIBlockRenderer extends StatelessWidget {
  final List<SduiBlockDTO> contentBlocks;

  const SDUIBlockRenderer({super.key, required this.contentBlocks});

  @override
  Widget build(BuildContext context) {
    if (contentBlocks.isEmpty) {
      return const SizedBox();
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: contentBlocks.map((block) {
        return switch (block) {
          SduiParagraphBlock p => _buildParagraph(context, p),
          SduiBulletListBlock b => _buildBulletList(context, b),
          SduiAlertBoxBlock a => _buildAlertBox(context, a),
          SduiHeroInsightBlock h => _buildHeroInsight(context, h),
        };
      }).toList(),
    );
  }

  Widget _buildParagraph(BuildContext context, SduiParagraphBlock block) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16.0),
      child: RichText(
        text: TextSpan(
          style: Theme.of(context).textTheme.bodyLarge?.copyWith(height: 1.5),
          children: [
            TextSpan(text: block.text),
            for (final citation in block.citations)
              WidgetSpan(
                alignment: PlaceholderAlignment.middle,
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 4.0),
                  child: Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 6,
                      vertical: 2,
                    ),
                    decoration: BoxDecoration(
                      color: Colors.blue.shade50,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: Colors.blue.shade200),
                    ),
                    child: Text(
                      citation,
                      style: TextStyle(
                        fontSize: 10,
                        fontWeight: FontWeight.bold,
                        color: Colors.blue.shade800,
                      ),
                    ),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildBulletList(BuildContext context, SduiBulletListBlock block) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: block.items.map((item) {
          return Padding(
            padding: const EdgeInsets.only(bottom: 8.0, left: 8.0),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Padding(
                  padding: EdgeInsets.only(top: 8.0, right: 8.0),
                  child: Icon(Icons.circle, size: 6, color: Colors.grey),
                ),
                Expanded(
                  child: RichText(
                    text: TextSpan(
                      style: Theme.of(
                        context,
                      ).textTheme.bodyLarge?.copyWith(height: 1.5),
                      children: [
                        TextSpan(text: item.text),
                        for (final citation in item.citations)
                          WidgetSpan(
                            alignment: PlaceholderAlignment.middle,
                            child: Padding(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 4.0,
                              ),
                              child: Container(
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 6,
                                  vertical: 2,
                                ),
                                decoration: BoxDecoration(
                                  color: Colors.blue.shade50,
                                  borderRadius: BorderRadius.circular(12),
                                  border: Border.all(
                                    color: Colors.blue.shade200,
                                  ),
                                ),
                                child: Text(
                                  citation.toString(),
                                  style: TextStyle(
                                    fontSize: 10,
                                    fontWeight: FontWeight.bold,
                                    color: Colors.blue.shade800,
                                  ),
                                ),
                              ),
                            ),
                          ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          );
        }).toList(),
      ),
    );
  }

  Widget _buildAlertBox(BuildContext context, SduiAlertBoxBlock block) {
    final isWarning = block.severity == 'warning' || block.severity == 'high';
    final color = isWarning ? Colors.amber : Colors.blue;

    return Padding(
      padding: const EdgeInsets.only(bottom: 16.0),
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.all(16.0),
        decoration: BoxDecoration(
          color: color.shade50,
          borderRadius: BorderRadius.circular(8),
          border: Border(
            left: BorderSide(color: color.shade400, width: 4),
            top: BorderSide(color: color.shade200),
            right: BorderSide(color: color.shade200),
            bottom: BorderSide(color: color.shade200),
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              block.title,
              style: TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 16,
                color: color.shade900,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              block.message,
              style: TextStyle(fontSize: 14, color: color.shade800),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHeroInsight(BuildContext context, SduiHeroInsightBlock block) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16.0),
      child: Text(
        block.text,
        style: Theme.of(context).textTheme.headlineSmall?.copyWith(
          fontWeight: FontWeight.bold,
          color: Theme.of(context).primaryColor,
        ),
      ),
    );
  }
}
