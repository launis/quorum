import 'package:flutter/material.dart';

class ExecutionTimeline extends StatelessWidget {
  final List<Map<String, dynamic>> steps;
  final Map<String, dynamic>? results;
  final bool compact;

  const ExecutionTimeline({
    super.key,
    required this.steps,
    this.results,
    this.compact = false,
  });

  @override
  Widget build(BuildContext context) {
    if (steps.isEmpty) {
      return const SizedBox.shrink();
    }

    return Card(
      elevation: compact ? 0 : 1,
      margin: compact ? EdgeInsets.zero : null,
      child: ListView.separated(
        shrinkWrap: true,
        physics: const NeverScrollableScrollPhysics(),
        itemCount: steps.length,
        separatorBuilder: (_, _) => const Divider(height: 1),
        itemBuilder: (context, index) {
          final step = steps[index];
          final stepStatus = step['status']?.toString() ?? 'pending';
          final stepLabel = step['label']?.toString() ?? 'Tuntematon askel';

          final isCompleted =
              stepStatus == 'completed' || stepStatus == 'finished';
          final isRunning = stepStatus == 'running';
          final isFailed = stepStatus == 'failed' || stepStatus == 'error';

          Color? labelColor;
          if (isRunning) labelColor = Theme.of(context).primaryColor;
          if (isFailed) labelColor = Theme.of(context).colorScheme.error;

          final stepId = step['step_id']?.toString() ?? '';
          final stepResult = results != null && results!.containsKey(stepId)
              ? (results![stepId] as Map<String, dynamic>?) ?? {}
              : {};
              
          final warningsList = stepResult['_system_warnings'] as List<dynamic>?;
          final hasWarnings = warningsList != null && warningsList.isNotEmpty;

          return ListTile(
            dense: true,
            visualDensity: compact ? VisualDensity.compact : null,
            leading: _buildStepIcon(isCompleted, isRunning, isFailed, hasWarnings),
            title: Text(
              stepLabel,
              style: TextStyle(
                fontWeight:
                    isRunning || isCompleted
                        ? FontWeight.bold
                        : FontWeight.normal,
                color: labelColor,
              ),
            ),
            trailing:
                isRunning
                    ? const SizedBox(
                      width: 12,
                      height: 12,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                    : null,
          );
        },
      ),
    );
  }

  Widget _buildStepIcon(bool isCompleted, bool isRunning, bool isFailed, bool hasWarnings) {
    if (isFailed) {
      return const Icon(Icons.error, color: Colors.red, size: 20);
    }
    if (hasWarnings) {
      return const Icon(Icons.warning_amber_rounded, color: Colors.orange, size: 20);
    }
    if (isCompleted) {
      return const Icon(Icons.check_circle, color: Colors.green, size: 20);
    }
    if (isRunning) {
      return const Icon(Icons.play_circle_fill, color: Colors.blue, size: 20);
    }
    return const Icon(
      Icons.radio_button_unchecked,
      color: Colors.grey,
      size: 20,
    );
  }
}
