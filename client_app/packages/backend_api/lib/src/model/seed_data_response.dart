//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'seed_data_response.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class SeedDataResponse {
  /// Returns a new [SeedDataResponse] instance.
  SeedDataResponse({
    required this.components,

    required this.steps,

    required this.workflows,
  });

  @JsonKey(name: r'components', required: true)
  final List<Map<String, Object>> components;

  @JsonKey(name: r'steps', required: true)
  final List<Map<String, Object>> steps;

  @JsonKey(name: r'workflows', required: true)
  final List<Map<String, Object>> workflows;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is SeedDataResponse &&
          other.components == components &&
          other.steps == steps &&
          other.workflows == workflows;

  @override
  int get hashCode => components.hashCode + steps.hashCode + workflows.hashCode;

  factory SeedDataResponse.fromJson(Map<String, dynamic> json) =>
      _$SeedDataResponseFromJson(json);

  Map<String, dynamic> toJson() => _$SeedDataResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
