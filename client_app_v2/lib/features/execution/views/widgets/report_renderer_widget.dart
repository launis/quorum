import 'package:flutter/material.dart';
import 'package:client_app/features/execution/models/report_data_dto.dart';
import 'package:client_app/shared/widgets/logic_matrix_chart.dart';
import 'package:client_app/shared/widgets/score_card_radar.dart';

/// Static MVC View Renderer mapping exactly to the workflow preset views.
/// Adheres to the De-Generator Zero-Math rule natively traversing the array.
class ReportRendererWidget extends StatelessWidget {
  final ReportDataDTO payload;

  const ReportRendererWidget({super.key, required this.payload});

  @override
  Widget build(BuildContext context) {
    if (payload.layouts.isEmpty) {
      return const Center(
        child: Padding(
          padding: EdgeInsets.all(24.0),
          child: Text(
            'Tyhjä profiili (No layout blocks defined)',
            style: TextStyle(color: Colors.grey),
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
        ...payload.layouts.map(
          (layout) => _buildLayoutSequence(context, layout),
        ),
      ],
    );
  }

  Widget _buildMetadataHeaderBox(BuildContext context) {
    final defaultOrgName = payload.orgName ?? "Tuntematon organisaatio";
    final profileNameStr =
        payload.profileName['fi'] ??
        payload.profileName['en'] ??
        payload.profileId;

    // Formatting cost
    final costStr =
        payload.costEstimate != null
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
              "Aihe & Profiili: $profileNameStr",
              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),

            // KONTEKSTI
            Text(
              "Konteksti: $defaultOrgName",
              style: TextStyle(color: Colors.grey.shade800),
            ),
            if (payload.createdAt != null)
              Text(
                "Aikaleima: ${payload.createdAt}",
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
                      const Text(
                        "Kustannukset",
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 13,
                        ),
                      ),
                      Text(
                        "API-hinta: $costStr",
                        style: const TextStyle(fontSize: 13),
                      ),
                    ],
                  ),
                ),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        "Kognitiivinen työ (Tokens)",
                        style: TextStyle(
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

  Widget _buildLayoutSequence(BuildContext context, ReportLayoutDTO layout) {
    if (layout.axes.isEmpty) return const SizedBox.shrink();

    final lang = Localizations.localeOf(context).languageCode;
    final title =
        layout.title[lang] ?? layout.title['en'] ?? layout.title['fi'];
    final desc =
        layout.description[lang] ??
        layout.description['en'] ??
        layout.description['fi'];

    Widget content;
    switch (layout.presetView) {
      case '1d_metrics':
        content = _build1DMetrics(layout);
        break;
      case '2d_compare':
        content = _build2DCompare(layout);
        break;
      case '3d_complex':
        content = _build3DComplex(layout);
        break;
      case 'text_only':
        content = _buildWip('Teksti / Synteesi');
        break;
      default:
        // Graceful degradation fallback
        content = _build1DMetrics(layout);
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

  Widget _build1DMetrics(ReportLayoutDTO layout) {
    if (layout.axes.isEmpty) return const SizedBox.shrink();

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
                          if (layout.showText)
                            Text(
                              axis.justification,
                              style: const TextStyle(
                                fontSize: 14,
                                color: Colors.black87,
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
                                "💬 Ote alkuperäisestä tekstistä:\n${axis.citedTextQuote}",
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
                                "⚖️ Viitekehys: ${axis.citedSourceId}",
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
                                      "Tarkistettu Googlen lähteistä:\n${axis.citedWebCitation}",
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
                        '${axis.score}',
                        style: const TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                          color: Colors.blue,
                        ),
                      ),
                    ),
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

  Widget _build2DCompare(ReportLayoutDTO layout) {
    if (layout.axes.length < 2) return _build1DMetrics(layout);

    final dimensions =
        layout.axes
            .map(
              (a) => {
                'dimensionLabel': a.name,
                'score': a.score,
                'reasoning': a.justification,
              },
            )
            .toList();

    double total = layout.axes.fold(0.0, (sum, item) => sum + item.score);

    return Column(
      children: [
        ScoreCardRadar(
          cardData: {
            'agentName': 'Tutka-analyysi (2D)',
            'verdict': 'Vertailunäkymä',
            'totalScore': total / layout.axes.length,
            'dimensions': dimensions,
          },
        ),
        _build1DMetrics(layout),
      ],
    );
  }

  Widget _build3DComplex(ReportLayoutDTO layout) {
    if (layout.axes.length < 2) return _build1DMetrics(layout);

    final String title =
        layout.axes.length > 2
            ? "Analyyttinen Viitekehys (3D)"
            : "Analyyttinen Viitekehys (2D)";

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
                  zAxis: layout.axes.length > 2 ? layout.axes[2] : null,
                ),
              ],
            ),
          ),
        ),
        _build1DMetrics(layout),
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
