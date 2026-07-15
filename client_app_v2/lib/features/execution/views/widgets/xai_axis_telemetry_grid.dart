import 'package:flutter/material.dart';
import 'package:client_app/features/execution/models/matrix_scorecard_dto.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/models/enums.dart';

class XAIAxisTelemetryGrid extends StatelessWidget {
  final MatrixScorecardRowDto axis;
  final String textDeliveryMode;
  final bool showQuote;
  final Map<String, List<dynamic>> groupedExtensions;

  const XAIAxisTelemetryGrid({
    super.key,
    required this.axis,
    required this.textDeliveryMode,
    required this.showQuote,
    required this.groupedExtensions,
  });

  @override
  Widget build(BuildContext context) {
    if (textDeliveryMode == 'none') {
      return const SizedBox();
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      mainAxisSize: MainAxisSize.min,
      children: [
        _buildMainContent(context),
        const SizedBox(height: 12),
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
    final hasQuote = showQuote && !isOverride;
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
                  padding: const EdgeInsets.only(top: 2.0, right: 8.0),
                  child: _buildEvidenceIcon(axis.evidenceType!),
                ),
              ],
              Expanded(
                child: Text(
                  axis.rowExplanation,
                  style: const TextStyle(fontSize: 14, color: Colors.black87),
                ),
              ),
            ],
          ),
        if (hasQuote)
          Container(
            margin: const EdgeInsets.only(top: 12.0),
            padding: const EdgeInsets.all(12.0),
            decoration: BoxDecoration(
              color: Colors.grey.withValues(alpha: 0.1),
              border: const Border(
                left: BorderSide(color: Colors.grey, width: 4),
              ),
            ),
            child: Text(
              l10n.reportQuoteTitle(axis.citedTextQuote!),
              style: const TextStyle(
                fontSize: 14,
                fontStyle: FontStyle.italic,
                color: Colors.black87,
              ),
            ),
          ),
        if (hasExplanation)
          Container(
            margin: const EdgeInsets.only(top: 12.0),
            padding: const EdgeInsets.all(12.0),
            decoration: BoxDecoration(
              color: Colors.orange.withValues(alpha: 0.1),
              border: const Border(
                left: BorderSide(color: Colors.orange, width: 4),
              ),
              borderRadius: const BorderRadius.only(
                topRight: Radius.circular(8.0),
                bottomRight: Radius.circular(8.0),
              ),
            ),
            child: Text(
              l10n.reportSemanticExplanationTitle(axis.semanticReasoning!),
              style: const TextStyle(
                fontSize: 14,
                fontStyle: FontStyle.italic,
                color: Colors.black87,
              ),
            ),
          ),
        if (hasSourceId)
          Padding(
            padding: const EdgeInsets.only(top: 8.0),
            child: Text(
              l10n.reportFrameworkReference(axis.citedSourceId!),
              style: const TextStyle(
                fontSize: 12,
                color: Colors.blueGrey,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        if (hasWebCitation)
          Container(
            margin: const EdgeInsets.only(top: 8.0),
            padding: const EdgeInsets.symmetric(
              horizontal: 12.0,
              vertical: 8.0,
            ),
            decoration: BoxDecoration(
              color: Colors.green.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(6),
              border: Border.all(color: Colors.green.withValues(alpha: 0.3)),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Padding(
                  padding: EdgeInsets.only(top: 2.0),
                  child: Icon(Icons.verified, size: 16, color: Colors.green),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    l10n.reportGoogleVerified(axis.citedWebCitation!),
                    style: const TextStyle(
                      fontSize: 12,
                      color: Colors.green,
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
    if (textDeliveryMode != 'full') {
      return const SizedBox();
    }

    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);

    final List<Widget> boxes = [];

    if (axis.confidence != null &&
        groupedExtensions.containsKey('confidence')) {
      boxes.add(
        Padding(
          padding: const EdgeInsets.only(bottom: 8.0),
          child: Text(
            l10n.reportConfidenceTitle(
              (axis.confidence! * 100).toStringAsFixed(0),
            ),
            style: const TextStyle(
              fontWeight: FontWeight.bold,
              color: Colors.indigo,
              fontSize: 12,
            ),
          ),
        ),
      );
    }

    if (axis.riskFlag == true) {
      boxes.add(
        Container(
          margin: const EdgeInsets.only(bottom: 12.0),
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            color: theme.colorScheme.errorContainer,
            borderRadius: BorderRadius.circular(4),
          ),
          child: Text(
            l10n.reportRiskFlagTitle,
            style: TextStyle(
              fontWeight: FontWeight.bold,
              color: theme.colorScheme.onErrorContainer,
              fontSize: 12,
            ),
          ),
        ),
      );
    }

    // Epic 10: Preserve in Payload, Hide in View.
    // User Mandate: XAI extensions (Coaching, Falsification, etc.) are never rendered
    // at the fragmented matrix level in the UI. They are strictly reserved for the global synthesis block.
    // The data remains intact within the ScorecardRow DTO for API JSON exports.

    if (axis.emotionalSentiment != null &&
        axis.emotionalSentiment!.isNotEmpty) {
      boxes.add(
        Padding(
          padding: const EdgeInsets.only(bottom: 12.0),
          child: Text(
            '${l10n.reportEmotionalSentimentTitle}: ${axis.emotionalSentiment!}',
            style: const TextStyle(
              fontSize: 13,
              fontStyle: FontStyle.italic,
              color: Colors.pink,
            ),
          ),
        ),
      );
    }

    if (axis.theoryLink != null && axis.theoryLink!.isNotEmpty) {
      boxes.add(
        Padding(
          padding: const EdgeInsets.only(bottom: 8.0),
          child: Text(
            '${l10n.reportTheoryLinkTitle}: ${axis.theoryLink!}',
            style: const TextStyle(fontSize: 13, color: Colors.blue),
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

  Widget _buildEvidenceIcon(EvidenceType type) {
    return switch (type) {
      EvidenceType.explicitQuote => const Icon(
        Icons.check_circle,
        color: Colors.green,
        size: 16,
      ),
      EvidenceType.impliedIntent => const Icon(
        Icons.warning,
        color: Colors.orange,
        size: 16,
      ),
      EvidenceType.noEvidence => const Icon(
        Icons.cancel,
        color: Colors.red,
        size: 16,
      ),
    };
  }
}
