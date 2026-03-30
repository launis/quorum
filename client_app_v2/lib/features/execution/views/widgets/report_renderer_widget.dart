import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/execution/models/report_data_dto.dart';
import 'package:client_app/shared/widgets/logic_matrix_chart.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/features/execution/views/widgets/xai_evidence_box.dart';
import 'package:client_app/core/ui/error_view.dart';

/// Static MVC View Renderer mapping exactly to the workflow preset views.
/// Adheres to the De-Generator Zero-Math rule natively traversing the array.
class ReportRendererWidget extends ConsumerWidget {
  final ReportDataDTO payload;

  const ReportRendererWidget({super.key, required this.payload});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    if (payload.layouts.isEmpty) {
      final l10n = AppLocalizations.of(context)!;
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Text(
            l10n.reportEmptyProfile,
            style: const TextStyle(color: Colors.grey),
          ),
        ),
      );
    }

    return ListView(
      padding: EdgeInsets.zero,
      shrinkWrap: true,
      primary: false,
      children: [
        _buildMetadataHeaderBox(context),
        if (payload.globalScore != null) _buildGlobalScoreBadge(context),
        ...payload.layouts.map(
          (layout) => _buildLayoutSequence(context, ref, layout),
        ),
        // XAI Evidence Box — only renders when MCP tool searches were executed
        if (payload.mcpToolAudit.isNotEmpty)
          XAIEvidenceBox(auditTraces: payload.mcpToolAudit),
      ],
    );
  }

  Widget _buildMetadataHeaderBox(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final defaultOrgName = payload.orgName ?? l10n.reportUnknownOrg;
    final lang = Localizations.localeOf(context).languageCode;
    final profileNameStr = payload.profileName?.get(lang) ?? payload.profileId;

    // Formatting cost
    final costStr = payload.costEstimate != null
        ? '\$${payload.costEstimate!.toStringAsFixed(4)}'
        : '-';

    return Card(
      elevation: 3,
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // AIHE & PROFIILI
            Text(
              l10n.reportTopicProfile(profileNameStr),
              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),

            // KONTEKSTI
            Text(
              l10n.reportContext(defaultOrgName),
              style: TextStyle(color: Colors.grey.shade800),
            ),
            if (payload.createdAt != null)
              Text(
                l10n.reportTimestamp(payload.createdAt.toString()),
                style: TextStyle(color: Colors.grey.shade600, fontSize: 13),
              ),

            const Divider(height: 24),

            // KUSTANNUKSET & KOGNITIIVINEN TYÖ
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        l10n.reportCosts,
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 13,
                        ),
                      ),
                      Text(
                        l10n.reportApiPrice(costStr),
                        style: const TextStyle(fontSize: 13),
                      ),
                    ],
                  ),
                ),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        l10n.reportCognitiveWork,
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 13,
                        ),
                      ),
                      Text(
                        "Prompt: ${payload.promptTokens ?? '-'}",
                        style: const TextStyle(fontSize: 13),
                      ),
                      Text(
                        "Completion: ${payload.completionTokens ?? '-'}",
                        style: const TextStyle(fontSize: 13),
                      ),
                      Text(
                        "Reasoning: ${payload.reasoningTokens ?? '-'}",
                        style: const TextStyle(fontSize: 13),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildGlobalScoreBadge(BuildContext context) {
    if (payload.globalScore == null) return const SizedBox.shrink();

    final l10n = AppLocalizations.of(context)!;

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.green.shade50,
        border: Border.all(color: Colors.green, width: 2),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        children: [
          Text(
            l10n.reportScore.toUpperCase(),
            style: TextStyle(
              color: Colors.green.shade800,
              fontSize: 14,
              fontWeight: FontWeight.bold,
              letterSpacing: 1.2,
            ),
          ),
          const SizedBox(height: 8),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.baseline,
            textBaseline: TextBaseline.alphabetic,
            children: [
              Text(
                payload.globalScore!.toStringAsFixed(1),
                style: TextStyle(
                  color: Colors.green.shade900,
                  fontSize: 42,
                  fontWeight: FontWeight.w900,
                ),
              ),
              const SizedBox(width: 8),
              Text(
                '/ 100',
                style: TextStyle(
                  color: Colors.green.shade700,
                  fontSize: 20,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildLayoutSequence(
    BuildContext context,
    WidgetRef ref,
    ReportLayoutDTO layout,
  ) {
    if (layout.axes.isEmpty) return const SizedBox.shrink();

    final l10n = AppLocalizations.of(context)!;
    final lang = Localizations.localeOf(context).languageCode;
    final title = layout.title?.get(lang);
    final desc = layout.description?.get(lang);

    Widget content;
    try {
      switch (layout.presetView) {
        case '1d_metrics':
          content = _build1DMetrics(context, layout);
          break;
        case '2d_compare':
          content = _build2DCompare(context, layout);
          break;
        case '3d_complex':
          content = _build3DComplex(context, layout);
          break;
        case 'text_only':
          content = _buildWip(l10n.reportTextSynthesis);
          break;
        default:
          // Graceful degradation fallback
          content = _build1DMetrics(context, layout);
      }
    } catch (e, st) {
      ref
          .read(loggerServiceProvider)
          .error(
            'ReportRenderer',
            'VALIDATION_FAILED: Widget render error',
            e,
            st,
          );
      return ErrorView(error: e, stackTrace: st, compact: true);
    }

    if ((title != null && title.isNotEmpty) ||
        (desc != null && desc.isNotEmpty)) {
      return Padding(
        padding: const EdgeInsets.only(
          top: 32.0,
          bottom: 8.0,
          left: 16.0,
          right: 16.0,
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (title != null && title.isNotEmpty)
              Text(
                title,
                style: const TextStyle(
                  fontSize: 22,
                  fontWeight: FontWeight.bold,
                  letterSpacing: -0.5,
                ),
              ),
            if (desc != null && desc.isNotEmpty) ...[
              const SizedBox(height: 8),
              Text(
                desc,
                style: TextStyle(
                  fontSize: 15,
                  color: Colors.grey.shade700,
                  height: 1.4,
                ),
              ),
            ],
            const SizedBox(height: 16),
            content,
          ],
        ),
      );
    }

    return content;
  }

  Widget _build1DMetrics(BuildContext context, ReportLayoutDTO layout) {
    if (layout.axes.isEmpty) return const SizedBox.shrink();

    final l10n = AppLocalizations.of(context)!;
    final Set<String> seenQuotes = {};
    final List<bool> shouldShowQuote = [];
    for (var axis in layout.axes) {
      if (axis.citedTextQuote != null && axis.citedTextQuote!.isNotEmpty) {
        final norm = axis.citedTextQuote!.toLowerCase().trim();
        if (seenQuotes.contains(norm)) {
          shouldShowQuote.add(false);
        } else {
          seenQuotes.add(norm);
          shouldShowQuote.add(true);
        }
      } else {
        shouldShowQuote.add(false);
      }
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      mainAxisSize: MainAxisSize.min,
      children: [
        ListView.builder(
          padding: const EdgeInsets.all(16.0),
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: layout.axes.length,
          itemBuilder: (context, index) {
            final axis = layout.axes[index];
            return Card(
              elevation: 2,
              margin: const EdgeInsets.only(bottom: 12.0),
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            axis.name,
                            style: const TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          if (axis.description != null &&
                              axis.description!.isNotEmpty) ...[
                            const SizedBox(height: 4),
                            Text(
                              axis.description!,
                              style: TextStyle(
                                fontSize: 14,
                                color: Colors.grey.shade700,
                                fontStyle: FontStyle.italic,
                              ),
                            ),
                          ],
                          const SizedBox(height: 8),
                          if (layout.showText &&
                              axis.justification.trim().isNotEmpty)
                            Text(
                              axis.justification,
                              style: const TextStyle(
                                fontSize: 14,
                                color: Colors.black87,
                              ),
                            ),

                          if (layout.showText && axis.confidence != null)
                            Padding(
                              padding: const EdgeInsets.only(top: 8.0),
                              child: Text(
                                l10n.reportConfidenceTitle(
                                  axis.confidence!.toStringAsFixed(1),
                                ),
                                style: const TextStyle(
                                  fontWeight: FontWeight.bold,
                                  color: Colors.indigo,
                                  fontSize: 12,
                                ),
                              ),
                            ),

                          if (layout.showText && axis.riskFlag == true)
                            Container(
                              margin: const EdgeInsets.only(top: 8.0),
                              padding: const EdgeInsets.symmetric(
                                horizontal: 8,
                                vertical: 4,
                              ),
                              decoration: BoxDecoration(
                                color: Colors.red.withValues(alpha: 0.1),
                                borderRadius: BorderRadius.circular(4),
                              ),
                              child: Text(
                                l10n.reportRiskFlagTitle,
                                style: const TextStyle(
                                  fontWeight: FontWeight.bold,
                                  color: Colors.red,
                                  fontSize: 12,
                                ),
                              ),
                            ),

                          if (layout.showText &&
                              axis.coaching != null &&
                              axis.coaching!.isNotEmpty)
                            Container(
                              margin: const EdgeInsets.only(top: 12.0),
                              padding: const EdgeInsets.all(12.0),
                              decoration: BoxDecoration(
                                color: Colors.amber.withValues(alpha: 0.1),
                                border: Border(
                                  left: BorderSide(
                                    color: Colors.amber.shade700,
                                    width: 4,
                                  ),
                                ),
                              ),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    l10n.reportCoachingTitle,
                                    style: TextStyle(
                                      fontWeight: FontWeight.bold,
                                      fontSize: 12,
                                      color: Colors.amber.shade800,
                                    ),
                                  ),
                                  const SizedBox(height: 4),
                                  Text(
                                    axis.coaching!,
                                    style: const TextStyle(
                                      fontSize: 14,
                                      color: Colors.black87,
                                    ),
                                  ),
                                ],
                              ),
                            ),

                          if (layout.showText &&
                              axis.falsification != null &&
                              axis.falsification!.isNotEmpty)
                            Container(
                              margin: const EdgeInsets.only(top: 12.0),
                              padding: const EdgeInsets.all(12.0),
                              decoration: BoxDecoration(
                                color: Colors.deepPurple.withValues(
                                  alpha: 0.05,
                                ),
                                border: Border(
                                  left: BorderSide(
                                    color: Colors.deepPurple.shade400,
                                    width: 4,
                                  ),
                                ),
                              ),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    l10n.reportFalsificationTitle,
                                    style: TextStyle(
                                      fontWeight: FontWeight.bold,
                                      fontSize: 12,
                                      color: Colors.deepPurple.shade600,
                                    ),
                                  ),
                                  const SizedBox(height: 4),
                                  Text(
                                    axis.falsification!,
                                    style: const TextStyle(
                                      fontSize: 14,
                                      fontStyle: FontStyle.italic,
                                      color: Colors.black87,
                                    ),
                                  ),
                                ],
                              ),
                            ),

                          if (layout.showText &&
                              axis.missingContext != null &&
                              axis.missingContext!.isNotEmpty)
                            Container(
                              margin: const EdgeInsets.only(top: 12.0),
                              padding: const EdgeInsets.all(12.0),
                              decoration: BoxDecoration(
                                color: Colors.grey.withValues(alpha: 0.1),
                                border: const Border(
                                  left: BorderSide(
                                    color: Colors.grey,
                                    width: 4,
                                  ),
                                ),
                              ),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    l10n.reportMissingContextTitle,
                                    style: const TextStyle(
                                      fontWeight: FontWeight.bold,
                                      fontSize: 12,
                                      color: Colors.black54,
                                    ),
                                  ),
                                  const SizedBox(height: 4),
                                  Text(
                                    axis.missingContext!,
                                    style: const TextStyle(
                                      fontSize: 14,
                                      color: Colors.black87,
                                    ),
                                  ),
                                ],
                              ),
                            ),

                          if (layout.showText &&
                              axis.remediationSteps != null &&
                              axis.remediationSteps!.isNotEmpty)
                            Container(
                              margin: const EdgeInsets.only(top: 12.0),
                              padding: const EdgeInsets.all(12.0),
                              decoration: BoxDecoration(
                                color: Colors.teal.withValues(alpha: 0.1),
                                border: const Border(
                                  left: BorderSide(
                                    color: Colors.teal,
                                    width: 4,
                                  ),
                                ),
                              ),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    l10n.reportRemediationStepsTitle,
                                    style: const TextStyle(
                                      fontWeight: FontWeight.bold,
                                      fontSize: 12,
                                      color: Colors.teal,
                                    ),
                                  ),
                                  const SizedBox(height: 4),
                                  Text(
                                    '- ${axis.remediationSteps!.join('\\n- ')}',
                                    style: const TextStyle(
                                      fontSize: 14,
                                      color: Colors.black87,
                                    ),
                                  ),
                                ],
                              ),
                            ),

                          if (layout.showText &&
                              axis.emotionalSentiment != null &&
                              axis.emotionalSentiment!.isNotEmpty)
                            Padding(
                              padding: const EdgeInsets.only(top: 12.0),
                              child: Text(
                                '${l10n.reportEmotionalSentimentTitle}: ${axis.emotionalSentiment!}',
                                style: const TextStyle(
                                  fontSize: 13,
                                  fontStyle: FontStyle.italic,
                                  color: Colors.pink,
                                ),
                              ),
                            ),

                          if (layout.showText &&
                              axis.theoryLink != null &&
                              axis.theoryLink!.isNotEmpty)
                            Padding(
                              padding: const EdgeInsets.only(top: 8.0),
                              child: Text(
                                '${l10n.reportTheoryLinkTitle}: ${axis.theoryLink!}',
                                style: const TextStyle(
                                  fontSize: 13,
                                  color: Colors.blue,
                                ),
                              ),
                            ),

                          if (layout.showText && shouldShowQuote[index])
                            Container(
                              margin: const EdgeInsets.only(top: 12.0),
                              padding: const EdgeInsets.all(12.0),
                              decoration: BoxDecoration(
                                color: Colors.grey.withValues(alpha: 0.1),
                                border: const Border(
                                  left: BorderSide(
                                    color: Colors.grey,
                                    width: 4,
                                  ),
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
                          if (layout.showText &&
                              axis.citedSourceId != null &&
                              axis.citedSourceId!.isNotEmpty)
                            Padding(
                              padding: const EdgeInsets.only(top: 8.0),
                              child: Text(
                                l10n.reportFrameworkReference(
                                  axis.citedSourceId!,
                                ),
                                style: const TextStyle(
                                  fontSize: 12,
                                  color: Colors.blueGrey,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ),
                          if (layout.showText &&
                              axis.citedWebCitation != null &&
                              axis.citedWebCitation!.isNotEmpty)
                            Container(
                              margin: const EdgeInsets.only(top: 8.0),
                              padding: const EdgeInsets.symmetric(
                                horizontal: 12.0,
                                vertical: 8.0,
                              ),
                              decoration: BoxDecoration(
                                color: Colors.green.withValues(alpha: 0.1),
                                borderRadius: BorderRadius.circular(6),
                                border: Border.all(
                                  color: Colors.green.withValues(alpha: 0.3),
                                ),
                              ),
                              child: Row(
                                mainAxisSize: MainAxisSize.min,
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  const Padding(
                                    padding: EdgeInsets.only(top: 2.0),
                                    child: Icon(
                                      Icons.verified,
                                      size: 16,
                                      color: Colors.green,
                                    ),
                                  ),
                                  const SizedBox(width: 8),
                                  Expanded(
                                    child: Text(
                                      l10n.reportGoogleVerified(
                                        axis.citedWebCitation!,
                                      ),
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
                      ),
                    ),
                    if (axis.score != null) ...[
                      const SizedBox(width: 16),
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 16,
                          vertical: 8,
                        ),
                        decoration: BoxDecoration(
                          color: Colors.blue.withValues(alpha: 0.1),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Text(
                          axis.scaleMax > axis.scaleMin
                              ? '${axis.score} / ${axis.scaleMax}'
                              : '${axis.score}',
                          style: const TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                            color: Colors.blue,
                          ),
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            );
          },
        ),
        const Divider(),
      ],
    );
  }

  Widget _build2DCompare(BuildContext context, ReportLayoutDTO layout) {
    if (layout.axes.length < 2) {
      return _build1DMetrics(context, layout);
    }

    final l10n = AppLocalizations.of(context)!;

    return Column(
      children: [
        Card(
          elevation: 2,
          margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              children: [
                Text(
                  l10n.reportInteractionMatrix2D,
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 16),
                LogicMatrixChart(
                  xAxis: layout.axes[0],
                  yAxis: layout.axes[1],
                  zAxis: null,
                ),
              ],
            ),
          ),
        ),
        _build1DMetrics(context, layout),
      ],
    );
  }

  Widget _build3DComplex(BuildContext context, ReportLayoutDTO layout) {
    if (layout.axes.length < 2) {
      return _build1DMetrics(context, layout);
    }

    final l10n = AppLocalizations.of(context)!;
    final String title = layout.axes.length > 2
        ? l10n.reportAnalyticalFramework3D
        : l10n.reportAnalyticalFramework2D;

    return Column(
      children: [
        Card(
          elevation: 2,
          margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 16),
                LogicMatrixChart(
                  xAxis: layout.axes[0],
                  yAxis: layout.axes[1],
                  zAxis: layout.axes.length >= 3 ? layout.axes[2] : null,
                ),
              ],
            ),
          ),
        ),
        _build1DMetrics(context, layout),
      ],
    );
  }

  Widget _buildWip(String name) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Text(
          '$name (Static Placeholder)',
          style: const TextStyle(
            fontStyle: FontStyle.italic,
            color: Colors.grey,
          ),
        ),
      ),
    );
  }
}
