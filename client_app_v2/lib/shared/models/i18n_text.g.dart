// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'i18n_text.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_I18nText _$I18nTextFromJson(Map<String, dynamic> json) =>
    $checkedCreate('_I18nText', json, ($checkedConvert) {
      $checkKeys(json, allowedKeys: const ['translations']);
      final val = _I18nText(
        translations: $checkedConvert(
          'translations',
          (v) => Map<String, String>.from(v as Map),
        ),
      );
      return val;
    });

Map<String, dynamic> _$I18nTextToJson(_I18nText instance) => <String, dynamic>{
  'translations': instance.translations,
};
