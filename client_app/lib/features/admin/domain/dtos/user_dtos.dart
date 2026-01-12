import 'package:freezed_annotation/freezed_annotation.dart';

import 'package:client_app/features/auth/domain/models/user.dart';

part 'user_dtos.freezed.dart';
part 'user_dtos.g.dart';

/// **User Creation Data Transfer Object**
///
/// Payload for creating a new user via Admin API.
@freezed
abstract class UserCreateDto with _$UserCreateDto {
  // ignore: invalid_annotation_target
  @JsonSerializable(includeIfNull: false)
  const factory UserCreateDto({
    required String email,
    required String password,
    @JsonKey(name: 'display_name') required String displayName,
    required UserRole role,
    @JsonKey(name: 'organization_id') String? organizationId,
  }) = _UserCreateDto;

  factory UserCreateDto.fromJson(Map<String, dynamic> json) =>
      _$UserCreateDtoFromJson(json);
}

/// **User Update Data Transfer Object**
///
/// Payload for updating an existing user via Admin API.
/// Only non-null fields will be sent to the backend.
@freezed
abstract class UserUpdateDto with _$UserUpdateDto {
  // ignore: invalid_annotation_target
  @JsonSerializable(includeIfNull: false)
  const factory UserUpdateDto({
    @JsonKey(name: 'display_name') String? displayName,
    UserRole? role,
    @JsonKey(name: 'is_active') bool? isActive,
  }) = _UserUpdateDto;

  factory UserUpdateDto.fromJson(Map<String, dynamic> json) =>
      _$UserUpdateDtoFromJson(json);
}
