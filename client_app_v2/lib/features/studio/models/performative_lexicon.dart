import 'package:freezed_annotation/freezed_annotation.dart';

part 'performative_lexicon.freezed.dart';
part 'performative_lexicon.g.dart';

// ignore_for_file: invalid_annotation_target
@freezed
abstract class LexiconConfigPayload with _$LexiconConfigPayload {
  const factory LexiconConfigPayload({
    @JsonKey(name: 'language_code') required String languageCode,
    @JsonKey(name: 'language_name') required String languageName,
    @JsonKey(name: 'fuzz_threshold') @Default(90) int fuzzThreshold,
    @Default([]) List<String> words,
  }) = _LexiconConfigPayload;

  factory LexiconConfigPayload.fromJson(Map<String, dynamic> json) =>
      _$LexiconConfigPayloadFromJson(json);
}

@freezed
abstract class SystemConfigPerformativeLexicons
    with _$SystemConfigPerformativeLexicons {
  const factory SystemConfigPerformativeLexicons({
    required String id,
    required String slug,
    required String type,
    @JsonKey(name: 'lexicon_configs')
    @Default({})
    Map<String, LexiconConfigPayload> lexiconConfigs,
  }) = _SystemConfigPerformativeLexicons;

  factory SystemConfigPerformativeLexicons.fromJson(
    Map<String, dynamic> json,
  ) => _$SystemConfigPerformativeLexiconsFromJson(json);
}

@freezed
abstract class LexiconSuggestionListDTO with _$LexiconSuggestionListDTO {
  const factory LexiconSuggestionListDTO({
    @JsonKey(name: 'suggested_phrases')
    @Default([])
    List<String> suggestedPhrases,
  }) = _LexiconSuggestionListDTO;

  factory LexiconSuggestionListDTO.fromJson(Map<String, dynamic> json) =>
      _$LexiconSuggestionListDTOFromJson(json);
}
