enum UserRole {
  root,
  admin,
  manager,
  member,
  viewer,
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
///
/// **Business Context**:
/// The [User] object is critical for:
/// 1.  **Access Control**: The [role] property determines access to Admin vs. Dashboard routes.
/// 2.  **Multi-tenancy**: The [organizationId] scopes all data access.
/// 3.  **Audit**: The [id] is logged with every sensitive action.
class User {
  /// The UUID, acting as the primary key.
  final String id;

  /// The legacy string identifier (optional).
  final String? slug;

  /// The user's primary email address.
  final String email;

  /// The assigned system role.
  final UserRole role;

  /// The ID of the organization this user belongs to.
  final String? organizationId;

  /// User's display name for UI.
  final String? displayName;

  /// ISO 8601 Timestamp of creation.
  final String? createdAt;

  /// User's preferred language code (e.g., 'en', 'fi').
  final String? language;

  /// User's preferred theme mode (e.g., 'system', 'light', 'dark').
  final String? themeMode;

  /// Timestamp of the last successful login.
  /// Nullable as it might be missing for legacy users or first login.
  final DateTime? lastLoginAt;

  /// Total number of logic executions performed by the user.
  /// Nullable because the standard `/api/v1/users/me` endpoint might omit it compared to Admin SDK views.
  final int? executionCount;

  const User({
    required this.id,
    this.slug,
    required this.email,
    required this.role,
    this.organizationId,
    this.displayName,
    this.createdAt,
    this.language,
    this.themeMode,
    this.lastLoginAt,
    this.executionCount,
  });

  /// Factory constructor for creating a new [User] instance from a map.
  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] as String,
      slug: json['slug'] as String?,
      email: json['email'] as String,
      role: UserRole.fromString(json['role'] as String),
      organizationId: json['organization_id'] as String?,
      displayName: json['display_name'] as String?,
      createdAt: json['created_at'] as String?,
      language: json['language'] as String?,
      themeMode: json['theme_mode'] as String?,
      lastLoginAt:
          json['last_login_at'] != null
              ? DateTime.tryParse(json['last_login_at'] as String)
              : null,
      executionCount: json['execution_count'] as int?,
    );
  }

  /// Converts the [User] instance to a JSON map.
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'slug': slug,
      'email': email,
      'role': role.toJson(),
      'organization_id': organizationId,
      'display_name': displayName,
      'created_at': createdAt,
      'language': language,
      'theme_mode': themeMode,
      'last_login_at': lastLoginAt?.toIso8601String(),
      'execution_count': executionCount,
    };
  }

  /// **Helper**: Checks if the user has Admin privileges.
  bool get isAdmin => role == UserRole.root || role == UserRole.admin;
}
