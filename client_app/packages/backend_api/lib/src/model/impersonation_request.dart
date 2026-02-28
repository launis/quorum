//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'impersonation_request.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class ImpersonationRequest {
  /// Returns a new [ImpersonationRequest] instance.
  ImpersonationRequest({required this.targetId});

  @JsonKey(name: r'target_id', required: true)
  final String targetId;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is ImpersonationRequest && other.targetId == targetId;

  @override
  int get hashCode => targetId.hashCode;

  factory ImpersonationRequest.fromJson(Map<String, dynamic> json) =>
      _$ImpersonationRequestFromJson(json);

  Map<String, dynamic> toJson() => _$ImpersonationRequestToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
