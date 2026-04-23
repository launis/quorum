import 'package:flutter/material.dart';
import 'package:client_app/features/execution/models/report_data_dto.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

class XAIAxisTelemetryGrid extends StatelessWidget {
  final ReportAxisDTO axis;
  final String textDeliveryMode;
  final bool showQuote;

  const XAIAxisTelemetryGrid({
    super.key,
    required this.axis,
    required this.textDeliveryMode,
    required this.showQuote,
  });

  @override
  Widget build(BuildContext context) {
    if (textDeliveryMode == 'none') {
      return const SizedBox.shrink();
    }

    return LayoutBuilder(
      builder: (context, constraints) {
        if (constraints.maxWidth >= 800) {
          return Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(flex: 3, child: _buildMainContent(context)),
              const SizedBox(width: 24),
              Expanded(flex: 2, child: _buildTelemetryGrid(context)),
            ],
          );
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
      },
    );
  }

  Widget _buildMainContent(BuildContext context) {
    final hasJustification =
        axis.justification != null && axis.justification!.trim().isNotEmpty;
    final hasQuote = showQuote;
    final hasWebCitation =
        axis.citedWebCitation != null && axis.citedWebCitation!.isNotEmpty;
    final hasSourceId =
        axis.citedSourceId != null && axis.citedSourceId!.isNotEmpty;

    if (!hasJustification && !hasQuote && !hasWebCitation && !hasSourceId) {
      return const SizedBox.shrink();
    }

    final l10n = AppLocalizations.of(context)!;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: [
        if (hasJustification)
          Text(
            axis.justification!,
            style: const TextStyle(fontSize: 14, color: Colors.black87),
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
      return const SizedBox.shrink();
    }

    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);

    final List<Widget> boxes = [];

    if (axis.confidence != null) {
      boxes.add(
        Padding(
          padding: const EdgeInsets.only(bottom: 8.0),
          child: Text(
            l10n.reportConfidenceTitle(axis.confidence!.toStringAsFixed(1)),
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

    if (axis.coaching != null && axis.coaching!.isNotEmpty) {
      boxes.add(
        _buildBox(
          title: l10n.reportCoachingTitle,
          content: axis.coaching!,
          color: Colors.amber,
        ),
      );
    }

    if (axis.falsification != null && axis.falsification!.isNotEmpty) {
      boxes.add(
        _buildBox(
          title: l10n.reportFalsificationTitle,
          content: axis.falsification!,
          color: Colors.deepPurple,
          contentFontStyle: FontStyle.italic,
        ),
      );
    }

    if (axis.missingContext != null && axis.missingContext!.isNotEmpty) {
      boxes.add(
        _buildBox(
          title: l10n.reportMissingContextTitle,
          content: axis.missingContext!,
          color: Colors.grey,
          titleColor: Colors.black54,
        ),
      );
    }

    if (axis.remediationSteps != null && axis.remediationSteps!.isNotEmpty) {
      boxes.add(
        _buildBox(
          title: l10n.reportRemediationStepsTitle,
          content: '- ${axis.remediationSteps!.join('\\n- ')}',
          color: Colors.teal,
        ),
      );
    }

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
      return const SizedBox.shrink();
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      mainAxisSize: MainAxisSize.min,
      children: boxes,
    );
  }

  Widget _buildBox({
    required String title,
    required String content,
    required MaterialColor color,
    Color? titleColor,
    FontStyle? contentFontStyle,
  }) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12.0),
      padding: const EdgeInsets.all(12.0),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        border: Border(left: BorderSide(color: color.shade700, width: 4)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            title,
            style: TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: 12,
              color: titleColor ?? color.shade800,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            content,
            style: TextStyle(
              fontSize: 14,
              color: Colors.black87,
              fontStyle: contentFontStyle,
            ),
          ),
        ],
      ),
    );
  }
}
