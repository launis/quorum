import 'package:freezed_annotation/freezed_annotation.dart';

part 'distilled_evaluation.freezed.dart';
part 'distilled_evaluation.g.dart';

/// Phase 5, Step 5.1: Strongly typed scalar/list extension value replacing `Map<String, Object?>`.
class DistilledExtensionValueConverter
    implements JsonConverter<DistilledExtensionValue, Object?> {
  const DistilledExtensionValueConverter();

  @override
  DistilledExtensionValue fromJson(Object? json) {
    if (json is List) {
      return DistilledExtensionValue(
        stringListValue: json
            .map((Object? e) => e.toString())
            .toList(growable: false),
      );
    }
    if (json is num) {
      return DistilledExtensionValue(numberValue: json.toDouble());
    }
    if (json is bool) {
      return DistilledExtensionValue(boolValue: json);
    }
    if (json is String) {
      return DistilledExtensionValue(stringValue: json);
    }
    return const DistilledExtensionValue();
  }

  @override
  Object? toJson(DistilledExtensionValue object) {
    if (object.stringListValue != null) {
      return object.stringListValue;
    }
    if (object.numberValue != null) {
      return object.numberValue;
    }
    if (object.boolValue != null) {
      return object.boolValue;
    }
    return object.stringValue;
  }
}

/// Strongly typed value wrapper for XAI extension entries in [DistilledEvaluation].
@freezed
abstract class DistilledExtensionValue with _$DistilledExtensionValue {
  const DistilledExtensionValue._();

  @JsonSerializable(
    explicitToJson: true,
    disallowUnrecognizedKeys: true,
    fieldRename: FieldRename.snake,
  )
  const factory DistilledExtensionValue({
    String? stringValue,
    double? numberValue,
    bool? boolValue,
    List<String>? stringListValue,
  }) = _DistilledExtensionValue;

  factory DistilledExtensionValue.fromJson(Map<String, dynamic> json) =>
      _$DistilledExtensionValueFromJson(json);

  Object? get rawValue =>
      stringListValue ?? numberValue ?? boolValue ?? stringValue;
}

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
    String? status,
    @DistilledExtensionValueConverter()
    Map<String, DistilledExtensionValue>? extensions,
    @Default([]) List<String> dependsOnTdaIds,
    @Default([]) List<String> shortCircuitReasonTdaIds,
    @Default(false) bool isInverseEvidence,
    @Default(0) int topologicalOutDegree,
  }) = _DistilledEvaluation;

  factory DistilledEvaluation.fromJson(Map<String, dynamic> json) =>
      _$DistilledEvaluationFromJson(json);
}
