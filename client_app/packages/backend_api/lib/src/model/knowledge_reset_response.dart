//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'knowledge_reset_response.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class KnowledgeResetResponse {
  /// Returns a new [KnowledgeResetResponse] instance.
  KnowledgeResetResponse({required this.message});

  @JsonKey(name: r'message', required: true)
  final String message;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is KnowledgeResetResponse && other.message == message;

  @override
  int get hashCode => message.hashCode;

  factory KnowledgeResetResponse.fromJson(Map<String, dynamic> json) =>
      _$KnowledgeResetResponseFromJson(json);

  Map<String, dynamic> toJson() => _$KnowledgeResetResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
