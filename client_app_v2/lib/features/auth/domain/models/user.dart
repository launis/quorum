import 'package:freezed_annotation/freezed_annotation.dart';

part 'user.freezed.dart';
part 'user.g.dart';

enum UserRole {
  @JsonValue('ROOT')
  root,
  @JsonValue('ADMIN')
  admin,
  @JsonValue('MANAGER')
  manager,
  @JsonValue('MEMBER')
  member,
  @JsonValue('VIEWER')
  viewer,
  @JsonValue('UNKNOWN')
  unknown;

  static UserRole fromString(String value) {
    switch (value.toUpperCase()) {
      case 'ROOT':
        return UserRole.root;
      case 'ADMIN':
        return UserRole.admin;
      case 'MANAGER':
        return UserRole.manager;
      case 'MEMBER':
        return UserRole.member;
      case 'VIEWER':
        return UserRole.viewer;
      default:
        throw FormatException('Unknown UserRole: $value');
    }
  }

  String toJson() {
    if (this == UserRole.unknown) return 'VIEWER';
    return name.toUpperCase();
  }
}

/// **User Domain Model**
///
/// Represents the profile of an authenticated user in the system.
/// This model is hydrated from the `/api/v1/users/me` endpoint.
@freezed
abstract class User with _$User {
  const User._();

  const factory User({
    required String id,
    String? slug,
    required String email,
    required UserRole role,
    String? organizationId,
    String? displayName,
    String? createdAt,
    String? language,
    String? themeMode,
    DateTime? lastLoginAt,
    int? executionCount,
    bool? isActive,
    String? createdBy,
  }) = _User;

  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);

  /// **Helper**: Checks if the user has Admin privileges.
  bool get isAdmin => role == UserRole.root || role == UserRole.admin;
}
