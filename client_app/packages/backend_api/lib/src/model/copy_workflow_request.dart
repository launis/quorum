//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'copy_workflow_request.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class CopyWorkflowRequest {
  /// Returns a new [CopyWorkflowRequest] instance.
  CopyWorkflowRequest({required this.newName});

  /// Name for the copy.
  @JsonKey(name: r'new_name', required: true)
  final String newName;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is CopyWorkflowRequest && other.newName == newName;

  @override
  int get hashCode => newName.hashCode;

  factory CopyWorkflowRequest.fromJson(Map<String, dynamic> json) =>
      _$CopyWorkflowRequestFromJson(json);

  Map<String, dynamic> toJson() => _$CopyWorkflowRequestToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
