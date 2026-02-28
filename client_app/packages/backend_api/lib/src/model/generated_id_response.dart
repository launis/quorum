//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'generated_id_response.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class GeneratedIdResponse {
  /// Returns a new [GeneratedIdResponse] instance.
  GeneratedIdResponse({required this.id});

  @JsonKey(name: r'id', required: true)
  final String id;

  @override
  bool operator ==(Object other) =>
      identical(this, other) || other is GeneratedIdResponse && other.id == id;

  @override
  int get hashCode => id.hashCode;

  factory GeneratedIdResponse.fromJson(Map<String, dynamic> json) =>
      _$GeneratedIdResponseFromJson(json);

  Map<String, dynamic> toJson() => _$GeneratedIdResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
