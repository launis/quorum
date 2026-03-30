import 'dart:io';
import 'package:flutter/material.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

class ValidationTimelineWidget extends StatelessWidget {
  final String title;
  final List<dynamic> events;

  const ValidationTimelineWidget({
    super.key,
    required this.title,
    required this.events,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      child: Semantics(
        excludeSemantics: Platform.isWindows,
        child: ExpansionTile(
          initiallyExpanded: true,
          title: Text(
            title,
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
          children: [
            if (events.isEmpty)
              Padding(
                padding: const EdgeInsets.all(16.0),
                child: Text(
                  AppLocalizations.of(context)?.sharedNoTimelineData ??
                      'No timeline data available.',
                ),
              ),
            ...events.asMap().entries.map((entry) {
              final index = entry.key;
              final e = entry.value as Map<String, dynamic>;
              final ts = e['timestamp'] as String? ?? '';

              String timeDisplay = ts;
              if (ts.length >= 16) {
                final tIndex = ts.indexOf('T');
                if (tIndex != -1 && tIndex + 5 < ts.length) {
                  timeDisplay = ts.substring(tIndex + 1, tIndex + 6);
                }
              }

              // Alert check: we look for error flags or severe words in the label
              final label = e['label'] as String? ?? '';
              final lowerLabel = label.toLowerCase();
              final isAlert =
                  lowerLabel.contains('error') ||
                  lowerLabel.contains('fail') ||
                  lowerLabel.contains('virhe') ||
                  e['is_alert'] == true;

              final isLast = index == events.length - 1;

              return IntrinsicHeight(
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    // Timeline connector
                    SizedBox(
                      width: 60,
                      child: Column(
                        children: [
                          Container(
                            width: 2,
                            height: 16,
                            color: index == 0
                                ? Colors.transparent
                                : Theme.of(
                                    context,
                                  ).colorScheme.onSurfaceVariant,
                          ),
                          Container(
                            width: 12,
                            height: 12,
                            decoration: BoxDecoration(
                              color: isAlert
                                  ? Theme.of(context).colorScheme.error
                                  : Theme.of(context).colorScheme.primary,
                              shape: BoxShape.circle,
                              border: Border.all(
                                color: Theme.of(context).colorScheme.surface,
                                width: 2,
                              ),
                            ),
                          ),
                          Expanded(
                            child: Container(
                              width: 2,
                              color: isLast
                                  ? Colors.transparent
                                  : Theme.of(
                                      context,
                                    ).colorScheme.onSurfaceVariant,
                            ),
                          ),
                        ],
                      ),
                    ),

                    // Time text
                    SizedBox(
                      width: 50,
                      child: Padding(
                        padding: const EdgeInsets.only(top: 12.0),
                        child: Text(
                          timeDisplay,
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 12,
                            color: isAlert
                                ? Theme.of(context).colorScheme.error
                                : Theme.of(
                                    context,
                                  ).colorScheme.onSurfaceVariant,
                          ),
                        ),
                      ),
                    ),

                    // Content
                    Expanded(
                      child: Padding(
                        padding: const EdgeInsets.fromLTRB(8, 12, 16, 24),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              label,
                              style: TextStyle(
                                fontWeight: FontWeight.bold,
                                color: isAlert
                                    ? Theme.of(context).colorScheme.error
                                    : Theme.of(context).colorScheme.onSurface,
                              ),
                            ),
                            if (e['content'] != null &&
                                e['content'].toString().isNotEmpty) ...[
                              const SizedBox(height: 4),
                              Text(
                                e['content'].toString(),
                                style: TextStyle(
                                  color: Theme.of(
                                    context,
                                  ).colorScheme.onSurfaceVariant,
                                ),
                              ),
                            ],
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              );
            }),
            const SizedBox(height: 8), // Padding at bottom of list
          ],
        ),
      ),
    );
  }
}
