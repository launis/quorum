import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/features/execution/models/execution_step.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class ExecutionTimeline extends ConsumerWidget {
  final List<ExecutionStep> steps;
  final bool compact;

  const ExecutionTimeline({
    super.key,
    required this.steps,
    this.compact = false,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    if (steps.isEmpty) {
      return const SizedBox();
    }

    final theme = Theme.of(context);
    final l10n = AppLocalizations.of(context)!;

    try {
      for (final step in steps) {
        if (step.id.trim().isEmpty) {
          throw AppException.validation(
            'Fail-Fast: ExecutionStep id cannot be empty.',
          );
        }
        if (step.label.trim().isEmpty) {
          throw AppException.validation(
            'Fail-Fast: ExecutionStep label cannot be empty.',
          );
        }
        if (step.status.trim().isEmpty) {
          throw AppException.validation(
            'Fail-Fast: ExecutionStep status cannot be empty.',
          );
        }
        final stepProgress = step.progress;
        if (stepProgress != null && (stepProgress < 0 || stepProgress > 100)) {
          throw AppException.validation(
            'Fail-Fast: ExecutionStep progress must be between 0 and 100.',
          );
        }
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
              labelColor = theme.colorScheme.primary;
            } else if (isQueued) {
              labelColor = theme.disabledColor;
            } else if (isFailed) {
              labelColor = theme.colorScheme.error;
            }

            final lastError = step.lastError;
            final messageCode = step.messageCode;
            final progress = step.progress;
            final hasWarnings = step.hasWarning;

            Widget? subtitleWidget;
            if (isFailed && lastError != null && lastError.isNotEmpty) {
              subtitleWidget = Text(
                lastError,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.error,
                ),
              );
            } else if (isRunning && progress != null) {
              subtitleWidget = Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  AppSpacing.h8,
                  Row(
                    children: [
                      Expanded(
                        child: ClipRRect(
                          borderRadius: BorderRadius.circular(AppSpacing.s4),
                          child: LinearProgressIndicator(
                            value: progress / 100.0,
                            backgroundColor: theme.disabledColor.withValues(
                              alpha: 0.2,
                            ),
                            minHeight: AppSpacing.s6,
                          ),
                        ),
                      ),
                      AppSpacing.w12,
                      Flexible(
                        child: Text(
                          '${progress.toInt()}%',
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: theme.textTheme.bodySmall?.copyWith(
                            color: theme.colorScheme.primary,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ],
                  ),
                  if (messageCode == 'event_llm_anomaly_retry') ...[
                    AppSpacing.h4,
                    Text(
                      l10n.eventLlmAnomalyRetry,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.colorScheme.primary,
                        fontStyle: FontStyle.italic,
                      ),
                    ),
                  ],
                  AppSpacing.h4,
                ],
              );
            } else if (isRunning && messageCode == 'event_llm_anomaly_retry') {
              subtitleWidget = Text(
                l10n.eventLlmAnomalyRetry,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.primary,
                  fontStyle: FontStyle.italic,
                ),
              );
            }

            return ListTile(
              dense: true,
              visualDensity: compact ? VisualDensity.compact : null,
              leading: _buildStepIcon(
                theme,
                isCompleted,
                isQueued,
                isRunning,
                isFailed,
                hasWarnings,
              ),
              title: Text(
                stepLabel,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: theme.textTheme.bodyMedium?.copyWith(
                  fontWeight: isRunning || isCompleted
                      ? FontWeight.bold
                      : FontWeight.normal,
                  color: labelColor,
                ),
              ),
              subtitle: subtitleWidget,
              trailing: isRunning
                  ? const SizedBox(
                      width: AppSpacing.s12,
                      height: AppSpacing.s12,
                      child: CircularProgressIndicator(
                        strokeWidth: AppSpacing.s2,
                      ),
                    )
                  : null,
            );
          },
        ),
      );
    } catch (e, st) {
      ref
          .read(loggerServiceProvider)
          .error(
            'ExecutionTimeline',
            'VALIDATION_FAILED: Failed to render execution timeline',
            e,
            st,
          );
      return ErrorView(error: e, stackTrace: st, compact: true);
    }
  }

  Widget _buildStepIcon(
    ThemeData theme,
    bool isCompleted,
    bool isQueued,
    bool isRunning,
    bool isFailed,
    bool hasWarnings,
  ) {
    if (isFailed) {
      return Icon(Icons.error, color: theme.colorScheme.error, size: 20);
    }
    if (hasWarnings) {
      return Icon(
        Icons.warning_amber_rounded,
        color: theme.colorScheme.error,
        size: 20,
      );
    }
    if (isCompleted) {
      return Icon(
        Icons.check_circle,
        color: theme.colorScheme.primary,
        size: 20,
      );
    }
    if (isRunning) {
      return Icon(
        Icons.play_circle_fill,
        color: theme.colorScheme.primary,
        size: 20,
      );
    }
    if (isQueued) {
      return Icon(Icons.hourglass_empty, color: theme.disabledColor, size: 20);
    }
    return Icon(
      Icons.radio_button_unchecked,
      color: theme.colorScheme.onSurfaceVariant,
      size: 20,
    );
  }
}
