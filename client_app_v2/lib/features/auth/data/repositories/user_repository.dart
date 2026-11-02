import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/error/validation_error_reason.dart';
import 'package:client_app/core/network/api_client.dart';
import 'package:client_app/features/auth/domain/models/user.dart';
import 'package:client_app/features/settings/domain/models/tenant_secret_dto.dart';
import 'package:dio/dio.dart';
import 'package:fpdart/fpdart.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'user_repository.g.dart';

// Phase 6, Step 6.2: Strongly typed User, Organization, Invitation, and BYOK Secret Repository.

@Riverpod(keepAlive: true)
UserRepository userRepository(Ref ref) {
  return UserRepository(ref.watch(apiClientProvider));
}

class UserRepository {
  final Dio _client;
  UserRepository(this._client);

  Either<AppException, T> _handleError<T>(Object e) {
    if (e is DioException) {
      if (e.error is AppException) {
        return Left(e.error as AppException);
      }
      if (e.response?.statusCode == 404) {
        return Left(AppException.notFound('Resource not found'));
      }
      if (e.response?.statusCode == 401) {
        return Left(AppException.unauthorized());
      }
      if (e.response?.statusCode == 400) {
        return Left(
          AppException.validation(ValidationErrorReason.unknown.toString()),
        );
      }
      return Left(AppException.unknown(e));
    }
    if (e is AppException) return Left(e);
    return Left(AppException.unknown(e));
  }

  Future<Either<AppException, User>> fetchCurrentUser() async {
    try {
      final response = await _client.get<Map<String, Object?>>('/iam/users/me');
      final payload = response.data;
      if (payload == null) return const Left(AppException(detail: ''));
      return Right(User.fromJson(payload));
    } catch (e) {
      return _handleError(e);
    }
  }

  Future<Either<AppException, User>> updateUser(
    String userId,
    UserUpdate payload,
  ) async {
    try {
      final response = await _client.put<Map<String, Object?>>(
        '/iam/users/$userId',
        data: payload.toJson(),
      );
      final data = response.data;
      if (data == null) return const Left(AppException(detail: ''));
      return Right(User.fromJson(data));
    } catch (e) {
      return _handleError(e);
    }
  }

  Future<Either<AppException, List<User>>> listUsers() async {
    try {
      final response = await _client.get<List<Object?>>('/iam/users/');
      final items = response.data;
      if (items == null) return const Left(AppException(detail: ''));
      final users = <User>[];
      for (final item in items) {
        if (item is Map<String, Object?>) {
          users.add(User.fromJson(item));
        }
      }
      return Right(users);
    } catch (e) {
      return _handleError(e);
    }
  }

  Future<Either<AppException, UserDeleteResponse>> deleteUser(
    String userId,
  ) async {
    try {
      final response = await _client.delete<Map<String, Object?>>(
        '/iam/users/$userId',
      );
      final data = response.data;
      if (data == null) return const Left(AppException(detail: ''));
      return Right(UserDeleteResponse.fromJson(data));
    } catch (e) {
      return _handleError(e);
    }
  }

  Future<Either<AppException, Organization>> getOrganization(
    String orgId,
  ) async {
    try {
      final response = await _client.get<Map<String, Object?>>(
        '/iam/organizations/$orgId',
      );
      final data = response.data;
      if (data == null) return const Left(AppException(detail: ''));
      return Right(Organization.fromJson(data));
    } catch (e) {
      return _handleError(e);
    }
  }

  Future<Either<AppException, Organization>> updateOrganization(
    String orgId,
    OrganizationUpdateDto payload,
  ) async {
    try {
      final response = await _client.put<Map<String, Object?>>(
        '/iam/organizations/$orgId',
        data: payload.toJson(),
      );
      final data = response.data;
      if (data == null) return const Left(AppException(detail: ''));
      return Right(Organization.fromJson(data));
    } catch (e) {
      return _handleError(e);
    }
  }

  Future<Either<AppException, List<InvitationResponseDto>>> listInvitations(
    String orgId,
  ) async {
    try {
      final response = await _client.get<List<Object?>>(
        '/iam/organizations/$orgId/invitations',
      );
      final items = response.data;
      if (items == null) return const Left(AppException(detail: ''));
      final invitations = <InvitationResponseDto>[];
      for (final item in items) {
        if (item is Map<String, Object?>) {
          invitations.add(InvitationResponseDto.fromJson(item));
        }
      }
      return Right(invitations);
    } catch (e) {
      return _handleError(e);
    }
  }

  Future<Either<AppException, InvitationResponseDto>> createInvitation(
    String orgId,
    InvitationCreateDto payload,
  ) async {
    try {
      final response = await _client.post<Map<String, Object?>>(
        '/iam/organizations/$orgId/invitations',
        data: payload.toJson(),
      );
      final data = response.data;
      if (data == null) return const Left(AppException(detail: ''));
      return Right(InvitationResponseDto.fromJson(data));
    } catch (e) {
      return _handleError(e);
    }
  }

  Future<Either<AppException, InvitationBatchResponseDto>>
  createInvitationBatch(String orgId, InvitationBatchCreateDto payload) async {
    try {
      final response = await _client.post<Map<String, Object?>>(
        '/iam/organizations/$orgId/invitations/batch',
        data: payload.toJson(),
      );
      final data = response.data;
      if (data == null) return const Left(AppException(detail: ''));
      return Right(InvitationBatchResponseDto.fromJson(data));
    } catch (e) {
      return _handleError(e);
    }
  }

  Future<Either<AppException, InvitationResponseDto>> revokeInvitation(
    String orgId,
    String invitationId,
  ) async {
    try {
      final response = await _client.delete<Map<String, Object?>>(
        '/iam/organizations/$orgId/invitations/$invitationId',
      );
      final data = response.data;
      if (data == null) return const Left(AppException(detail: ''));
      return Right(InvitationResponseDto.fromJson(data));
    } catch (e) {
      return _handleError(e);
    }
  }

  Future<Either<AppException, List<TenantSecretResponseDto>>> listSecrets(
    String orgId,
  ) async {
    try {
      final response = await _client.get<List<Object?>>(
        '/iam/organizations/$orgId/secrets',
      );
      final items = response.data;
      if (items == null) return const Left(AppException(detail: ''));
      final secrets = <TenantSecretResponseDto>[];
      for (final item in items) {
        if (item is Map<String, Object?>) {
          secrets.add(TenantSecretResponseDto.fromJson(item));
        }
      }
      return Right(secrets);
    } catch (e) {
      return _handleError(e);
    }
  }

  Future<Either<AppException, TenantSecretResponseDto>> upsertSecret(
    String orgId,
    TenantSecretCreateDto payload,
  ) async {
    try {
      final response = await _client.put<Map<String, Object?>>(
        '/iam/organizations/$orgId/secrets',
        data: payload.toJson(),
      );
      final data = response.data;
      if (data == null) return const Left(AppException(detail: ''));
      return Right(TenantSecretResponseDto.fromJson(data));
    } catch (e) {
      return _handleError(e);
    }
  }

  Future<Either<AppException, OrganizationDeleteResponse>> deleteSecret(
    String orgId,
    String secretId,
  ) async {
    try {
      final response = await _client.delete<Map<String, Object?>>(
        '/iam/organizations/$orgId/secrets/$secretId',
      );
      final data = response.data;
      if (data == null) return const Left(AppException(detail: ''));
      return Right(OrganizationDeleteResponse.fromJson(data));
    } catch (e) {
      return _handleError(e);
    }
  }
}
