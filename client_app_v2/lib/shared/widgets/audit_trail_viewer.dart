import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/widgets/deep_dive_expander.dart';

class _ParsedAuditStep {
  final int stepNumber;
  final String agent;
  final String version;
  final String timestamp;
  final String? reasoningTrace;
  final String? methodologicalLog;

  const _ParsedAuditStep({
    required this.stepNumber,
    required this.agent,
    required this.version,
    required this.timestamp,
    this.reasoningTrace,
    this.methodologicalLog,
  });
}

class AuditTrailViewer extends ConsumerWidget {
  final Map<String, Object?> data;

  const AuditTrailViewer({super.key, required this.data});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    if (data.isEmpty ||
        !data.containsKey('Raw_Steps') ||
        data['Raw_Steps'] == null) {
      return const SizedBox();
    }

    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);

    try {
      final rawStepsObj = data['Raw_Steps'];
      if (rawStepsObj is! Map<String, Object?>) {
        throw AppException.validation(
          'Fail-Fast: Raw_Steps must be a Map<String, Object?>.',
        );
      }

      if (rawStepsObj.isEmpty) {
        return const SizedBox();
      }

      final parsedSteps = <_ParsedAuditStep>[];
      for (final entry in rawStepsObj.entries) {
        final stepKey = entry.key;
        final val = entry.value;
        if (val is! Map<String, Object?>) {
          throw AppException.validation(
            'Fail-Fast: Step entry "$stepKey" must be a Map<String, Object?>.',
          );
        }

        final meta = val['metadata'];
        if (meta is! Map<String, Object?>) {
          throw AppException.validation(
            'Fail-Fast: Missing or invalid metadata for step "$stepKey".',
          );
        }

        final stepNumRaw = meta['step'];
        if (stepNumRaw is! num) {
          throw AppException.validation(
            'Fail-Fast: Missing or invalid numeric step index for "$stepKey".',
          );
        }

        final agent = meta['agent'];
        if (agent is! String || agent.trim().isEmpty) {
          throw AppException.validation(
            'Fail-Fast: Missing or invalid agent identifier for "$stepKey".',
          );
        }

        final version = meta['version'];
        if (version is! String || version.trim().isEmpty) {
          throw AppException.validation(
            'Fail-Fast: Missing or invalid version for "$stepKey".',
          );
        }

        final timestamp = meta['timestamp'];
        if (timestamp is! String || timestamp.trim().isEmpty) {
          throw AppException.validation(
            'Fail-Fast: Missing or invalid timestamp for "$stepKey".',
          );
        }

        final reasoningRaw = val['reasoning_trace'];
        if (reasoningRaw != null && reasoningRaw is! String) {
          throw AppException.validation(
            'Fail-Fast: Invalid reasoning_trace type for "$stepKey".',
          );
        }

        final methodLogRaw = val['methodological_log'];
        if (methodLogRaw != null && methodLogRaw is! String) {
          throw AppException.validation(
            'Fail-Fast: Invalid methodological_log type for "$stepKey".',
          );
        }

        parsedSteps.add(
          _ParsedAuditStep(
            stepNumber: stepNumRaw.toInt(),
            agent: agent,
            version: version,
            timestamp: timestamp,
            reasoningTrace: reasoningRaw as String?,
            methodologicalLog: methodLogRaw as String?,
          ),
        );
      }

      parsedSteps.sort((a, b) => a.stepNumber.compareTo(b.stepNumber));

      return DeepDiveExpander(
        title: l10n.systemAuditTrailLabel,
        icon: Icons.terminal,
        initiallyExpanded: false,
        child: ListView.separated(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: parsedSteps.length,
          separatorBuilder: (_, _) => const Divider(),
          itemBuilder: (context, index) {
            final step = parsedSteps[index];

            return Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Expanded(
                      child: Text(
                        '${step.agent} (${step.version})',
                        overflow: TextOverflow.ellipsis,
                        style: theme.textTheme.bodyMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: theme.colorScheme.onSurfaceVariant,
                        ),
                      ),
                    ),
                    AppSpacing.w8,
                    Flexible(
                      child: Text(
                        step.timestamp,
                        overflow: TextOverflow.ellipsis,
                        style: theme.textTheme.labelSmall?.copyWith(
                          color: theme.colorScheme.onSurfaceVariant,
                        ),
                      ),
                    ),
                  ],
                ),
                AppSpacing.h8,
                if (step.reasoningTrace != null &&
                    step.reasoningTrace!.isNotEmpty) ...[
                  Text(
                    '${l10n.lblReasoning}:',
                    style: theme.textTheme.labelSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                      fontStyle: FontStyle.italic,
                      color: theme.colorScheme.onSurface,
                    ),
                  ),
                  Container(
                    width: double.infinity,
                    padding: AppSpacing.p8,
                    color: theme.colorScheme.surfaceContainerHighest.withValues(
                      alpha: 0.5,
                    ),
                    child: Text(
                      step.reasoningTrace!,
                      style: theme.textTheme.labelSmall?.copyWith(
                        fontFamily: 'monospace',
                        color: theme.colorScheme.onSurface,
                      ),
                    ),
                  ),
                  AppSpacing.h8,
                ],
                if (step.methodologicalLog != null &&
                    step.methodologicalLog!.isNotEmpty) ...[
                  Text(
                    '${l10n.lblMethodologicalLog}: ${step.methodologicalLog}',
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: theme.colorScheme.onSurface,
                    ),
                  ),
                ],
              ],
            );
          },
        ),
      );
    } catch (e, st) {
      ref
          .read(loggerServiceProvider)
          .error(
            'AuditTrailViewer',
            'VALIDATION_FAILED: Failed to render audit trail',
            e,
            st,
          );
      return ErrorView(error: e, stackTrace: st, compact: true);
    }
  }
}
