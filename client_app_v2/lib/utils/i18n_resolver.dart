import 'package:client_app/utils/safe_cast.dart';

/// **I18n Fallback Resolver**
///
/// Converts a dynamic backend I18n block (containing translations and a default locale)
/// into a flat string for the UI based on the user's current device locale.
///
/// **Backend JSON Structure Expected**:
/// ```json
/// {
///   "default_locale": "fi",
///   "translations": {
///     "fi": "Arvioi innovaatiotaso.",
///     "en": "Evaluate the innovation level."
///   }
/// }
/// ```
class I18nResolver {
  /// Resolves an I18n JSON block to the target locale if available.
  /// Falls back to the `default_locale` from the JSON block,
  /// or an empty string / error message if completely missing.
  ///
  /// [data] The dynamic JSON block (from the backend).
  /// [targetLocale] The app's current primary language code (e.g. 'fi', 'en').
  static String resolve(dynamic data, String targetLocale) {
    if (data == null) return '';

    // If it's just a raw String somehow, return it gracefully
    if (data is String) return data;

    final map = SafeCast.safeMap(data);
    if (map.isEmpty) return '';

    // Extract default locale and translations Map
    final String defaultLocale = SafeCast.safeString(map['default_locale']);
    final Map<String, dynamic> translations = SafeCast.safeMap(
      map['translations'],
    );

    if (translations.isEmpty) {
      // In case translations map is completely empty, see if they passed flat properties
      final directTry = SafeCast.safeString(map[targetLocale]);
      if (directTry.isNotEmpty) return directTry;

      return map.toString(); // Very graceful degradation instead of crash
    }

    // 1. Try Target Locale
    final targetStr = SafeCast.safeString(translations[targetLocale]);
    if (targetStr.isNotEmpty) return targetStr;

    // 2. Try Default Locale
    if (defaultLocale.isNotEmpty) {
      final defaultStr = SafeCast.safeString(translations[defaultLocale]);
      if (defaultStr.isNotEmpty) return defaultStr;
    }

    // 3. Ultimate Fallback (Grab whatever first translation exists)
    if (translations.values.isNotEmpty) {
      return SafeCast.safeString(translations.values.first);
    }

    return '';
  }
}
