// ignore_for_file: invalid_annotation_target
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:client_app/core/models/enums.dart';
import 'matrix_scorecard_dto.dart';

part 'human_override_request_dto.freezed.dart';
part 'human_override_request_dto.g.dart';

/// Payload for human override requests.
///
/// Matches backend SSOT `HumanOverrideRequest` in `backend_v2/models/dtos/matrix_scorecard.py`.
@Freezed(equal: false)
abstract class HumanOverrideRequestDto with _$HumanOverrideRequestDto {
  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory HumanOverrideRequestDto({
    @JsonKey(name: 'new_status') required ExecutionStatus newStatus,
    required String reason,
    @JsonKey(name: 'evidence_quotes')
    @Default([])
    List<QuoteEvidenceDto> evidenceQuotes,
  }) = _HumanOverrideRequestDto;

  factory HumanOverrideRequestDto.fromJson(Map<String, dynamic> json) =>
      _$HumanOverrideRequestDtoFromJson(json);
}
