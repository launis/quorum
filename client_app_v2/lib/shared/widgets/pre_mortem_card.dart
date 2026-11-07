import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/widgets/deep_dive_expander.dart';
import 'package:client_app/theme/app_colors.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

@immutable
class PreMortemAnalysisData {
  final bool? suoritettu;
  final List<String> hiljaisetSignaalit;
  final bool isCorrupted;

  const PreMortemAnalysisData({
    required this.suoritettu,
    this.hiljaisetSignaalit = const <String>[],
    this.isCorrupted = false,
  });
}

@immutable
class PreMortemReportData {
  final PreMortemAnalysisData? preMortemAnalyysi;

  const PreMortemReportData({this.preMortemAnalyysi});
}

class PreMortemCard extends ConsumerWidget {
  final PreMortemReportData report;

  const PreMortemCard({super.key, required this.report});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final preMortem = report.preMortemAnalyysi;
    if (preMortem == null) {
      return const SizedBox();
    }

    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);
    final semanticColors = context.semanticColors;

    try {
      if (preMortem.isCorrupted) {
        throw AppException.validation(
          'Fail-Fast: pre_mortem_analyysi payload is corrupted.',
        );
      }

      final executedRaw = preMortem.suoritettu;
      if (executedRaw == null) {
        throw AppException.validation(
          'Fail-Fast: Missing or invalid boolean "suoritettu" in pre_mortem_analyysi.',
        );
      }

      final parsedSignals = <String>[];
      for (var i = 0; i < preMortem.hiljaisetSignaalit.length; i++) {
        final item = preMortem.hiljaisetSignaalit[i];
        if (item.trim().isEmpty) {
          throw AppException.validation(
            'Fail-Fast: Weak signal at index $i must be a non-empty String.',
          );
        }
        parsedSignals.add(item);
      }

      return DeepDiveExpander(
        title: l10n.subPerformativityCheck,
        icon: Icons.visibility_outlined,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Flexible(
                  child: Text(
                    l10n.sharedAnalysisPerformed,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: theme.colorScheme.onSurface,
                    ),
                  ),
                ),
                AppSpacing.w4,
                Icon(
                  executedRaw ? Icons.check : Icons.close,
                  size: AppSpacing.s16,
                  color: executedRaw
                      ? semanticColors.success
                      : theme.colorScheme.onSurfaceVariant,
                ),
              ],
            ),
            AppSpacing.h12,
            if (parsedSignals.isNotEmpty) ...[
              Text(
                '${l10n.lblFindings}:',
                style: theme.textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: theme.colorScheme.onSurface,
                ),
              ),
              AppSpacing.h8,
              Container(
                decoration: BoxDecoration(
                  color: semanticColors.warning.withValues(alpha: 0.05),
                  borderRadius: BorderRadius.circular(AppSpacing.s8),
                  border: Border.all(
                    color: semanticColors.warning.withValues(alpha: 0.2),
                  ),
                ),
                child: Column(
                  children: parsedSignals.map((signal) {
                    return ListTile(
                      leading: Icon(
                        Icons.sensors,
                        size: AppSpacing.s16,
                        color: semanticColors.warning,
                      ),
                      title: Text(
                        signal,
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: theme.colorScheme.onSurface,
                        ),
                      ),
                      dense: true,
                      visualDensity: VisualDensity.compact,
                    );
                  }).toList(),
                ),
              ),
            ],
          ],
        ),
      );
    } catch (e, st) {
      ref
          .read(loggerServiceProvider)
          .error(
            'PreMortemCard',
            'VALIDATION_FAILED: Failed to render pre-mortem card',
            e,
            st,
          );
      return ErrorView(error: e, stackTrace: st, compact: true);
    }
  }
}
