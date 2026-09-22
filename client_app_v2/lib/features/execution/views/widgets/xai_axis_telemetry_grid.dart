import 'package:flutter/material.dart';
import 'package:client_app/features/execution/models/matrix_scorecard_dto.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/core/theme/app_spacing.dart';

/// Renders explainable AI (XAI) telemetry, evidence quotes, semantic explanations,
/// and remediation coaching for a matrix scorecard axis.
class XAIAxisTelemetryGrid extends StatelessWidget {
  final MatrixScorecardRowDto axis;
  final TextDeliveryMode textDeliveryMode;
  final bool showQuote;
  const XAIAxisTelemetryGrid({
    super.key,
    required this.axis,
    required this.textDeliveryMode,
    required this.showQuote,
  });

  @override
  Widget build(BuildContext context) {
    if (textDeliveryMode == TextDeliveryMode.none) {
      return const SizedBox();
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      mainAxisSize: MainAxisSize.min,
      children: [
        _buildMainContent(context),
        AppSpacing.h12,
        _buildTelemetryGrid(context),
      ],
    );
  }

  Widget _buildMainContent(BuildContext context) {
    final hasRowExplanation = axis.rowExplanation.trim().isNotEmpty;
    final isOverride = axis.contextualOverride == true;
    final hasExplanation =
        isOverride &&
        axis.semanticReasoning != null &&
        axis.semanticReasoning!.trim().isNotEmpty;
    final hasQuote =
        showQuote &&
        !isOverride &&
        axis.citedTextQuote != null &&
        axis.citedTextQuote!.isNotEmpty;
    final hasWebCitation =
        axis.citedWebCitation != null && axis.citedWebCitation!.isNotEmpty;
    final hasSourceId =
        axis.citedSourceId != null && axis.citedSourceId!.isNotEmpty;

    if (!hasRowExplanation &&
        !hasQuote &&
        !hasExplanation &&
        !hasWebCitation &&
        !hasSourceId) {
      return const SizedBox();
    }

    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: [
        if (hasRowExplanation)
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              if (axis.evidenceType != null) ...[
                Padding(
                  padding: const EdgeInsets.only(
                    top: AppSpacing.s2,
                    right: AppSpacing.s8,
                  ),
                  child: _buildEvidenceIcon(context, axis.evidenceType!),
                ),
              ],
              Expanded(
                child: Text(
                  axis.rowExplanation,
                  style: theme.textTheme.bodyMedium?.copyWith(
                    color: theme.colorScheme.onSurface,
                  ),
                ),
              ),
            ],
          ),
        if (hasQuote)
          Container(
            margin: const EdgeInsets.only(top: AppSpacing.s12),
            padding: const EdgeInsets.all(AppSpacing.s12),
            decoration: BoxDecoration(
              color: theme.colorScheme.surfaceContainerHighest.withValues(alpha: 0.4),
              border: Border(
                left: BorderSide(
                  color: theme.colorScheme.outlineVariant,
                  width: AppSpacing.s4,
                ),
              ),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Padding(
                  padding: const EdgeInsets.only(top: AppSpacing.s2),
                  child: Icon(
                    Icons.format_quote,
                    size: AppSpacing.s16,
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                ),
                AppSpacing.w8,
                Expanded(
                  child: Text(
                    l10n.reportQuoteTitle(axis.citedTextQuote!),
                    style: theme.textTheme.bodyMedium?.copyWith(
                      fontStyle: FontStyle.italic,
                      color: theme.colorScheme.onSurface,
                    ),
                  ),
                ),
              ],
            ),
          ),
        if (hasExplanation)
          Container(
            margin: const EdgeInsets.only(top: AppSpacing.s12),
            padding: const EdgeInsets.all(AppSpacing.s12),
            decoration: BoxDecoration(
              color: theme.colorScheme.tertiaryContainer.withValues(alpha: 0.3),
              border: Border(
                left: BorderSide(
                  color: theme.colorScheme.tertiary,
                  width: AppSpacing.s4,
                ),
              ),
              borderRadius: const BorderRadius.only(
                topRight: Radius.circular(AppSpacing.s8),
                bottomRight: Radius.circular(AppSpacing.s8),
              ),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Padding(
                  padding: const EdgeInsets.only(top: AppSpacing.s2),
                  child: Icon(
                    Icons.lightbulb_outline,
                    size: AppSpacing.s16,
                    color: theme.colorScheme.tertiary,
                  ),
                ),
                AppSpacing.w8,
                Expanded(
                  child: Text(
                    l10n.reportSemanticExplanationTitle(
                      axis.semanticReasoning!,
                    ),
                    style: theme.textTheme.bodyMedium?.copyWith(
                      fontStyle: FontStyle.italic,
                      color: theme.colorScheme.onSurface,
                    ),
                  ),
                ),
              ],
            ),
          ),
        if (hasSourceId)
          Padding(
            padding: const EdgeInsets.only(top: AppSpacing.s8),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                Icon(
                  Icons.gavel,
                  size: AppSpacing.s16,
                  color: theme.colorScheme.primary,
                ),
                AppSpacing.w8,
                Expanded(
                  child: Text(
                    l10n.reportFrameworkReference(axis.citedSourceId!),
                    style: theme.textTheme.labelSmall?.copyWith(
                      color: theme.colorScheme.primary,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
          ),
        if (hasWebCitation)
          Container(
            margin: const EdgeInsets.only(top: AppSpacing.s8),
            padding: const EdgeInsets.symmetric(
              horizontal: AppSpacing.s12,
              vertical: AppSpacing.s8,
            ),
            decoration: BoxDecoration(
              color: theme.colorScheme.surfaceContainerHighest.withValues(alpha: 0.5),
              borderRadius: BorderRadius.circular(AppSpacing.s6),
              border: Border.all(
                color: theme.colorScheme.outlineVariant,
              ),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Padding(
                  padding: const EdgeInsets.only(top: AppSpacing.s2),
                  child: Icon(
                    Icons.verified,
                    size: AppSpacing.s16,
                    color: theme.colorScheme.primary,
                  ),
                ),
                AppSpacing.w8,
                Expanded(
                  child: Text(
                    l10n.reportGoogleVerified(axis.citedWebCitation!),
                    style: theme.textTheme.labelSmall?.copyWith(
                      color: theme.colorScheme.onSurface,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
              ],
            ),
          ),
      ],
    );
  }

  Widget _buildTelemetryGrid(BuildContext context) {
    if (textDeliveryMode != TextDeliveryMode.full) {
      return const SizedBox();
    }

    final hasConfidence = axis.confidence != null;
    final hasCoaching =
        axis.coaching != null && axis.coaching!.trim().isNotEmpty;
    final hasFalsification =
        axis.falsification != null && axis.falsification!.trim().isNotEmpty;
    final hasRemediation =
        axis.remediationSteps != null &&
        axis.remediationSteps!.trim().isNotEmpty;

    if (!hasConfidence &&
        !hasCoaching &&
        !hasFalsification &&
        !hasRemediation) {
      return const SizedBox();
    }

    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      mainAxisSize: MainAxisSize.min,
      children: [
        if (hasConfidence)
          Padding(
            padding: const EdgeInsets.only(bottom: AppSpacing.s8),
            child: Text(
              l10n.reportConfidenceTitle(
                (axis.confidence! * 100).toStringAsFixed(0),
              ),
              style: theme.textTheme.labelSmall?.copyWith(
                fontWeight: FontWeight.bold,
                color: theme.colorScheme.primary,
              ),
            ),
          ),
        if (hasCoaching)
          Padding(
            padding: const EdgeInsets.only(bottom: AppSpacing.s8),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Padding(
                  padding: const EdgeInsets.only(top: AppSpacing.s2),
                  child: Icon(
                    Icons.lightbulb_outline,
                    size: AppSpacing.s16,
                    color: theme.colorScheme.primary,
                  ),
                ),
                AppSpacing.w8,
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        l10n.reportCoachingTitle,
                        style: theme.textTheme.labelSmall?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Text(axis.coaching!, style: theme.textTheme.bodySmall),
                    ],
                  ),
                ),
              ],
            ),
          ),
        if (hasFalsification)
          Padding(
            padding: const EdgeInsets.only(bottom: AppSpacing.s8),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Padding(
                  padding: const EdgeInsets.only(top: AppSpacing.s2),
                  child: Icon(
                    Icons.gavel,
                    size: AppSpacing.s16,
                    color: theme.colorScheme.tertiary,
                  ),
                ),
                AppSpacing.w8,
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        l10n.reportFalsificationTitle,
                        style: theme.textTheme.labelSmall?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Text(
                        axis.falsification!,
                        style: theme.textTheme.bodySmall,
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        if (hasRemediation)
          Padding(
            padding: const EdgeInsets.only(bottom: AppSpacing.s8),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Padding(
                  padding: const EdgeInsets.only(top: AppSpacing.s2),
                  child: Icon(
                    Icons.build,
                    size: AppSpacing.s16,
                    color: theme.colorScheme.primary,
                  ),
                ),
                AppSpacing.w8,
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        l10n.reportRemediationStepsTitle,
                        style: theme.textTheme.labelSmall?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Text(
                        axis.remediationSteps!,
                        style: theme.textTheme.bodySmall,
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
      ],
    );
  }

  Widget _buildEvidenceIcon(BuildContext context, EvidenceType type) {
    final theme = Theme.of(context);
    return switch (type) {
      EvidenceType.explicitQuote => Icon(
        Icons.check_circle,
        color: theme.colorScheme.primary,
        size: AppSpacing.s16,
      ),
      EvidenceType.impliedIntent => Icon(
        Icons.warning,
        color: theme.colorScheme.tertiary,
        size: AppSpacing.s16,
      ),
      EvidenceType.noEvidence => Icon(
        Icons.cancel,
        color: theme.colorScheme.error,
        size: AppSpacing.s16,
      ),
    };
  }
}
