// ignore_for_file: invalid_annotation_target
import 'package:freezed_annotation/freezed_annotation.dart';

part 'synthesis_config_dto.freezed.dart';
part 'synthesis_config_dto.g.dart';

@Freezed(equal: false)
abstract class SynthesisConfigDto with _$SynthesisConfigDto {
  // disallowUnrecognizedKeys: false — SynthesisConfigDTO is a backend config
  // object with 15+ internal fields. Flutter carries it opaquely.
  @JsonSerializable(disallowUnrecognizedKeys: false)
  const factory SynthesisConfigDto({
    @JsonKey(name: 'system_prompt') String? systemPrompt,
    @JsonKey(name: 'synthesis_block_id') String? synthesisBlockId,
    @JsonKey(name: 'row_explanations_block_id') String? rowExplanationsBlockId,
    @JsonKey(name: 'model_strategy') @Default('synthesis') String modelStrategy,
    @JsonKey(name: 'length_constraint') int? lengthConstraint,
    @JsonKey(name: 'enable_pii_masking') @Default(false) bool enablePiiMasking,
    @JsonKey(name: 'omit_empty_sections') @Default(true) bool omitEmptySections,
  }) = _SynthesisConfigDto;

  factory SynthesisConfigDto.fromJson(Map<String, dynamic> json) =>
      _$SynthesisConfigDtoFromJson(json);
}
