import 'package:flutter/material.dart';

class LogViewer extends StatelessWidget {
  final List<String> logs;

  const LogViewer({super.key, required this.logs});

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.black,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: Theme.of(context).colorScheme.onSurfaceVariant,
        ),
      ),
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      child: logs.isEmpty
          ? Center(
              child: Text(
                'No logs available.',
                style: TextStyle(
                  color: Theme.of(context).colorScheme.onSurfaceVariant,
                  fontFamily: 'monospace',
                ),
              ),
            )
          : ListView.builder(
              itemCount: logs.length,
              itemBuilder: (context, index) {
                return Text(
                  logs[index],
                  style: const TextStyle(
                    color: Color(0xFF00FF00), // Matrix Green
                    fontFamily: 'monospace',
                    fontSize: 12,
                  ),
                );
              },
            ),
    );
  }
}
