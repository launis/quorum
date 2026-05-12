import 'package:freezed_annotation/freezed_annotation.dart';

part 'i18n_text.freezed.dart';
part 'i18n_text.g.dart';

/// V2 Strict: Frontend no-string mandate requires all localized text to be structured.
@freezed
abstract class I18nText with _$I18nText {
  const I18nText._();

  const factory I18nText({
    @JsonKey(name: 'default_locale') @Default('en') String defaultLocale,
    @Default({'en': ''}) Map<String, String> translations,
  }) = _I18nText;

  factory I18nText.fromJson(Map<String, dynamic> json) =>
      _$I18nTextFromJson(json);

  /// Extracts the localized string for a given language code. Defaults to [defaultLocale].
  String get(String langCode) {
    if (translations.containsKey(langCode) &&
        translations[langCode]!.isNotEmpty) {
      return translations[langCode]!;
    }
    return translations[defaultLocale] ?? '';
  }
}
