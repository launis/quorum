// ignore_for_file: invalid_annotation_target
import 'package:freezed_annotation/freezed_annotation.dart';

part 'execution_inputs.freezed.dart';
part 'execution_inputs.g.dart';

/// Strictly typed execution inputs container for client DAG execution.
@Freezed(equal: false)
abstract class ExecutionInputs with _$ExecutionInputs {
  const ExecutionInputs._();

  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory ExecutionInputs({
    @JsonKey(name: 'raw_inputs') @Default({}) Map<String, dynamic> rawInputs,
    @JsonKey(name: 'dynamic_inputs')
    @Default({})
    Map<String, dynamic> dynamicInputs,
    @JsonKey(name: 'user_role') String? userRole,
    @JsonKey(name: 'target_locale') String? targetLocale,
  }) = _ExecutionInputs;

  /// Instantiates a strictly typed [ExecutionInputs] from raw JSON.
  factory ExecutionInputs.fromJson(Map<String, dynamic> json) =>
      _$ExecutionInputsFromJson(json);
}
