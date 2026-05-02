import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/execution/models/report_data_dto.dart';
import 'package:client_app/shared/widgets/logic_matrix_chart.dart';
import 'package:client_app/shared/widgets/logic_radar_chart.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/execution/views/widgets/xai_evidence_box.dart';
import 'package:client_app/features/execution/views/widgets/xai_extensions_box.dart';
import 'package:client_app/features/execution/views/widgets/xai_axis_telemetry_grid.dart';
import 'package:client_app/features/execution/views/widgets/diagnostic_scorecard_widget.dart';

import 'package:client_app/shared/widgets/output_renderer.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/ui/error_view.dart';

/// Static MVC View Renderer mapping exactly to the workflow preset views.
/// Adheres to the De-Generator Zero-Math rule natively traversing the array.
class ReportRendererWidget extends ConsumerWidget {
  final ReportDataDTO payload;
  final String executionId;

  const ReportRendererWidget({
    super.key,
    required this.payload,
    required this.executionId,
  });

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
        if (payload.synthesizedMarkdown != null &&
            payload.synthesizedMarkdown!.isNotEmpty)
          _buildGlobalSynthesisBox(context),

        ...payload.layouts.map(
          (layout) => _buildLayoutSequence(context, ref, layout),
        ),

        // Milestone 4: Render Grouped XAI Extensions
        if (payload.groupedExtensions.isNotEmpty)
          XAIExtensionsBox(groupedExtensions: payload.groupedExtensions),

        // Epic 27: Render Independent Matrix Scorecard directly below extensions
        // V6.1 Parity Fix: This is the 'Appendix' of all matrices, regardless of 3D layout inclusion.
        DiagnosticScorecardWidget(
          globalAverage: payload.globalScore,
          evaluativeMatrices: payload.evaluativeMatrices,
          informationalMatrices: payload.informationalMatrices,
        ),

        // XAI Evidence Box — only renders when MCP tool searches were executed
        if (payload.mcpToolAudit.isNotEmpty)
          XAIEvidenceBox(auditTraces: payload.mcpToolAudit),

        if (payload.penaltiesApplied.isNotEmpty) _buildPenaltiesBox(context),
      ],
    );
  }

  Widget _buildGlobalSynthesisBox(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(
        top: 16.0,
        bottom: 8.0,
        left: 16.0,
        right: 16.0,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            AppLocalizations.of(context)!.reportExecutiveSummary,
            style: const TextStyle(
              fontSize: 22,
              fontWeight: FontWeight.bold,
              letterSpacing: -0.5,
            ),
          ),
          const SizedBox(height: 16),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(16.0),
            decoration: BoxDecoration(
              color: Colors.white,
              border: Border(
                left: BorderSide(
                  color: Theme.of(context).primaryColor,
                  width: 4,
                ),
              ),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withValues(alpha: 0.05),
                  blurRadius: 4,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: OutputRenderer(
              markdownContent: payload.synthesizedMarkdown!,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPenaltiesBox(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.all(16.0),
        decoration: BoxDecoration(
          color: Colors.red.shade50,
          border: Border.all(color: Colors.red.shade200),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              AppLocalizations.of(context)!.reportPenaltiesApplied,
              style: TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.bold,
                color: Colors.red.shade900,
              ),
            ),
            const SizedBox(height: 8),
            ...payload.penaltiesApplied.map(
              (penalty) => Padding(
                padding: const EdgeInsets.only(bottom: 4.0),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Padding(
                      padding: const EdgeInsets.only(top: 4.0, right: 8.0),
                      child: Icon(
                        Icons.warning,
                        size: 12,
                        color: Colors.red.shade700,
                      ),
                    ),
                    Expanded(
                      child: Text(
                        penalty,
                        style: TextStyle(
                          fontSize: 13,
                          color: Colors.red.shade800,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMetadataHeaderBox(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final defaultOrgName = payload.orgName ?? l10n.reportUnknownOrg;
    final lang = Localizations.localeOf(context).languageCode;
    final profileNameStr =
        payload.profileName?.get(lang) ??
        (throw AppException.validation(
          'Fail-Fast: Missing required translation for profileName.',
        ));

    // Formatting cost
    final costStr = payload.costEstimate != null
        ? '\$${payload.costEstimate!.toStringAsFixed(4)}'
        : '-';

    bool isVisible(String key) {
      if (payload.visibleMetadata.isEmpty) return true;
      return payload.visibleMetadata.contains(key);
    }

    final showOrg = isVisible('organization');
    final showDate = isVisible('date');
    final showCost = isVisible('cost');
    final showTokens = isVisible('tokens');

    return Card(
      elevation: 3,
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            // AIHE & PROFIILI
            Text(
              l10n.reportTopicProfile(profileNameStr),
              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),

            // KONTEKSTI
            if (showOrg)
              Text(
                l10n.reportContext(defaultOrgName),
                style: TextStyle(color: Colors.grey.shade800),
              ),
            if (showDate && payload.createdAt != null)
              Text(
                l10n.reportTimestamp(payload.createdAt.toString()),
                style: TextStyle(color: Colors.grey.shade600, fontSize: 13),
              ),

            if (payload.strictnessLevel != null)
              Padding(
                padding: const EdgeInsets.only(top: 8.0),
                child: Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 8,
                    vertical: 4,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.indigo.shade50,
                    borderRadius: BorderRadius.circular(4),
                    border: Border.all(color: Colors.indigo.shade200),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(
                        Icons.balance,
                        size: 14,
                        color: Colors.indigo.shade700,
                      ),
                      const SizedBox(width: 6),
                      Text(
                        '${l10n.strictnessSelectorTitle}: ${_getStrictnessName(context, payload.strictnessLevel!)}',
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.indigo.shade800,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),
              ),

            if (showCost || showTokens) const Divider(height: 24),

            // KUSTANNUKSET & KOGNITIIVINEN TYÖ
            if (showCost || showTokens)
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (showCost)
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        mainAxisSize: MainAxisSize.min,
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
                  if (showTokens)
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Text(
                            l10n.reportCognitiveWork,
                            style: const TextStyle(
                              fontWeight: FontWeight.bold,
                              fontSize: 13,
                            ),
                          ),
                          Text(
                            l10n.reportPromptTokens(
                              (payload.promptTokens ?? '-').toString(),
                            ),
                            style: const TextStyle(fontSize: 13),
                          ),
                          Text(
                            l10n.reportCompletionTokens(
                              (payload.completionTokens ?? '-').toString(),
                            ),
                            style: const TextStyle(fontSize: 13),
                          ),
                          Text(
                            l10n.reportReasoningTokens(
                              (payload.reasoningTokens ?? '-').toString(),
                            ),
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

  Widget _buildLayoutSequence(
    BuildContext context,
    WidgetRef ref,
    ReportLayoutDTO layout,
  ) {
    if (layout.axes.isEmpty) {
      throw AppException.validation(
        'CRITICAL FAIL-FAST: layout.axes is empty!',
      );
    }

    final lang = Localizations.localeOf(context).languageCode;
    final title = layout.title?.get(lang);
    final desc = layout.description?.get(lang);

    final hasTitle = title != null && title.isNotEmpty;
    final hasDesc = desc != null && desc.isNotEmpty;
    final hasSynthesis =
        layout.synthesisMd != null && layout.synthesisMd!.isNotEmpty;

    Widget content;
    try {
      content = switch (layout.presetView) {
        PresetView.metrics1d => _build1DMetrics(context, layout),
        PresetView.compare2d => _build2DCompare(context, layout),
        PresetView.matrix3d => _build3DComplex(context, layout),
        PresetView.complex3d => _build3DRadar(context, layout),
        PresetView.textOnly => const SizedBox(),
        _ => _build1DMetrics(context, layout),
      };
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

    if (hasTitle || hasDesc || hasSynthesis) {
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
            if (hasTitle)
              Text(
                title,
                style: const TextStyle(
                  fontSize: 22,
                  fontWeight: FontWeight.bold,
                  letterSpacing: -0.5,
                ),
              ),
            if (hasDesc) ...[
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
            if (hasSynthesis) ...[
              const SizedBox(height: 16),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(16.0),
                decoration: BoxDecoration(
                  color: Colors.white,
                  border: Border(
                    left: BorderSide(
                      color: Theme.of(context).primaryColor,
                      width: 4,
                    ),
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withValues(alpha: 0.05),
                      blurRadius: 4,
                      offset: const Offset(0, 2),
                    ),
                  ],
                ),
                child: OutputRenderer(markdownContent: layout.synthesisMd!),
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
    if (layout.axes.isEmpty) {
      throw AppException.validation(
        'CRITICAL FAIL-FAST: layout.axes empty in 1D metrics!',
      );
    }

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
                        mainAxisSize: MainAxisSize.min,
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
                          if (layout.presetView == PresetView.metrics1d &&
                              axis.uiPlotRatio != null) ...[
                            const SizedBox(height: 12),
                            Stack(
                              children: [
                                Container(
                                  height: 12,
                                  decoration: BoxDecoration(
                                    color: Colors.grey.shade200,
                                    borderRadius: BorderRadius.circular(6),
                                  ),
                                ),
                                FractionallySizedBox(
                                  widthFactor: axis.uiPlotRatio!.clamp(
                                    0.0,
                                    1.0,
                                  ),
                                  child: Container(
                                    height: 12,
                                    decoration: BoxDecoration(
                                      gradient: LinearGradient(
                                        colors: [
                                          Theme.of(
                                            context,
                                          ).primaryColor.withValues(alpha: 0.6),
                                          Theme.of(context).primaryColor,
                                        ],
                                      ),
                                      borderRadius: BorderRadius.circular(6),
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ],
                          const SizedBox(height: 8),
                          XAIAxisTelemetryGrid(
                            axis: axis,
                            textDeliveryMode: layout.textDeliveryMode,
                            showQuote: shouldShowQuote[index],
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
                        axis.scaleMax != null &&
                                axis.scaleMin != null &&
                                axis.scaleMax! > axis.scaleMin!
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
      mainAxisSize: MainAxisSize.min,
      children: [
        Card(
          elevation: 2,
          margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              mainAxisSize: MainAxisSize.min,
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
        if (layout.textDeliveryMode != 'none') _build1DMetrics(context, layout),
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
      mainAxisSize: MainAxisSize.min,
      children: [
        Card(
          elevation: 2,
          margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              mainAxisSize: MainAxisSize.min,
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
        if (layout.textDeliveryMode != 'none') _build1DMetrics(context, layout),
      ],
    );
  }

  Widget _build3DRadar(BuildContext context, ReportLayoutDTO layout) {
    if (layout.axes.length < 3) {
      return _build1DMetrics(context, layout);
    }

    final l10n = AppLocalizations.of(context)!;
    final String title = l10n.reportAnalyticalFramework3D;

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Card(
          elevation: 2,
          margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 16),
                LogicRadarChart(axes: layout.axes),
              ],
            ),
          ),
        ),
        if (layout.textDeliveryMode != 'none') _build1DMetrics(context, layout),
      ],
    );
  }

  String _getStrictnessName(BuildContext context, int level) {
    final l10n = AppLocalizations.of(context)!;
    return switch (level) {
      0 => l10n.strictnessAbsoluteLeniency,
      15 => l10n.strictnessLenient,
      50 => l10n.strictnessBalanced,
      85 => l10n.strictnessStrict,
      100 => l10n.strictnessAbsoluteStrictness,
      _ => '$level',
    };
  }
}
