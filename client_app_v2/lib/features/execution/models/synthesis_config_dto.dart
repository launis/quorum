// ignore_for_file: invalid_annotation_target
import 'package:freezed_annotation/freezed_annotation.dart';
import '../../../../shared/models/i18n_text.dart';

part 'synthesis_config_dto.freezed.dart';
part 'synthesis_config_dto.g.dart';

@Freezed(equal: false)
abstract class SynthesisConfigDto with _$SynthesisConfigDto {
  const SynthesisConfigDto._();

  @JsonSerializable(disallowUnrecognizedKeys: false)
  const factory SynthesisConfigDto({
    @JsonKey(name: 'system_prompt') String? systemPrompt,
    @JsonKey(name: 'synthesis_block_id') String? synthesisBlockId,
    @JsonKey(name: 'row_explanations_block_id') String? rowExplanationsBlockId,
    @JsonKey(name: 'length_constraint') int? lengthConstraint,
    @JsonKey(name: 'preamble_text') I18nText? preambleText,
    @JsonKey(name: 'tone_instruction') I18nText? toneInstruction,
  }) = _SynthesisConfigDto;

  factory SynthesisConfigDto.fromJson(Map<String, dynamic> json) =>
      _$SynthesisConfigDtoFromJson(json);
}
