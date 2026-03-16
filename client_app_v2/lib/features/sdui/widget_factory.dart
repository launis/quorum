import 'package:flutter/material.dart';

import 'package:client_app/shared/widgets/score_card_radar.dart';
import 'package:client_app/shared/widgets/unified_metric_gauge.dart';
import 'package:client_app/shared/widgets/deep_dive_expander.dart';
import 'package:client_app/utils/safe_cast.dart';
import 'package:client_app/utils/i18n_resolver.dart';
import 'package:client_app/core/logging/logger_service.dart';

/// **SDUI Widget Factory**
///
/// Central rendering engine for the V2 Architecture. Converts dynamic
/// backend `ui_hints_snapshot` definitions into Flutter widgets.
///
/// **Constraints:**
/// - Strictly adheres to the Zero-Codegen mandate.
/// - Defensive parsing is required for all data (SafeCast).
/// - Fails fast via logging but renders graceful degradation (SizedBox.shrink)
///   to avoid total UI crashes if a single component fails.
class SDUIWidgetFactory {
  /// Builds a Flutter widget based on the provided SDUI hint.
  ///
  /// [hint] The UI instruction from the backend (e.g., {'widget': 'radar_chart'}).
  /// [slug] The unique observation identifier (e.g., 'bloom_score').
  // ignore: avoid_annotating_with_dynamic
  /// [results] The dynamic execution results containing the actual values.
  /// [locale] The target language code for this render cycle.
  static Widget buildWidget({
    required Map<String, dynamic> hint,
    required String slug,
    required Map<String, dynamic> results,
    required String locale,
    required LoggerService logger,
  }) {
    final String widgetType = SafeCast.safeString(hint['type']);

    // V6 MVP Component Renderer using Dart 3 Pattern Matching
    Widget coreWidget = switch (widgetType) {
      'header' => _buildHeader(hint, locale),
      'metadata_header' => _buildMetadataHeader(hint, results, locale),
      'bibliography_footer' => _buildBibliographyFooter(hint, results, locale),
      '1d_gauge' => _build1DGauge(hint, slug, logger, locale),
      '2d_matrix' => _build2DMatrix(hint, slug, logger, locale),
      '3d_scatter' => _build3DScatter(hint, slug, logger, locale),
      'evaluation_notes_panel' => _buildEvaluationNotes(
        hint,
        slug,
        logger,
        locale,
      ),
      // Legacy Fallbacks
      'radar_chart' => _buildRadarChart(hint, slug, results, logger),
      'gauge' ||
      'slider' => _buildLegacyGauge(hint, slug, results, locale, logger),
      'text_input' || 'textarea' || 'markdown' => const SizedBox.shrink(),
      _ => () {
        logger.debug(
          'SDUIBuilder',
          'Ignored non-renderable widget type "$widgetType" for slug "$slug"',
        );
        return const SizedBox.shrink();
      }(),
    };

    // V6 Layout Constraints (Milestone 6)
    // Ensures widgets do not overflow horizontally regardless of screen size.
    return LayoutBuilder(
      builder: (context, constraints) {
        return ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 800), // Max desktop width
          child: Padding(
            padding: const EdgeInsets.symmetric(vertical: 8.0),
            child: coreWidget,
          ),
        );
      },
    );
  }

  static Widget _buildHeader(Map<String, dynamic> hint, String locale) {
    final title = I18nResolver.resolve(hint['title'], locale);
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 16.0),
      child: Text(
        title.isNotEmpty ? title : SafeCast.safeString(hint['title']),
        style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
      ),
    );
  }

  static Widget _buildMetadataHeader(
    Map<String, dynamic> hint,
    Map<String, dynamic> results,
    String locale,
  ) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.blueGrey.shade50,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          const Icon(Icons.analytics, color: Colors.blueGrey),
          const SizedBox(width: 8),
          Text(
            locale == 'fi' ? 'Raportin Metatiedot' : 'Report Metadata',
            style: const TextStyle(fontWeight: FontWeight.w600),
          ),
        ],
      ),
    );
  }

  static Widget _buildBibliographyFooter(
    Map<String, dynamic> hint,
    Map<String, dynamic> results,
    String locale,
  ) {
    // The BlueprintTransformer injects 'bibliography' array at the root of the Render endpoint payload
    // However, in execution_view.dart it passes `results` to the factory, so if bibliography is
    // root level we might need to fetch it from the unified payload. For now, render placeholder.
    return Container(
      margin: const EdgeInsets.only(top: 32),
      padding: const EdgeInsets.all(16),
      decoration: const BoxDecoration(
        border: Border(top: BorderSide(color: Colors.black12)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            locale == 'fi'
                ? 'Lähteet & Kirjallisuus'
                : 'Bibliography & References',
            style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          const Text(
            'Bibliographic data rendered here natively by SDUI.',
            style: TextStyle(color: Colors.black54),
          ),
        ],
      ),
    );
  }

  static Widget _build1DGauge(
    Map<String, dynamic> hint,
    String slug,
    LoggerService logger,
    String locale,
  ) {
    final double val = SafeCast.safeDouble(hint['value']);
    final String label = I18nResolver.resolve(hint['title'] ?? 'Gauge', locale);

    if (label.isEmpty) {
      logger.error(
        'SDUIBuilder',
        'VALIDATION_FAILED: 1d_gauge requires a label for slug "$slug"',
      );
      return const SizedBox.shrink();
    }

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      child: UnifiedMetricGauge(
        label: label.isNotEmpty ? label : SafeCast.safeString(hint['title']),
        value: val,
        max: 10.0, // Default max
        description: label,
        displayValue: val.toStringAsFixed(1),
      ),
    );
  }

  static Widget _build2DMatrix(
    Map<String, dynamic> hint,
    String slug,
    LoggerService logger,
    String locale,
  ) {
    final xVal = SafeCast.safeDouble(hint['x_value']);
    final yVal = SafeCast.safeDouble(hint['y_value']);
    return Card(
      elevation: 1,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '2D Matrix Component ($slug)',
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Text('X Axis: $xVal\nY Axis: $yVal'),
            if (hint.containsKey('x_note_text')) ...[
              const SizedBox(height: 8),
              Text(
                'X Note: ${SafeCast.safeString(hint['x_note_text'])}',
                style: const TextStyle(fontStyle: FontStyle.italic),
              ),
            ],
            if (hint.containsKey('y_note_text')) ...[
              const SizedBox(height: 4),
              Text(
                'Y Note: ${SafeCast.safeString(hint['y_note_text'])}',
                style: const TextStyle(fontStyle: FontStyle.italic),
              ),
            ],
          ],
        ),
      ),
    );
  }

  static Widget _build3DScatter(
    Map<String, dynamic> hint,
    String slug,
    LoggerService logger,
    String locale,
  ) {
    final xVal = SafeCast.safeDouble(hint['x_value']);
    final yVal = SafeCast.safeDouble(hint['y_value']);
    final zVal = SafeCast.safeDouble(hint['z_value']);
    return Card(
      elevation: 1,
      color: Colors.blue.shade50,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '3D Scatter Component ($slug)',
              style: const TextStyle(
                fontWeight: FontWeight.bold,
                color: Colors.blue,
              ),
            ),
            const SizedBox(height: 8),
            Text('X: $xVal  |  Y: $yVal  |  Z: $zVal'),
          ],
        ),
      ),
    );
  }

  static Widget _buildEvaluationNotes(
    Map<String, dynamic> hint,
    String slug,
    LoggerService logger,
    String locale,
  ) {
    final notes = SafeCast.safeMap(hint['resolved_notes']);
    if (notes.isEmpty) return const SizedBox.shrink();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text(
          locale == 'fi' ? 'Arviointimuistiot' : 'Evaluation Notes',
          style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),
        ...notes.entries.map(
          (e) => Padding(
            padding: const EdgeInsets.only(bottom: 8.0),
            child: DeepDiveExpander(
              title: e.key,
              child: Text(SafeCast.safeString(e.value)),
            ),
          ),
        ),
      ],
    );
  }

  static Widget _buildRadarChart(
    Map<String, dynamic> hint,
    String slug,
    Map<String, dynamic> results,
    LoggerService logger,
  ) {
    final rawValue = results[slug];
    final Map<String, dynamic> cardData = SafeCast.safeMap(rawValue);
    if (cardData.isEmpty) {
      logger.error(
        'SDUIBuilder',
        'VALIDATION_FAILED: radar_chart requires Map data for slug "$slug"',
      );
      return const SizedBox.shrink();
    }
    return ScoreCardRadar(cardData: cardData);
  }

  static Widget _buildLegacyGauge(
    Map<String, dynamic> hint,
    String slug,
    Map<String, dynamic> results,
    String locale,
    LoggerService logger,
  ) {
    final rawValue = results[slug];
    final double val = SafeCast.safeDouble(rawValue);
    final validationRules = SafeCast.safeMap(hint['validation_rules']);
    final double maxVal = SafeCast.safeDouble(
      validationRules['max'] ?? hint['max'],
      6.0,
    );

    String displayVal = val.toStringAsFixed(1);
    final scales = SafeCast.safeList(hint['scales']);
    if (scales.isNotEmpty) {
      final intIntVal = val.toInt();
      for (final dynamic s in scales) {
        final scaleDef = SafeCast.safeMap(s);
        if (SafeCast.safeInt(scaleDef['score']) == intIntVal) {
          final scaleName = I18nResolver.resolve(scaleDef['name'], locale);
          if (scaleName.isNotEmpty) {
            displayVal = '$intIntVal: $scaleName';
            break;
          }
        }
      }
    }

    final options = SafeCast.safeList(hint['options']);
    dynamic rawInstruction = hint['instruction'];
    if (options.isNotEmpty && options.first is Map) {
      rawInstruction ??= SafeCast.safeMap(options.first)['label'];
    }

    final String label = I18nResolver.resolve(rawInstruction, locale);
    if (label.isEmpty) {
      logger.error(
        'SDUIBuilder',
        'VALIDATION_FAILED: gauge requires a label for slug "$slug"',
      );
      return const SizedBox.shrink();
    }

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      child: UnifiedMetricGauge(
        label: label,
        value: val,
        max: maxVal,
        description: label,
        displayValue: displayVal,
      ),
    );
  }
}
