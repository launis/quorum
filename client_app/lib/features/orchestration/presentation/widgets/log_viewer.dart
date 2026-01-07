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
        border: Border.all(color: Colors.grey.shade800),
      ),
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      child:
          logs.isEmpty
              ? const Center(
                child: Text(
                  'No logs available.',
                  style: TextStyle(color: Colors.grey, fontFamily: 'monospace'),
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
