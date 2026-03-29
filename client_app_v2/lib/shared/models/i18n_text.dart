import 'package:client_app/utils/safe_cast.dart';

/// V2 Strict: Frontend no-string mandate requires all localized text to be structured.
class I18nText {
  final String defaultLocale;
  final Map<String, String> translations;

  const I18nText({
    this.defaultLocale = 'en',
    this.translations = const {'en': ''},
  });

  /// Extracts the localized string for a given language code. Defaults to [defaultLocale].
  String get(String langCode) {
    if (translations.containsKey(langCode) && translations[langCode]!.isNotEmpty) {
      return translations[langCode]!;
    }
    return translations[defaultLocale] ?? '';
  }

  factory I18nText.fromJson(Map<String, dynamic> json) {
    final translationsRaw = SafeCast.safeMap(json['translations']);
    final Map<String, String> parsedTranslations = {};
    for (final entry in translationsRaw.entries) {
      parsedTranslations[entry.key] = SafeCast.safeString(entry.value);
    }
    
    return I18nText(
      defaultLocale: SafeCast.safeString(json['default_locale'], 'en'),
      translations: parsedTranslations.isEmpty ? {'en': ''} : parsedTranslations,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'default_locale': defaultLocale,
      'translations': translations,
    };
  }

  I18nText copyWith({
    String? defaultLocale,
    Map<String, String>? translations,
  }) {
    return I18nText(
      defaultLocale: defaultLocale ?? this.defaultLocale,
      translations: translations ?? Map<String, String>.from(this.translations),
    );
  }
}
