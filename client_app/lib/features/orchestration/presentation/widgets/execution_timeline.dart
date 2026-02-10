
import 'package:flutter/material.dart';
import 'package:client_app/features/orchestration/domain/models/assessment_view.dart'; // For StepProgressItem

class ExecutionTimeline extends StatelessWidget {
  final List<StepProgressItem> steps;
  final bool compact;

  const ExecutionTimeline({
    super.key,
    required this.steps,
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
          
          final isCompleted = step.status == 'completed' || step.status == 'finished';
          final isRunning = step.status == 'running';
          final isFailed = step.status == 'failed' || step.status == 'error';
          
          Color? labelColor;
          if (isRunning) labelColor = Theme.of(context).primaryColor;
          if (isFailed) labelColor = Theme.of(context).colorScheme.error;

          return ListTile(
            dense: true,
            visualDensity: compact ? VisualDensity.compact : null,
            leading: _buildStepIcon(isCompleted, isRunning, isFailed),
            title: Text(
              step.label,
              style: TextStyle(
                fontWeight: isRunning || isCompleted ? FontWeight.bold : FontWeight.normal,
                color: labelColor,
              ),
            ),
            trailing: isRunning
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

  Widget _buildStepIcon(bool isCompleted, bool isRunning, bool isFailed) {
    if (isFailed) {
      return const Icon(Icons.error, color: Colors.red, size: 20);
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
