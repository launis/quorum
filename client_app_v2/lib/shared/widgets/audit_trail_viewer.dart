import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/widgets/deep_dive_expander.dart';

@immutable
class AuditTrailStepMetadata {
  final int step;
  final String agent;
  final String version;
  final String timestamp;

  const AuditTrailStepMetadata({
    required this.step,
    required this.agent,
    required this.version,
    required this.timestamp,
  });
}

@immutable
class AuditTrailStepEntry {
  final AuditTrailStepMetadata? metadata;
  final String? reasoningTrace;
  final String? methodologicalLog;

  const AuditTrailStepEntry({
    this.metadata,
    this.reasoningTrace,
    this.methodologicalLog,
  });
}

@immutable
class AuditTrailData {
  final Map<String, AuditTrailStepEntry>? rawSteps;
  final bool isCorrupted;

  const AuditTrailData({this.rawSteps, this.isCorrupted = false});
}

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
  final AuditTrailData data;

  const AuditTrailViewer({super.key, required this.data});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    if (!data.isCorrupted &&
        (data.rawSteps == null || data.rawSteps!.isEmpty)) {
      return const SizedBox();
    }

    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);

    try {
      if (data.isCorrupted || data.rawSteps == null) {
        throw AppException.validation(
          'Fail-Fast: Raw_Steps payload is corrupted or invalid.',
        );
      }

      final rawStepsMap = data.rawSteps!;
      if (rawStepsMap.isEmpty) {
        return const SizedBox();
      }

      final parsedSteps = <_ParsedAuditStep>[];
      for (final entry in rawStepsMap.entries) {
        final stepKey = entry.key;
        final val = entry.value;

        final meta = val.metadata;
        if (meta == null) {
          throw AppException.validation(
            'Fail-Fast: Missing or invalid metadata for step "$stepKey".',
          );
        }

        if (meta.step <= 0) {
          throw AppException.validation(
            'Fail-Fast: Missing or invalid numeric step index for "$stepKey".',
          );
        }

        final agent = meta.agent;
        if (agent.trim().isEmpty) {
          throw AppException.validation(
            'Fail-Fast: Missing or invalid agent identifier for "$stepKey".',
          );
        }

        final version = meta.version;
        if (version.trim().isEmpty) {
          throw AppException.validation(
            'Fail-Fast: Missing or invalid version for "$stepKey".',
          );
        }

        final timestamp = meta.timestamp;
        if (timestamp.trim().isEmpty) {
          throw AppException.validation(
            'Fail-Fast: Missing or invalid timestamp for "$stepKey".',
          );
        }

        parsedSteps.add(
          _ParsedAuditStep(
            stepNumber: meta.step,
            agent: agent,
            version: version,
            timestamp: timestamp,
            reasoningTrace: val.reasoningTrace,
            methodologicalLog: val.methodologicalLog,
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
