//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:backend_api/src/model/user_role.dart';
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'user_update.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class UserUpdate {
  /// Returns a new [UserUpdate] instance.
  UserUpdate({
    this.displayName,

    this.role,

    this.isActive,

    this.password,

    this.language,

    this.themeMode,

    this.organizationId,
  });

  @JsonKey(name: r'display_name', required: false)
  final String? displayName;

  @JsonKey(name: r'role', required: false)
  final UserRole? role;

  @JsonKey(name: r'is_active', required: false)
  final bool? isActive;

  @JsonKey(name: r'password', required: false)
  final String? password;

  @JsonKey(name: r'language', required: false)
  final String? language;

  @JsonKey(name: r'theme_mode', required: false)
  final String? themeMode;

  @JsonKey(name: r'organization_id', required: false)
  final String? organizationId;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is UserUpdate &&
          other.displayName == displayName &&
          other.role == role &&
          other.isActive == isActive &&
          other.password == password &&
          other.language == language &&
          other.themeMode == themeMode &&
          other.organizationId == organizationId;

  @override
  int get hashCode =>
      (displayName == null ? 0 : displayName.hashCode) +
      (role == null ? 0 : role.hashCode) +
      (isActive == null ? 0 : isActive.hashCode) +
      (password == null ? 0 : password.hashCode) +
      (language == null ? 0 : language.hashCode) +
      (themeMode == null ? 0 : themeMode.hashCode) +
      (organizationId == null ? 0 : organizationId.hashCode);

  factory UserUpdate.fromJson(Map<String, dynamic> json) =>
      _$UserUpdateFromJson(json);

  Map<String, dynamic> toJson() => _$UserUpdateToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
