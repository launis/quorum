// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'i18n_text.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_I18nText _$I18nTextFromJson(Map<String, dynamic> json) =>
    $checkedCreate('_I18nText', json, ($checkedConvert) {
      $checkKeys(json, allowedKeys: const ['default_locale', 'translations']);
      final val = _I18nText(
        defaultLocale: $checkedConvert(
          'default_locale',
          (v) => v as String? ?? 'en',
        ),
        translations: $checkedConvert(
          'translations',
          (v) =>
              (v as Map<String, dynamic>?)?.map(
                (k, e) => MapEntry(k, e as String),
              ) ??
              const {'en': ''},
        ),
      );
      return val;
    }, fieldKeyMap: const {'defaultLocale': 'default_locale'});

Map<String, dynamic> _$I18nTextToJson(_I18nText instance) => <String, dynamic>{
  'default_locale': instance.defaultLocale,
  'translations': instance.translations,
};
