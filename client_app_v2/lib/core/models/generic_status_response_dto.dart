import 'package:freezed_annotation/freezed_annotation.dart';

part 'generic_status_response_dto.freezed.dart';
part 'generic_status_response_dto.g.dart';

@freezed
abstract class GenericStatusResponseDto with _$GenericStatusResponseDto {
  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory GenericStatusResponseDto({
    @Default('ok') String status,
    required String message,
  }) = _GenericStatusResponseDto;

  factory GenericStatusResponseDto.fromJson(Map<String, dynamic> json) =>
      _$GenericStatusResponseDtoFromJson(json);
}
