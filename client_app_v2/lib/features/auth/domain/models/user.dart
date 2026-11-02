import 'package:client_app/core/models/enums.dart';
import 'package:client_app/utils/json_converters.dart';
import 'package:freezed_annotation/freezed_annotation.dart';

export 'package:client_app/core/models/enums.dart' show UserRole;

part 'user.freezed.dart';
part 'user.g.dart';

// Phase 6, Step 6.1: Synchronize User and IAM Session Upgrade / Logout Freezed DTOs.

/// **User Domain Model**
///
/// Represents the profile of an authenticated user in the system.
/// Hydrated from `/api/v2/iam/auth/exchange` and `/api/v2/iam/auth/me`.
@Freezed(equal: false)
abstract class User with _$User {
  const User._();

  @JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
  const factory User({
    @StrictOpaqueIdConverter() @JsonKey(name: 'id') required String id,
    @JsonKey(name: 'slug') String? slug,
    // Phase 2, Step 2: Synchronize firebase_uid and deleted_at with backend User SSOT
    @JsonKey(name: 'firebase_uid') String? firebaseUid,
    @JsonKey(name: 'email') required String email,
    @JsonKey(name: 'role') required UserRole role,
    @JsonKey(name: 'organization_id') String? organizationId,
    @JsonKey(name: 'name') String? name,
    @JsonKey(name: 'created_at') String? createdAt,
    @JsonKey(name: 'language') String? language,
    @JsonKey(name: 'theme_mode') String? themeMode,
    @JsonKey(name: 'last_login_at') DateTime? lastLoginAt,
    @JsonKey(name: 'execution_count') int? executionCount,
    @JsonKey(name: 'is_active') bool? isActive,
    @JsonKey(name: 'created_by') String? createdBy,
    @JsonKey(name: 'deleted_at') DateTime? deletedAt,
  }) = _User;

  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);

  /// Checks if the user has Admin or Root privileges.
  bool get isAdmin => role == UserRole.root || role == UserRole.admin;

  /// Checks if the user can access Organization & IAM governance views.
  bool get canManageOrganization =>
      role == UserRole.root ||
      role == UserRole.admin ||
      role == UserRole.manager;
}

/// Request payload for `POST /api/v2/iam/auth/exchange`.
@Freezed(equal: false)
abstract class TokenExchangeRequestDto with _$TokenExchangeRequestDto {
  const TokenExchangeRequestDto._();

  @JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
  const factory TokenExchangeRequestDto({
    @JsonKey(name: 'firebase_token', includeIfNull: false)
    String? firebaseToken,
    @JsonKey(name: 'target_user_id', includeIfNull: false) String? targetUserId,
    @JsonKey(name: 'service_auth_secret', includeIfNull: false)
    String? serviceAuthSecret,
  }) = _TokenExchangeRequestDto;

  factory TokenExchangeRequestDto.fromJson(Map<String, dynamic> json) =>
      _$TokenExchangeRequestDtoFromJson(json);
}

/// Response payload from `POST /api/v2/iam/auth/exchange`.
@Freezed(equal: false)
abstract class TokenExchangeResponseDto with _$TokenExchangeResponseDto {
  const TokenExchangeResponseDto._();

  @JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
  const factory TokenExchangeResponseDto({
    @JsonKey(name: 'access_token') required String accessToken,
    @JsonKey(name: 'token_type') @Default('bearer') String tokenType,
    @JsonKey(name: 'expires_in_seconds') required int expiresInSeconds,
    @JsonKey(name: 'user') required User user,
  }) = _TokenExchangeResponseDto;

  factory TokenExchangeResponseDto.fromJson(Map<String, dynamic> json) =>
      _$TokenExchangeResponseDtoFromJson(json);
}

/// Request payload for `POST /api/v2/iam/auth/logout`.
@Freezed(equal: false)
abstract class LogoutRequestDto with _$LogoutRequestDto {
  const LogoutRequestDto._();

  @JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
  const factory LogoutRequestDto({
    @JsonKey(name: 'revoke_all_sessions')
    @Default(false)
    bool revokeAllSessions,
  }) = _LogoutRequestDto;

  factory LogoutRequestDto.fromJson(Map<String, dynamic> json) =>
      _$LogoutRequestDtoFromJson(json);
}

/// Response payload from `POST /api/v2/iam/auth/logout`.
@Freezed(equal: false)
abstract class LogoutResponseDto with _$LogoutResponseDto {
  const LogoutResponseDto._();

  @JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
  const factory LogoutResponseDto({
    // Phase 2, Step 2: Synchronize default logout status with backend LogoutResponseDTO
    @JsonKey(name: 'status') @Default('logged_out') String status,
    @JsonKey(name: 'revoked_jti') required String revokedJti,
    @JsonKey(name: 'all_sessions_revoked') required bool allSessionsRevoked,
  }) = _LogoutResponseDto;

  factory LogoutResponseDto.fromJson(Map<String, dynamic> json) =>
      _$LogoutResponseDtoFromJson(json);
}

/// Request payload for `POST /api/v2/iam/users`.
@Freezed(equal: false)
abstract class UserCreate with _$UserCreate {
  const UserCreate._();

  @JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
  const factory UserCreate({
    @JsonKey(name: 'email') required String email,
    @JsonKey(name: 'name', includeIfNull: false) String? name,
    @JsonKey(name: 'role') @Default(UserRole.member) UserRole role,
    @StrictOpaqueIdConverter()
    @JsonKey(name: 'organization_id')
    required String organizationId,
    @JsonKey(name: 'is_active') @Default(true) bool isActive,
    @JsonKey(name: 'language', includeIfNull: false) String? language,
    @JsonKey(name: 'theme_mode', includeIfNull: false) String? themeMode,
    @JsonKey(name: 'created_by', includeIfNull: false) String? createdBy,
    @JsonKey(name: 'password', includeIfNull: false) String? password,
  }) = _UserCreate;

  factory UserCreate.fromJson(Map<String, dynamic> json) =>
      _$UserCreateFromJson(json);
}

/// Request payload for `PUT /api/v2/iam/users/{id}`.
@Freezed(equal: false)
abstract class UserUpdate with _$UserUpdate {
  const UserUpdate._();

  @JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
  const factory UserUpdate({
    @JsonKey(name: 'name', includeIfNull: false) String? name,
    @JsonKey(name: 'role', includeIfNull: false) UserRole? role,
    @JsonKey(name: 'organization_id', includeIfNull: false)
    String? organizationId,
    @JsonKey(name: 'is_active', includeIfNull: false) bool? isActive,
    @JsonKey(name: 'language', includeIfNull: false) String? language,
    @JsonKey(name: 'theme_mode', includeIfNull: false) String? themeMode,
    @JsonKey(name: 'password', includeIfNull: false) String? password,
  }) = _UserUpdate;

  factory UserUpdate.fromJson(Map<String, dynamic> json) =>
      _$UserUpdateFromJson(json);
}
