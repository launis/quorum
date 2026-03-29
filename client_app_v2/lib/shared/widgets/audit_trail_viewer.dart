import 'package:flutter/material.dart';
import 'package:client_app/shared/widgets/deep_dive_expander.dart';

class AuditTrailViewer extends StatelessWidget {
  final Map<String, dynamic> data;

  const AuditTrailViewer({super.key, required this.data});

  @override
  Widget build(BuildContext context) {
    final rawSteps = data['Raw_Steps'] as Map<String, dynamic>? ?? {};

    if (rawSteps.isEmpty) return const SizedBox.shrink();

    // Sort steps
    final stepsList =
        rawSteps.entries.map((e) {
            final val = e.value as Map<String, dynamic>;
            final meta = val['metadata'] as Map<String, dynamic>? ?? {};
            final stepNum = meta['vaihe'] as num? ?? 999;
            return MapEntry(stepNum.toInt(), e);
          }).toList()
          ..sort((a, b) => a.key.compareTo(b.key));

    return DeepDiveExpander(
      title: 'Audit Trail (System Logs)',
      icon: Icons.terminal,
      initiallyExpanded: false,
      child: ListView.separated(
        shrinkWrap: true,
        physics: const NeverScrollableScrollPhysics(),
        itemCount: stepsList.length,
        separatorBuilder: (_, _) => const Divider(),
        itemBuilder: (context, index) {
          final entry = stepsList[index].value;
          final key = entry.key;
          final val = entry.value as Map<String, dynamic>;
          final meta = val['metadata'] as Map<String, dynamic>? ?? {};

          final agent = meta['agent'] as String? ?? key;
          final version = meta['versio'] as String? ?? 'v?';
          final timestamp = meta['luontiaika'] as String? ?? 'N/A';

          final reasoning = val['reasoning_trace'] as String?;
          final methodLog = val['metodologinen_loki'] as String?;

          return Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    '$agent ($version)',
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      color: Theme.of(context).colorScheme.onSurfaceVariant,
                    ),
                  ),
                  Text(
                    timestamp,
                    style: TextStyle(
                      fontSize: 10,
                      color: Theme.of(context).colorScheme.onSurfaceVariant,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              if (reasoning != null) ...[
                const Text(
                  'Reasoning Trace:',
                  style: TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.bold,
                    fontStyle: FontStyle.italic,
                  ),
                ),
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(8),
                  color: Colors.black.withValues(alpha: 0.05),
                  child: Text(
                    reasoning,
                    style: const TextStyle(
                      fontFamily: 'monospace',
                      fontSize: 10,
                    ),
                  ),
                ),
                const SizedBox(height: 8),
              ],
              if (methodLog != null) ...[
                Text(
                  'Method Log: $methodLog',
                  style: const TextStyle(fontSize: 11),
                ),
              ],
            ],
          );
        },
      ),
    );
  }
}
