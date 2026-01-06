import 'package:json_annotation/json_annotation.dart';

part 'user.g.dart';

/// **User Role Enum**
///
/// Defines the permission levels within the Cognitive Quorum system.
/// Mapped to the backend's `UserRole` definition.
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
  unknown, // Fallback for future-proofing
}

/// **User Domain Model**
///
/// Represents the profile of an authenticated user in the system.
/// This model is hydrated from the `/api/v1/users/me` endpoint.
///
/// **Business Context**:
/// The [User] object is critical for:
/// 1.  **Access Control**: The [role] property determines access to Admin vs. Dashboard routes.
/// 2.  **Multi-tenancy**: The [organizationId] scopes all data access.
/// 3.  **Audit**: The [uid] is logged with every sensitive action.
@JsonSerializable()
class User {
  /// The Firebase UID, acting as the primary key.
  final String uid;

  /// The user's primary email address.
  final String email;

  /// The assigned system role.
  /// Defaults to [UserRole.viewer] to fail secure if data is missing.
  @JsonKey(defaultValue: UserRole.viewer, unknownEnumValue: UserRole.unknown)
  final UserRole role;

  /// The ID of the organization this user belongs to.
  @JsonKey(name: 'organization_id')
  final String? organizationId;

  /// User's display name for UI.
  @JsonKey(name: 'display_name')
  final String? displayName;

  /// ISO 8601 Timestamp of creation.
  @JsonKey(name: 'created_at')
  final String? createdAt;

  const User({
    required this.uid,
    required this.email,
    required this.role,
    this.organizationId,
    this.displayName,
    this.createdAt,
  });

  /// Factory constructor for creating a new [User] instance from a map.
  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);

  /// Converts the [User] instance to a JSON map.
  Map<String, dynamic> toJson() => _$UserToJson(this);

  /// **Helper**: Checks if the user has Admin privileges.
  bool get isAdmin => role == UserRole.root || role == UserRole.admin;
}
