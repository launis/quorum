// ignore_for_file: invalid_annotation_target
import 'package:freezed_annotation/freezed_annotation.dart';

part 'global_synthesis_dto.freezed.dart';
part 'global_synthesis_dto.g.dart';

@freezed
abstract class GlobalSynthesisDto with _$GlobalSynthesisDto {
  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory GlobalSynthesisDto({
    @JsonKey(name: 'executive_summary') String? executiveSummary,
    @JsonKey(name: 'urgency_level') int? urgencyLevel,
    @JsonKey(name: 'user_role') String? userRole,
    @JsonKey(name: 'user_role_justification') String? userRoleJustification,
  }) = _GlobalSynthesisDto;

  factory GlobalSynthesisDto.fromJson(Map<String, dynamic> json) =>
      _$GlobalSynthesisDtoFromJson(json);
}
