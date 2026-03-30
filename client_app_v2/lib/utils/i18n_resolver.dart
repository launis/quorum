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

    final map = data is Map
        ? Map<String, dynamic>.from(data)
        : <String, dynamic>{};
    if (map.isEmpty) return '';

    // Extract translations Map (default_locale is no longer used due to exact matching)
    final trRaw = map['translations'];
    final Map<String, dynamic> translations = trRaw is Map
        ? Map<String, dynamic>.from(trRaw)
        : <String, dynamic>{};

    if (translations.isEmpty) {
      // In case translations map is completely empty, see if they passed flat properties
      final directTry = map[targetLocale]?.toString() ?? '';
      if (directTry.isNotEmpty) return directTry;

      throw FormatException(
        'Translation missing for required locale "$targetLocale" in flat map. Fallbacks are strictly forbidden.',
        map,
      );
    }

    // 1. Try Target Locale strictly
    final targetStr = translations[targetLocale]?.toString() ?? '';
    if (targetStr.isNotEmpty) return targetStr;

    // Fail Fast Mandate: No fallbacks allowed.
    throw FormatException(
      'Translation missing for required locale "$targetLocale". Fallbacks are strictly forbidden.',
      map,
    );
  }
}
