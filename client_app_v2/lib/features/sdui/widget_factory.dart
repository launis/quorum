import 'package:flutter/material.dart';

import 'package:client_app/shared/widgets/score_card_radar.dart';
import 'package:client_app/shared/widgets/unified_metric_gauge.dart';
import 'package:client_app/shared/widgets/deep_dive_expander.dart';
import 'package:client_app/utils/safe_cast.dart';
import 'package:client_app/utils/i18n_resolver.dart';

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
  }) {
    final String widgetType = hint['widget']?.toString() ?? 'unknown';

    // 1. Defensively extract the primary value
    final dynamic rawValue = results[slug];

    // 2. Build the core widget
    Widget coreWidget;
    switch (widgetType) {
      case 'radar_chart':
        final Map<String, dynamic> cardData = SafeCast.safeMap(rawValue);
        if (cardData.isEmpty) {
          debugPrint(
            'SDUIWidgetFactory WARN: radar_chart requires Map data for slug "$slug"',
          );
          return const SizedBox.shrink();
        }
        coreWidget = ScoreCardRadar(cardData: cardData);
        break;

      case 'gauge':
      case 'slider':
        final double val = SafeCast.safeDouble(rawValue);
        final double maxVal = SafeCast.safeDouble(hint['max'], 6.0);
        final String label = I18nResolver.resolve(hint['instruction'], locale);

        if (label.isEmpty) {
          debugPrint(
            'SDUIWidgetFactory WARN: gauge requires a label for slug "$slug"',
          );
          return const SizedBox.shrink();
        }

        coreWidget = Padding(
          padding: const EdgeInsets.symmetric(vertical: 8.0),
          child: UnifiedMetricGauge(
            label: label,
            value: val,
            max: maxVal,
            description: label,
            displayValue: val.toStringAsFixed(1),
          ),
        );
        break;

      default:
        debugPrint(
          'SDUIWidgetFactory WARN: Unsupported widget type "$widgetType" for slug "$slug"',
        );
        return const SizedBox.shrink();
    }

    // 3. XAI Compound Logic: Check for justification & citation
    final String justification = SafeCast.safeString(
      results['${slug}_justification'],
    );
    final String citation = SafeCast.safeString(results['${slug}_citation']);

    if (justification.isNotEmpty) {
      String titleStr = I18nResolver.resolve(
        hint['justification_title'],
        locale,
      );
      if (titleStr.isEmpty) {
        titleStr = locale == 'fi' ? 'Perustelu' : 'Justification';
      }

      coreWidget = Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        mainAxisSize: MainAxisSize.min,
        children: [
          coreWidget,
          const SizedBox(height: 16),
          Container(
            decoration: BoxDecoration(
              border: Border.all(color: Colors.grey.shade300),
              borderRadius: BorderRadius.circular(12),
              color: Colors.white,
            ),
            padding: const EdgeInsets.all(8),
            child: DeepDiveExpander(
              title: titleStr,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Text(
                    justification,
                    style: const TextStyle(height: 1.5, color: Colors.black87),
                  ),
                  if (citation.isNotEmpty) ...[
                    const SizedBox(height: 12),
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 8,
                      ),
                      decoration: BoxDecoration(
                        color: Colors.grey.shade50,
                        borderRadius: BorderRadius.circular(6),
                        border: Border.all(color: Colors.grey.shade200),
                      ),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Icon(
                            Icons.menu_book,
                            size: 16,
                            color: Colors.grey,
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              citation,
                              style: const TextStyle(
                                fontStyle: FontStyle.italic,
                                color: Colors.black54,
                                fontSize: 13,
                              ),
                            ),
                          ),
                        ],
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

    // 4. Layout Constraints (Milestone 4)
    // Ensures widgets do not overflow horizontally regardless of screen size.
    return LayoutBuilder(
      builder: (context, constraints) {
        return ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 800), // Max desktop width
          child: Padding(
            padding: const EdgeInsets.symmetric(vertical: 4.0),
            child: coreWidget,
          ),
        );
      },
    );
  }
}
