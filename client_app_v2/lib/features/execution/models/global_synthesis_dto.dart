// ignore_for_file: invalid_annotation_target
import 'package:freezed_annotation/freezed_annotation.dart';

part 'global_synthesis_dto.freezed.dart';
part 'global_synthesis_dto.g.dart';

@freezed
abstract class GlobalSynthesisDTO with _$GlobalSynthesisDTO {
  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory GlobalSynthesisDTO({
    @JsonKey(name: 'executive_summary') String? executiveSummary,
    @JsonKey(name: 'urgency_level') int? urgencyLevel,
  }) = _GlobalSynthesisDTO;

  factory GlobalSynthesisDTO.fromJson(Map<String, dynamic> json) =>
      _$GlobalSynthesisDTOFromJson(json);
}
