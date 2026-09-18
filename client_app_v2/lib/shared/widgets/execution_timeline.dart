import 'package:flutter/material.dart';
import 'package:client_app/features/execution/models/execution_step.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

class ExecutionTimeline extends StatelessWidget {
  final List<ExecutionStep> steps;
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
          final stepStatus = step.status.toLowerCase();
          final stepLabel = step.label;

          final isCompleted = stepStatus == 'passed';
          final isQueued = stepStatus == 'queued' || stepStatus == 'pending';
          final isRunning = stepStatus == 'running';
          final isFailed =
              stepStatus == 'failed' || stepStatus == 'system_error';

          Color? labelColor;
          if (isRunning) {
            labelColor = Theme.of(context).colorScheme.primary;
          } else if (isQueued) {
            labelColor = Theme.of(context).disabledColor;
          } else if (isFailed) {
            labelColor = Theme.of(context).colorScheme.error;
          }

          final lastError = step.lastError;
          final messageCode = step.messageCode;
          final progress = step.progress;
          final hasWarnings = step.hasWarning;

          Widget? subtitleWidget;
          if (isFailed && lastError != null && lastError.isNotEmpty) {
            subtitleWidget = Text(
              lastError,
              style: TextStyle(
                color: Theme.of(context).colorScheme.error,
                fontSize: 12,
              ),
            );
          } else if (isRunning && progress != null) {
            subtitleWidget = Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SizedBox(height: 8),
                Row(
                  children: [
                    Expanded(
                      child: ClipRRect(
                        borderRadius: BorderRadius.circular(4),
                        child: LinearProgressIndicator(
                          value: progress / 100.0,
                          backgroundColor: Theme.of(
                            context,
                          ).disabledColor.withValues(alpha: 0.2),
                          minHeight: 6,
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Text(
                      '${progress.toInt()}%',
                      style: TextStyle(
                        fontSize: 12,
                        color: Theme.of(context).colorScheme.primary,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                if (messageCode == 'event_llm_anomaly_retry') ...[
                  const SizedBox(height: 4),
                  Text(
                    AppLocalizations.of(context)!.eventLlmAnomalyRetry,
                    style: TextStyle(
                      color: Theme.of(context).colorScheme.primary,
                      fontSize: 12,
                      fontStyle: FontStyle.italic,
                    ),
                  ),
                ],
                const SizedBox(height: 4),
              ],
            );
          } else if (isRunning && messageCode == 'event_llm_anomaly_retry') {
            subtitleWidget = Text(
              AppLocalizations.of(context)!.eventLlmAnomalyRetry,
              style: TextStyle(
                color: Theme.of(context).colorScheme.primary,
                fontSize: 12,
                fontStyle: FontStyle.italic,
              ),
            );
          }

          return ListTile(
            dense: true,
            visualDensity: compact ? VisualDensity.compact : null,
            leading: _buildStepIcon(
              context,
              isCompleted,
              isQueued,
              isRunning,
              isFailed,
              hasWarnings,
            ),
            title: Text(
              stepLabel,
              overflow: TextOverflow.ellipsis,
              style: TextStyle(
                fontWeight: isRunning || isCompleted
                    ? FontWeight.bold
                    : FontWeight.normal,
                color: labelColor,
              ),
            ),
            subtitle: subtitleWidget,
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

  Widget _buildStepIcon(
    BuildContext context,
    bool isCompleted,
    bool isQueued,
    bool isRunning,
    bool isFailed,
    bool hasWarnings,
  ) {
    if (isFailed) {
      return Icon(
        Icons.error,
        color: Theme.of(context).colorScheme.error,
        size: 20,
      );
    }
    if (hasWarnings) {
      return Icon(
        Icons.warning_amber_rounded,
        color: Theme.of(context).colorScheme.error,
        size: 20,
      );
    }
    if (isCompleted) {
      return Icon(
        Icons.check_circle,
        color: Theme.of(context).colorScheme.primary,
        size: 20,
      );
    }
    if (isRunning) {
      return Icon(
        Icons.play_circle_fill,
        color: Theme.of(context).colorScheme.primary,
        size: 20,
      );
    }
    if (isQueued) {
      return Icon(
        Icons.hourglass_empty,
        color: Theme.of(context).disabledColor,
        size: 20,
      );
    }
    return Icon(
      Icons.radio_button_unchecked,
      color: Theme.of(context).colorScheme.onSurfaceVariant,
      size: 20,
    );
  }
}
