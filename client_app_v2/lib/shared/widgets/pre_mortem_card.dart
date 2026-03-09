import 'package:flutter/material.dart';
import 'package:client_app/shared/widgets/deep_dive_expander.dart';

class PreMortemCard extends StatelessWidget {
  final Map<String, dynamic> report;

  const PreMortemCard({super.key, required this.report});

  @override
  Widget build(BuildContext context) {
    final preMortem = report['pre_mortem_analyysi'] as Map<String, dynamic>?;

    if (preMortem == null) return const SizedBox.shrink();

    final executed = preMortem['suoritettu'] as bool? ?? false;
    final signals = preMortem['hiljaiset_signaalit'] as List? ?? [];

    return DeepDiveExpander(
      title: 'Pre-Mortem & Future Signs',
      icon: Icons.visibility_outlined, // Eye icon for "Foreseeing"
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Text('Analysis Performed: '),
              Icon(
                executed ? Icons.check : Icons.close,
                size: 16,
                color: executed ? Colors.green : Colors.grey,
              ),
            ],
          ),
          const SizedBox(height: 12),
          if (signals.isNotEmpty) ...[
            Text(
              'Hiljaiset signaalit (Weak Signals):',
              style: Theme.of(
                context,
              ).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Container(
              decoration: BoxDecoration(
                color: Colors.amber.withValues(alpha: 0.05),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.amber.withValues(alpha: 0.2)),
              ),
              child: Column(
                children:
                    signals.map((s) {
                      return ListTile(
                        leading: const Icon(
                          Icons.sensors,
                          size: 16,
                          color: Colors.amber,
                        ),
                        title: Text(
                          s.toString(),
                          style: const TextStyle(fontSize: 13),
                        ),
                        dense: true,
                        visualDensity: VisualDensity.compact,
                      );
                    }).toList(),
              ),
            ),
          ],
        ],
      ),
    );
  }
}
