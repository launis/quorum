import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// **Execution Details Screen**
///
/// Displays detailed information about a specific orchestration execution.
///
/// **Features**:
/// - Shows Execution ID.
/// - Placeholder for future detailed steps/logs view.
class ExecutionDetailsScreen extends ConsumerWidget {
  const ExecutionDetailsScreen({super.key, required this.executionId});

  final String executionId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(title: const Text('Execution Details')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              'Execution ID:',
              style: Theme.of(context).textTheme.labelLarge,
            ),
            const SizedBox(height: 8),
            Text(executionId, style: Theme.of(context).textTheme.headlineSmall),
            const SizedBox(height: 24),
            const Text('Details view coming soon...'),
          ],
        ),
      ),
    );
  }
}
