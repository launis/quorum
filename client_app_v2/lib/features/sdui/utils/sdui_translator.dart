import 'package:flutter/widgets.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

/// Translates dynamic SDUI keys into localized strings.
/// Acts as the bridge between the semantic routing defined by the backend
/// and the strongly-typed Flutter `AppLocalizations`.
class SduiTranslator {
  /// Translates an SDUI title/key (e.g. `report.title_main`).
  /// If the translation is not found, it gracefully degrades by returning the
  /// original key, ensuring UI stability.
  static String translate(BuildContext context, String key) {
    // If the key is empty or null, return empty
    if (key.isEmpty) return key;

    final l10n = AppLocalizations.of(context);
    if (l10n == null) return key;

    // Convert keys to match our .arb mapping
    switch (key.toLowerCase()) {
      case 'report.title_main':
      case 'reporttitlemain':
        return l10n.reportTitleMain;
      case 'report.metrics':
      case 'reportmetrics':
        return l10n.reportMetrics;
      case 'report.score':
      case 'reportscore':
        return l10n.reportScore;
      default:
        // Graceful degradation: return original key so developers see what's missing
        return key;
    }
  }
}
