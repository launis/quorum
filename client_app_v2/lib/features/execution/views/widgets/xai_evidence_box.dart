import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:client_app/features/execution/models/matrix_scorecard_dto.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/theme/app_colors.dart';

/// Renders the XAI Evidence Box — clickable source URLs from MCP Tool Loop searches.
/// Follows Flat MVC (§5): Zero logic, pure data mapping from McpAuditTraceDto.
/// Only renders if audit traces are non-empty (zero visual clutter for non-MCP workflows).
class XAIEvidenceBox extends ConsumerWidget {
  final List<McpAuditTraceDto> traces;

  const XAIEvidenceBox({super.key, required this.traces});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    if (traces.isEmpty) return const SizedBox();

    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);

    return Card(
      elevation: 3,
      margin: const EdgeInsets.symmetric(
        horizontal: AppSpacing.s16,
        vertical: AppSpacing.s16,
      ),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppSpacing.s12),
      ),
      child: ExpansionTile(
        initiallyExpanded: true,
        leading: Icon(Icons.fact_check, color: theme.colorScheme.primary),
        title: Text(
          l10n.xaiEvidenceTitle,
          style: theme.textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.bold,
            color: theme.colorScheme.primary,
          ),
        ),
        children: [
          const Divider(height: 1.0),
          ...traces.asMap().entries.map((entry) {
            final index = entry.key;
            final audit = entry.value;
            return _buildAuditEntry(context, ref, audit, index);
          }),
          AppSpacing.h8,
        ],
      ),
    );
  }

  Widget _buildAuditEntry(
    BuildContext context,
    WidgetRef ref,
    McpAuditTraceDto audit,
    int index,
  ) {
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);

    try {
      return Padding(
        padding: const EdgeInsets.symmetric(
          horizontal: AppSpacing.s16,
          vertical: AppSpacing.s8,
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            if (audit.claimText != null && audit.claimText!.isNotEmpty)
              Padding(
                padding: const EdgeInsets.only(bottom: AppSpacing.s8),
                child: Text.rich(
                  TextSpan(
                    children: [
                      TextSpan(
                        text: '${l10n.xaiEvidenceClaim}: ',
                        style: theme.textTheme.bodyMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: theme.colorScheme.primary,
                        ),
                      ),
                      TextSpan(
                        text: '"${audit.claimText}"',
                        style: theme.textTheme.bodyMedium?.copyWith(
                          fontStyle: FontStyle.italic,
                          color: theme.colorScheme.onSurface,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            // Query row with duration badge
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Icon(
                  Icons.search,
                  size: AppSpacing.s16,
                  color: theme.colorScheme.onSurfaceVariant,
                ),
                AppSpacing.w8,
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: AppSpacing.s6,
                          vertical: AppSpacing.s2,
                        ),
                        margin: const EdgeInsets.only(bottom: AppSpacing.s4),
                        decoration: BoxDecoration(
                          color: AppColors.intentInfo.withValues(alpha: 0.1),
                          borderRadius: BorderRadius.circular(AppSpacing.s4),
                          border: Border.all(
                            color: AppColors.intentInfo.withValues(alpha: 0.3),
                          ),
                        ),
                        child: Text(
                          audit.toolId,
                          style: theme.textTheme.labelSmall?.copyWith(
                            color: AppColors.intentInfo,
                            fontWeight: FontWeight.bold,
                            fontFamily: 'monospace',
                          ),
                        ),
                      ),
                      Text(
                        '${l10n.xaiEvidenceQuery}: "${audit.query}"',
                        style: theme.textTheme.bodyMedium?.copyWith(
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: AppSpacing.s8,
                    vertical: AppSpacing.s2,
                  ),
                  decoration: BoxDecoration(
                    color: theme.colorScheme.surfaceContainerHighest,
                    borderRadius: BorderRadius.circular(AppSpacing.s12),
                  ),
                  child: Text(
                    '${l10n.xaiEvidenceDuration}: ${audit.durationMs}ms',
                    style: theme.textTheme.labelSmall?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  ),
                ),
              ],
            ),

            // Reasoning (Language specific LLM explanation)
            if (audit.reasoning.isNotEmpty)
              Padding(
                padding: const EdgeInsets.only(
                  top: AppSpacing.s8,
                  left: AppSpacing.s24,
                ),
                child: Text.rich(
                  TextSpan(
                    children: [
                      TextSpan(
                        text: '${l10n.xaiEvidenceReasoning}: ',
                        style: theme.textTheme.bodySmall?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: theme.colorScheme.primary,
                        ),
                      ),
                      TextSpan(
                        text: audit.reasoning,
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: theme.colorScheme.onSurface,
                          height: 1.4,
                        ),
                      ),
                    ],
                  ),
                ),
              ),

            // Summary (if present) - Raw tool response
            if (audit.responseSummary.isNotEmpty)
              Padding(
                padding: const EdgeInsets.only(
                  top: AppSpacing.s8,
                  left: AppSpacing.s24,
                ),
                child: Text(
                  audit.responseSummary,
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant,
                    fontStyle: FontStyle.italic,
                    height: 1.4,
                  ),
                ),
              ),

            // Impacted Axes (if present)
            if (audit.impactedAxisNames.isNotEmpty) ...[
              Padding(
                padding: const EdgeInsets.only(
                  top: AppSpacing.s8,
                  left: AppSpacing.s24,
                ),
                child: Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: AppSpacing.s8,
                    vertical: AppSpacing.s6,
                  ),
                  decoration: BoxDecoration(
                    color: AppColors.intentSuccess.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(AppSpacing.s6),
                    border: Border.all(
                      color: AppColors.intentSuccess.withValues(alpha: 0.3),
                    ),
                  ),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Icon(
                        Icons.auto_awesome,
                        size: AppSpacing.s12,
                        color: AppColors.intentSuccess,
                      ),
                      const SizedBox(width: AppSpacing.s6),
                      Expanded(
                        child: Text.rich(
                          TextSpan(
                            children: [
                              TextSpan(
                                text: '${l10n.xaiEvidenceImpactedAxes} ',
                                style: theme.textTheme.labelSmall?.copyWith(
                                  fontWeight: FontWeight.bold,
                                  color: AppColors.intentSuccess,
                                ),
                              ),
                              TextSpan(
                                text: audit.impactedAxisNames.join(', '),
                                style: theme.textTheme.labelSmall?.copyWith(
                                  color: AppColors.intentSuccess,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],

            // Source URLs as clickable chips
            if (audit.sourceUrls.isNotEmpty) ...[
              Padding(
                padding: const EdgeInsets.only(
                  top: AppSpacing.s8,
                  left: AppSpacing.s24,
                ),
                child: Text(
                  l10n.xaiEvidenceSources,
                  style: theme.textTheme.labelSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: theme.colorScheme.primary,
                  ),
                ),
              ),
              Padding(
                padding: const EdgeInsets.only(
                  top: AppSpacing.s4,
                  left: AppSpacing.s24,
                ),
                child: Wrap(
                  spacing: AppSpacing.s8,
                  runSpacing: AppSpacing.s4,
                  children: audit.sourceUrls.map((url) {
                    return ActionChip(
                      avatar: Icon(
                        Icons.link,
                        size: AppSpacing.s12,
                        color: AppColors.intentInfo,
                      ),
                      label: Text(
                        _truncateUrl(url),
                        overflow: TextOverflow.ellipsis,
                        style: theme.textTheme.labelSmall?.copyWith(
                          color: AppColors.intentInfo,
                        ),
                      ),
                      onPressed: () => _launchUrl(url, ref),
                      backgroundColor: AppColors.intentInfo.withValues(
                        alpha: 0.08,
                      ),
                      side: BorderSide(
                        color: AppColors.intentInfo.withValues(alpha: 0.2),
                      ),
                    );
                  }).toList(),
                ),
              ),
            ],

            if (index < traces.length - 1)
              const Divider(height: AppSpacing.s24),
          ],
        ),
      );
    } catch (e, st) {
      // Diagnostic Node (§6.3): Fail loudly instead of hiding corruption
      ref
          .read(loggerServiceProvider)
          .error(
            'XAIEvidenceBox',
            'VALIDATION_FAILED: Failed to render audit entry',
            e,
            st,
          );
      return ErrorView(error: e, stackTrace: st, compact: true);
    }
  }

  /// Truncate URL for chip display (domain + first path segment).
  String _truncateUrl(String url) {
    try {
      final uri = Uri.parse(url);
      final pathSegments = uri.pathSegments;
      if (pathSegments.isEmpty) return uri.host.isNotEmpty ? uri.host : url;
      return '${uri.host}/${pathSegments.first}';
    } catch (_) {
      return url;
    }
  }

  Future<void> _launchUrl(String url, WidgetRef ref) async {
    try {
      final uri = Uri.parse(url);
      if (!await launchUrl(uri, mode: LaunchMode.externalApplication)) {
        ref
            .read(loggerServiceProvider)
            .error('XAIEvidenceBox', 'Could not launch URL: $url', null, null);
      }
    } catch (e, st) {
      ref
          .read(loggerServiceProvider)
          .error('XAIEvidenceBox', 'URL launch error: $e', e, st);
      throw AppException.network(
        'URL launch error: $e',
      ).copyWith(extensions: {'url': url});
    }
  }
}
