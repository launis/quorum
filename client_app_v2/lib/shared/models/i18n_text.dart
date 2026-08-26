// ignore_for_file: invalid_annotation_target

import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:client_app/core/error/app_exception.dart';

part 'i18n_text.freezed.dart';
part 'i18n_text.g.dart';

/// V2 Strict: Frontend no-string mandate requires all localized text to be structured.
@freezed
abstract class I18nText with _$I18nText {
  const I18nText._();

  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory I18nText({required Map<String, String> translations}) =
      _I18nText;

  factory I18nText.fromJson(Map<String, dynamic> json) =>
      _$I18nTextFromJson(json);

  /// Returns true if translations map is empty or all values are blank.
  bool get isEmpty =>
      translations.isEmpty ||
      translations.values.every((v) => v.trim().isEmpty);

  /// Returns true if at least one translation value contains non-whitespace text.
  bool get isNotEmpty => !isEmpty;

  /// Returns true if a non-empty translation exists for the given language code.
  bool has(String? langCode) {
    if (langCode == null) return false;
    final clean = langCode.split(RegExp(r'[-_]')).first.toLowerCase().trim();
    return translations.containsKey(clean) &&
        translations[clean]!.trim().isNotEmpty;
  }

  /// Extracts the localized string for a given language code following Fail-Fast rules.
  ///
  /// Fallback resolution order:
  /// 1. Requested [langCode] (e.g. 'fi' from 'fi-FI')
  /// 2. [fallback] language code (default 'en')
  /// 3. Lingua Franca 'en'
  ///
  /// Throws [AppException.validation] if no non-empty translation is resolved.
  String get(String? langCode, {String fallback = 'en'}) {
    if (langCode != null && langCode.trim().isNotEmpty) {
      final clean = langCode.split(RegExp(r'[-_]')).first.toLowerCase().trim();
      if (translations.containsKey(clean) &&
          translations[clean]!.trim().isNotEmpty) {
        return translations[clean]!;
      }
    }

    final cleanFallback = fallback
        .split(RegExp(r'[-_]'))
        .first
        .toLowerCase()
        .trim();
    if (translations.containsKey(cleanFallback) &&
        translations[cleanFallback]!.trim().isNotEmpty) {
      return translations[cleanFallback]!;
    }

    if (translations.containsKey('en') &&
        translations['en']!.trim().isNotEmpty) {
      return translations['en']!;
    }

    throw AppException.validation(
      'Fail-Fast: Missing required translation for langCode "$langCode" and fallback "$fallback". Available keys: ${translations.keys.toList()}',
    );
  }
}
