//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:backend_api/src/model/user_role.dart';
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'user.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class User {
  /// Returns a new [User] instance.
  User({
    required this.email,

    this.displayName,

    this.role = UserRole.MEMBER,

    this.organizationId,

    this.isActive = true,

    this.language = UserLanguageEnum.fi,

    this.themeMode = UserThemeModeEnum.system,

    this.id,

    this.slug,

    required this.createdAt,

    this.createdBy,
  });

  /// User email address
  @JsonKey(name: r'email', required: true)
  final String email;

  @JsonKey(name: r'display_name', required: false)
  final String? displayName;

  /// Assigned permission role
  @JsonKey(defaultValue: UserRole.MEMBER, name: r'role', required: false)
  final UserRole? role;

  @JsonKey(name: r'organization_id', required: false)
  final String? organizationId;

  /// Is the account active?
  @JsonKey(defaultValue: true, name: r'is_active', required: false)
  final bool? isActive;

  /// Preferred UI language
  @JsonKey(defaultValue: 'fi', name: r'language', required: false)
  final UserLanguageEnum? language;

  /// Preferred Theme Mode
  @JsonKey(defaultValue: 'system', name: r'theme_mode', required: false)
  final UserThemeModeEnum? themeMode;

  /// Unique ID (matches Firebase UID if used)
  @JsonKey(name: r'id', required: false)
  final String? id;

  @JsonKey(name: r'slug', required: false)
  final String? slug;

  /// ISO 8601 Timestamp
  @JsonKey(name: r'created_at', required: true)
  final DateTime createdAt;

  @JsonKey(name: r'created_by', required: false)
  final String? createdBy;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is User &&
          other.email == email &&
          other.displayName == displayName &&
          other.role == role &&
          other.organizationId == organizationId &&
          other.isActive == isActive &&
          other.language == language &&
          other.themeMode == themeMode &&
          other.id == id &&
          other.slug == slug &&
          other.createdAt == createdAt &&
          other.createdBy == createdBy;

  @override
  int get hashCode =>
      email.hashCode +
      (displayName == null ? 0 : displayName.hashCode) +
      role.hashCode +
      (organizationId == null ? 0 : organizationId.hashCode) +
      isActive.hashCode +
      language.hashCode +
      themeMode.hashCode +
      id.hashCode +
      (slug == null ? 0 : slug.hashCode) +
      createdAt.hashCode +
      (createdBy == null ? 0 : createdBy.hashCode);

  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);

  Map<String, dynamic> toJson() => _$UserToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}

/// Preferred UI language
enum UserLanguageEnum {
  /// Preferred UI language
  @JsonValue(r'fi')
  fi(r'fi'),

  /// Preferred UI language
  @JsonValue(r'en')
  en(r'en'),

  /// Preferred UI language
  @JsonValue(r'sv')
  sv(r'sv');

  const UserLanguageEnum(this.value);

  final String value;

  @override
  String toString() => value;
}

/// Preferred Theme Mode
enum UserThemeModeEnum {
  /// Preferred Theme Mode
  @JsonValue(r'system')
  system(r'system'),

  /// Preferred Theme Mode
  @JsonValue(r'light')
  light(r'light'),

  /// Preferred Theme Mode
  @JsonValue(r'dark')
  dark(r'dark');

  const UserThemeModeEnum(this.value);

  final String value;

  @override
  String toString() => value;
}
