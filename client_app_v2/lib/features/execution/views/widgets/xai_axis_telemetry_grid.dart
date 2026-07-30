import 'package:flutter/material.dart';
import 'package:client_app/features/execution/models/matrix_scorecard_dto.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/theme/app_colors.dart';

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
              color: AppColors.intentNeutral.withValues(alpha: 0.1),
              border: const Border(
                left: BorderSide(
                  color: AppColors.intentNeutral,
                  width: AppSpacing.s4,
                ),
              ),
            ),
            child: Text(
              l10n.reportQuoteTitle(axis.citedTextQuote!),
              style: theme.textTheme.bodyMedium?.copyWith(
                fontStyle: FontStyle.italic,
                color: theme.colorScheme.onSurface,
              ),
            ),
          ),
        if (hasExplanation)
          Container(
            margin: const EdgeInsets.only(top: AppSpacing.s12),
            padding: const EdgeInsets.all(AppSpacing.s12),
            decoration: BoxDecoration(
              color: AppColors.intentWarning.withValues(alpha: 0.1),
              border: const Border(
                left: BorderSide(
                  color: AppColors.intentWarning,
                  width: AppSpacing.s4,
                ),
              ),
              borderRadius: const BorderRadius.only(
                topRight: Radius.circular(AppSpacing.s8),
                bottomRight: Radius.circular(AppSpacing.s8),
              ),
            ),
            child: Text(
              l10n.reportSemanticExplanationTitle(axis.semanticReasoning!),
              style: theme.textTheme.bodyMedium?.copyWith(
                fontStyle: FontStyle.italic,
                color: theme.colorScheme.onSurface,
              ),
            ),
          ),
        if (hasSourceId)
          Padding(
            padding: const EdgeInsets.only(top: AppSpacing.s8),
            child: Text(
              l10n.reportFrameworkReference(axis.citedSourceId!),
              style: theme.textTheme.labelSmall?.copyWith(
                color: AppColors.intentInfo,
                fontWeight: FontWeight.bold,
              ),
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
              color: AppColors.intentSuccess.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(AppSpacing.s6),
              border: Border.all(
                color: AppColors.intentSuccess.withValues(alpha: 0.3),
              ),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Padding(
                  padding: EdgeInsets.only(top: AppSpacing.s2),
                  child: Icon(
                    Icons.verified,
                    size: AppSpacing.s16,
                    color: AppColors.intentSuccess,
                  ),
                ),
                AppSpacing.w8,
                Expanded(
                  child: Text(
                    l10n.reportGoogleVerified(axis.citedWebCitation!),
                    style: theme.textTheme.labelSmall?.copyWith(
                      color: AppColors.intentSuccess,
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

    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);

    final List<Widget> boxes = [];

    if (axis.confidence != null) {
      boxes.add(
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
      );
    }

    if (boxes.isEmpty) {
      return const SizedBox();
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      mainAxisSize: MainAxisSize.min,
      children: boxes,
    );
  }

  Widget _buildEvidenceIcon(BuildContext context, EvidenceType type) {
    final theme = Theme.of(context);
    return switch (type) {
      EvidenceType.explicitQuote => const Icon(
        Icons.check_circle,
        color: AppColors.intentSuccess,
        size: AppSpacing.s16,
      ),
      EvidenceType.impliedIntent => const Icon(
        Icons.warning,
        color: AppColors.intentWarning,
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
