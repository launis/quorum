// ignore_for_file: invalid_annotation_target
import 'package:freezed_annotation/freezed_annotation.dart';
import '../../../core/models/enums.dart';

part 'atom_result_dto.freezed.dart';
part 'atom_result_dto.g.dart';

@freezed
abstract class ExtractedValueDTO with _$ExtractedValueDTO {
  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory ExtractedValueDTO({required dynamic value, String? unit}) =
      _ExtractedValueDTO;

  factory ExtractedValueDTO.fromJson(Map<String, dynamic> json) =>
      _$ExtractedValueDTOFromJson(json);
}

@freezed
abstract class ErrorDetailsDTO with _$ErrorDetailsDTO {
  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory ErrorDetailsDTO({
    @JsonKey(name: 'error_code') required String errorCode,
    required String message,
  }) = _ErrorDetailsDTO;

  factory ErrorDetailsDTO.fromJson(Map<String, dynamic> json) =>
      _$ErrorDetailsDTOFromJson(json);
}

@Freezed(equal: false)
abstract class AtomResultDTO with _$AtomResultDTO {
  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory AtomResultDTO({
    @JsonKey(name: 'tda_id') required String tdaId,
    required ExecutionStatus status,
    @JsonKey(name: 'extracted_data') ExtractedValueDTO? extractedData,
    @JsonKey(name: 'source_quote') String? sourceQuote,
    @JsonKey(name: 'contextual_override')
    @Default(false)
    bool contextualOverride,
    @JsonKey(name: 'evaluation_reasoning') String? evaluationReasoning,
    @JsonKey(name: 'error_details') ErrorDetailsDTO? errorDetails,
    @JsonKey(name: 'extensions') @Default({}) Map<String, String> extensions,
    @JsonKey(name: 'depends_on_tda_ids')
    @Default([])
    List<String> dependsOnTdaIds,
    @JsonKey(name: 'short_circuit_reason_tda_ids')
    @Default([])
    List<String> shortCircuitReasonTdaIds,
  }) = _AtomResultDTO;

  factory AtomResultDTO.fromJson(Map<String, dynamic> json) =>
      _$AtomResultDTOFromJson(json);
}
