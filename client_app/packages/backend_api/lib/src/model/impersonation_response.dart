//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'impersonation_response.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class ImpersonationResponse {
  /// Returns a new [ImpersonationResponse] instance.
  ImpersonationResponse({required this.accessToken, this.tokenType = 'bearer'});

  @JsonKey(name: r'access_token', required: true)
  final String accessToken;

  @JsonKey(defaultValue: 'bearer', name: r'token_type', required: false)
  final String? tokenType;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is ImpersonationResponse &&
          other.accessToken == accessToken &&
          other.tokenType == tokenType;

  @override
  int get hashCode => accessToken.hashCode + tokenType.hashCode;

  factory ImpersonationResponse.fromJson(Map<String, dynamic> json) =>
      _$ImpersonationResponseFromJson(json);

  Map<String, dynamic> toJson() => _$ImpersonationResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
