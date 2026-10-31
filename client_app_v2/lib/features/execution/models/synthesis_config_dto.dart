import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/utils/json_converters.dart';
import 'package:freezed_annotation/freezed_annotation.dart';

part 'synthesis_config_dto.freezed.dart';
part 'synthesis_config_dto.g.dart';

/// Strongly typed configuration DTO for synthesis directives and block targets.
@Freezed(equal: false)
abstract class SynthesisConfigDto with _$SynthesisConfigDto {
  const SynthesisConfigDto._();

  @JsonSerializable(disallowUnrecognizedKeys: true, explicitToJson: true)
  const factory SynthesisConfigDto({
    @JsonKey(name: 'system_prompt') String? systemPrompt,
    @StrictOpaqueIdConverter()
    @JsonKey(name: 'synthesis_block_id')
    String? synthesisBlockId,
    @StrictOpaqueIdConverter()
    @JsonKey(name: 'row_explanations_block_id')
    String? rowExplanationsBlockId,
    @JsonKey(name: 'length_constraint') int? lengthConstraint,
    @JsonKey(name: 'preamble_text') I18nText? preambleText,
    @JsonKey(name: 'tone_instruction') I18nText? toneInstruction,
  }) = _SynthesisConfigDto;

  /// Instantiates a strictly typed [SynthesisConfigDto] from raw JSON.
  factory SynthesisConfigDto.fromJson(Map<String, dynamic> json) =>
      _$SynthesisConfigDtoFromJson(json);
}
