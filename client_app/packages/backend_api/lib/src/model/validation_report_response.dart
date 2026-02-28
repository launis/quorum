//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'validation_report_response.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class ValidationReportResponse {
  /// Returns a new [ValidationReportResponse] instance.
  ValidationReportResponse({
    required this.valid,

    required this.errors,

    required this.trace,

    required this.finalStateKeys,
  });

  @JsonKey(name: r'valid', required: true)
  final bool valid;

  @JsonKey(name: r'errors', required: true)
  final List<String> errors;

  @JsonKey(name: r'trace', required: true)
  final List<String> trace;

  @JsonKey(name: r'final_state_keys', required: true)
  final List<String> finalStateKeys;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is ValidationReportResponse &&
          other.valid == valid &&
          other.errors == errors &&
          other.trace == trace &&
          other.finalStateKeys == finalStateKeys;

  @override
  int get hashCode =>
      valid.hashCode +
      errors.hashCode +
      trace.hashCode +
      finalStateKeys.hashCode;

  factory ValidationReportResponse.fromJson(Map<String, dynamic> json) =>
      _$ValidationReportResponseFromJson(json);

  Map<String, dynamic> toJson() => _$ValidationReportResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
