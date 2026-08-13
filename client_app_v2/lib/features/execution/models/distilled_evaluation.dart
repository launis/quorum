// ignore_for_file: invalid_annotation_target
import 'package:freezed_annotation/freezed_annotation.dart';

part 'distilled_evaluation.freezed.dart';
part 'distilled_evaluation.g.dart';

@Freezed(equal: false)
abstract class DistilledEvaluation with _$DistilledEvaluation {
  @JsonSerializable(
    explicitToJson: true,
    disallowUnrecognizedKeys: true,
    fieldRename: FieldRename.snake,
  )
  const factory DistilledEvaluation({
    String? atomId,
    required List<String> exactQuotes,
    String? semanticReasoning,
    Map<String, dynamic>? extensions,
  }) = _DistilledEvaluation;

  factory DistilledEvaluation.fromJson(Map<String, dynamic> json) =>
      _$DistilledEvaluationFromJson(json);
}
