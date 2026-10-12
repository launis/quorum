import 'package:flutter/material.dart';
import 'package:client_app/core/error/app_error_boundary.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/features/execution/presentation/causal_inspector_modal.dart';
import 'package:client_app/shared/models/sdui_block_dto.dart';
import 'package:client_app/theme/app_colors.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

/// Server-driven UI widget rendering the Unified Causal Action Card.
///
/// Implements 1:1 layout and semantic parity with the Jinja2 PDF report macro
/// (`render_causal_graph_block`), adhering strictly to Flutter Theme Sovereignty.
class SduiCausalGraphWidget extends StatelessWidget {
  final SduiCausalGraphBlock block;

  const SduiCausalGraphWidget({super.key, required this.block});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final textTheme = theme.textTheme;
    final semanticColors = context.semanticColors;
    final langCode = Localizations.localeOf(context).languageCode;
    final summaryText = block.summary.get(langCode);

    return AppErrorBoundary(
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: AppSpacing.s8),
        padding: const EdgeInsets.all(AppSpacing.s12),
        decoration: BoxDecoration(
          color: colorScheme.surfaceContainerLow,
          borderRadius: BorderRadius.circular(AppSpacing.s8),
          border: Border.all(color: colorScheme.outlineVariant),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            _buildHeader(
              context,
              summaryText,
              colorScheme,
              textTheme,
              semanticColors,
            ),
            if (block.criticalPathNodes.isNotEmpty) ...[
              AppSpacing.h12,
              _buildCriticalPath(
                context,
                colorScheme,
                textTheme,
                semanticColors,
              ),
            ],
            if (block.rootCauseDiagnoses.isNotEmpty) ...[
              AppSpacing.h12,
              _buildRootCauses(context, colorScheme, textTheme, semanticColors),
            ],
            if (block.prescriptiveRemediations.isNotEmpty) ...[
              AppSpacing.h12,
              _buildRemediations(
                context,
                colorScheme,
                textTheme,
                semanticColors,
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildHeader(
    BuildContext context,
    String summaryText,
    ColorScheme colorScheme,
    TextTheme textTheme,
    AppSemanticColors semanticColors,
  ) {
    return Container(
      padding: const EdgeInsets.only(bottom: AppSpacing.s8),
      decoration: BoxDecoration(
        border: Border(
          bottom: BorderSide(
            color: colorScheme.outlineVariant.withValues(alpha: 0.5),
          ),
        ),
      ),
      child: Row(
        children: [
          Icon(Icons.hub_outlined, color: colorScheme.primary, size: 20),
          AppSpacing.w8,
          Expanded(
            child: Text(
              summaryText.isNotEmpty
                  ? summaryText
                  : 'Causal Discovery & Fault Analysis',
              style: textTheme.titleSmall?.copyWith(
                fontWeight: FontWeight.bold,
                color: colorScheme.onSurface,
              ),
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
          ),
          AppSpacing.w8,
          Container(
            padding: const EdgeInsets.symmetric(
              horizontal: AppSpacing.s8,
              vertical: AppSpacing.s4,
            ),
            decoration: BoxDecoration(
              color: colorScheme.primaryContainer,
              borderRadius: BorderRadius.circular(AppSpacing.s12),
              border: Border.all(
                color: colorScheme.primary.withValues(alpha: 0.2),
              ),
            ),
            child: Text(
              '${block.intactClaimsCount} / ${block.totalClaimsCount} Intact',
              style: textTheme.labelSmall?.copyWith(
                fontWeight: FontWeight.bold,
                color: colorScheme.onPrimaryContainer,
              ),
            ),
          ),
          AppSpacing.w8,
          OutlinedButton.icon(
            style: OutlinedButton.styleFrom(
              visualDensity: VisualDensity.compact,
              padding: const EdgeInsets.symmetric(
                horizontal: AppSpacing.s8,
                vertical: AppSpacing.s4,
              ),
            ),
            icon: const Icon(Icons.fullscreen, size: 16),
            label: Text(AppLocalizations.of(context)!.causalInspectorTitle),
            onPressed: () => showDialog<void>(
              context: context,
              builder: (ctx) => CausalInspectorModal(block: block),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCriticalPath(
    BuildContext context,
    ColorScheme colorScheme,
    TextTheme textTheme,
    AppSemanticColors semanticColors,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'CRITICAL CAUSAL PATH',
          style: textTheme.labelSmall?.copyWith(
            fontWeight: FontWeight.bold,
            letterSpacing: 0.5,
            color: colorScheme.primary,
          ),
        ),
        AppSpacing.h8,
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(AppSpacing.s8),
          decoration: BoxDecoration(
            color: colorScheme.surfaceContainerLowest,
            borderRadius: BorderRadius.circular(AppSpacing.s6),
            border: Border.all(color: colorScheme.outlineVariant),
          ),
          child: Wrap(
            spacing: AppSpacing.s4,
            runSpacing: AppSpacing.s6,
            crossAxisAlignment: WrapCrossAlignment.center,
            children: [
              for (int i = 0; i < block.criticalPathNodes.length; i++) ...[
                _buildNodeChip(
                  block.criticalPathNodes[i],
                  colorScheme,
                  textTheme,
                ),
                if (i < block.criticalPathNodes.length - 1)
                  Padding(
                    padding: const EdgeInsets.symmetric(
                      horizontal: AppSpacing.s2,
                    ),
                    child: Icon(
                      Icons.arrow_forward,
                      size: 12,
                      color: colorScheme.outline,
                    ),
                  ),
              ],
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildNodeChip(
    dynamic node,
    ColorScheme colorScheme,
    TextTheme textTheme,
  ) {
    final isPassed = node.status == ExecutionStatus.passed;
    final claimText = node.claim as String;
    final truncatedClaim = claimText.length > 45
        ? '${claimText.substring(0, 42)}...'
        : claimText;

    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: AppSpacing.s6,
        vertical: AppSpacing.s2,
      ),
      decoration: BoxDecoration(
        color: isPassed
            ? colorScheme.primaryContainer.withValues(alpha: 0.6)
            : colorScheme.errorContainer.withValues(alpha: 0.6),
        borderRadius: BorderRadius.circular(AppSpacing.s4),
        border: Border.all(
          color: isPassed
              ? colorScheme.primary.withValues(alpha: 0.3)
              : colorScheme.error.withValues(alpha: 0.3),
        ),
      ),
      child: Text(
        '[${node.nodeId}] $truncatedClaim',
        style: textTheme.labelSmall?.copyWith(
          fontWeight: FontWeight.w600,
          color: isPassed
              ? colorScheme.onPrimaryContainer
              : colorScheme.onErrorContainer,
        ),
      ),
    );
  }

  Widget _buildRootCauses(
    BuildContext context,
    ColorScheme colorScheme,
    TextTheme textTheme,
    AppSemanticColors semanticColors,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'ROOT CAUSE DIAGNOSES',
          style: textTheme.labelSmall?.copyWith(
            fontWeight: FontWeight.bold,
            letterSpacing: 0.5,
            color: colorScheme.error,
          ),
        ),
        AppSpacing.h8,
        ...block.rootCauseDiagnoses.map(
          (diag) => Container(
            margin: const EdgeInsets.only(bottom: AppSpacing.s6),
            padding: const EdgeInsets.all(AppSpacing.s8),
            decoration: BoxDecoration(
              color: colorScheme.errorContainer.withValues(alpha: 0.15),
              borderRadius: BorderRadius.circular(AppSpacing.s4),
              border: Border(
                left: BorderSide(
                  color: colorScheme.error,
                  width: AppSpacing.s4,
                ),
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text(
                      'Fault Chain: ${diag.rootCauseParentId} → ${diag.failingNodeId}',
                      style: textTheme.labelSmall?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: colorScheme.error,
                      ),
                    ),
                    if (diag.paragraphRef.isNotEmpty) ...[
                      const Spacer(),
                      Text(
                        'Ref: ${diag.paragraphRef}',
                        style: textTheme.labelSmall?.copyWith(
                          color: colorScheme.onSurfaceVariant,
                        ),
                      ),
                    ],
                  ],
                ),
                AppSpacing.h4,
                Text(
                  diag.explanation,
                  style: textTheme.bodySmall?.copyWith(
                    color: colorScheme.onSurface,
                  ),
                ),
                if (diag.penaltyPoints > 0) ...[
                  AppSpacing.h4,
                  Text(
                    'Penalty: -${diag.penaltyPoints.toStringAsFixed(1)} pts',
                    style: textTheme.labelSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: colorScheme.error,
                    ),
                  ),
                ],
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildRemediations(
    BuildContext context,
    ColorScheme colorScheme,
    TextTheme textTheme,
    AppSemanticColors semanticColors,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'PRESCRIPTIVE REMEDIATIONS',
          style: textTheme.labelSmall?.copyWith(
            fontWeight: FontWeight.bold,
            letterSpacing: 0.5,
            color: colorScheme.primary,
          ),
        ),
        AppSpacing.h8,
        ...block.prescriptiveRemediations.map(
          (rem) => Container(
            margin: const EdgeInsets.only(bottom: AppSpacing.s4),
            padding: const EdgeInsets.all(AppSpacing.s8),
            decoration: BoxDecoration(
              color: colorScheme.primaryContainer.withValues(alpha: 0.15),
              borderRadius: BorderRadius.circular(AppSpacing.s4),
              border: Border(
                left: BorderSide(
                  color: colorScheme.primary,
                  width: AppSpacing.s4,
                ),
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Target [${rem.targetNodeId}]: ${rem.requiredAction}',
                  style: textTheme.bodySmall?.copyWith(
                    fontWeight: FontWeight.w600,
                    color: colorScheme.onSurface,
                  ),
                ),
                if (rem.potentialScoreImpact > 0) ...[
                  AppSpacing.h2,
                  Text(
                    'Estimated Impact: +${rem.potentialScoreImpact.toStringAsFixed(1)} pts',
                    style: textTheme.labelSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: colorScheme.primary,
                    ),
                  ),
                ],
              ],
            ),
          ),
        ),
      ],
    );
  }
}
