//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'token_payload.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class TokenPayload {
  /// Returns a new [TokenPayload] instance.
  TokenPayload({required this.token});

  @JsonKey(name: r'token', required: true)
  final String token;

  @override
  bool operator ==(Object other) =>
      identical(this, other) || other is TokenPayload && other.token == token;

  @override
  int get hashCode => token.hashCode;

  factory TokenPayload.fromJson(Map<String, dynamic> json) =>
      _$TokenPayloadFromJson(json);

  Map<String, dynamic> toJson() => _$TokenPayloadToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
