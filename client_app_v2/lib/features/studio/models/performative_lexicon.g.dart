// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'performative_lexicon.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_LexiconConfigPayload _$LexiconConfigPayloadFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_LexiconConfigPayload',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'language_code',
        'language_name',
        'fuzz_threshold',
        'words',
      ],
    );
    final val = _LexiconConfigPayload(
      languageCode: $checkedConvert('language_code', (v) => v as String),
      languageName: $checkedConvert('language_name', (v) => v as String),
      fuzzThreshold: $checkedConvert(
        'fuzz_threshold',
        (v) => (v as num?)?.toInt() ?? 90,
      ),
      words: $checkedConvert(
        'words',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'languageCode': 'language_code',
    'languageName': 'language_name',
    'fuzzThreshold': 'fuzz_threshold',
  },
);

Map<String, dynamic> _$LexiconConfigPayloadToJson(
  _LexiconConfigPayload instance,
) => <String, dynamic>{
  'language_code': instance.languageCode,
  'language_name': instance.languageName,
  'fuzz_threshold': instance.fuzzThreshold,
  'words': instance.words,
};

_SystemConfigPerformativeLexicons _$SystemConfigPerformativeLexiconsFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_SystemConfigPerformativeLexicons',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const ['id', 'slug', 'type', 'lexicon_configs'],
    );
    final val = _SystemConfigPerformativeLexicons(
      id: $checkedConvert('id', (v) => v as String),
      slug: $checkedConvert('slug', (v) => v as String),
      type: $checkedConvert('type', (v) => v as String),
      lexiconConfigs: $checkedConvert(
        'lexicon_configs',
        (v) =>
            (v as Map<String, dynamic>?)?.map(
              (k, e) => MapEntry(
                k,
                LexiconConfigPayload.fromJson(e as Map<String, dynamic>),
              ),
            ) ??
            const {},
      ),
    );
    return val;
  },
  fieldKeyMap: const {'lexiconConfigs': 'lexicon_configs'},
);

Map<String, dynamic> _$SystemConfigPerformativeLexiconsToJson(
  _SystemConfigPerformativeLexicons instance,
) => <String, dynamic>{
  'id': instance.id,
  'slug': instance.slug,
  'type': instance.type,
  'lexicon_configs': instance.lexiconConfigs.map(
    (k, e) => MapEntry(k, e.toJson()),
  ),
};

_LexiconSuggestionListDTO _$LexiconSuggestionListDTOFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_LexiconSuggestionListDTO',
  json,
  ($checkedConvert) {
    $checkKeys(json, allowedKeys: const ['suggested_phrases']);
    final val = _LexiconSuggestionListDTO(
      suggestedPhrases: $checkedConvert(
        'suggested_phrases',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
    );
    return val;
  },
  fieldKeyMap: const {'suggestedPhrases': 'suggested_phrases'},
);

Map<String, dynamic> _$LexiconSuggestionListDTOToJson(
  _LexiconSuggestionListDTO instance,
) => <String, dynamic>{'suggested_phrases': instance.suggestedPhrases};
