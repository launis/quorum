import 'package:dio/dio.dart';
import 'package:fpdart/fpdart.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:client_app/api/api_client.dart';
import 'package:client_app/core/error/app_error.dart';
import 'package:client_app/features/auth/domain/models/user.dart';
import 'package:client_app/features/admin/domain/models/queue_stats.dart';
import 'package:client_app/features/admin/domain/dtos/user_dtos.dart';

part 'admin_repository.g.dart';

/// **Admin Repository**
///
/// Handles data operations for the Admin Panel.
/// Strictly follows the functional error handling pattern using [Either].
///
/// **Dependencies**:
/// - ApiClient: For making HTTP requests.
@Riverpod(keepAlive: true)
AdminRepository adminRepository(Ref ref) {
  return AdminRepository(ref.watch(apiClientProvider));
}

class AdminRepository {
  final Dio _client;

  AdminRepository(this._client);

  /// **Get Users by Organization**
  ///
  /// Fetches the list of users for a specific organization.
  /// Access control: Handled by backend (ROOT or Organization ADMIN).
  ///
  /// **Endpoint**: `GET /api/v1/admin/org/{id}/users`
  Future<Either<AppError, List<User>>> getUsersByOrganization(
    String orgId,
  ) async {
    try {
      final response = await _client.get<List<dynamic>>(
        '/admin/org/$orgId/users',
      );

      final data = response.data;
      if (data == null) return const Right([]);

      final users =
          data
              .map((json) => User.fromJson(json as Map<String, dynamic>))
              .toList();

      return Right(users);
    } catch (e, st) {
      return Left(_handleError(e, st));
    }
  }

  /// **Update User Role**
  ///
  /// Updates the role of a specific user.
  ///
  /// **Endpoint**: `PUT /api/v1/admin/user/{id}/role`
  /// **Features**:
  /// - Handles LAST_ADMIN_PROTECTION error specifically.
  Future<Either<AppError, void>> updateUserRole(
    String userId,
    String newRole,
  ) async {
    try {
      await _client.put<void>(
        '/admin/user/$userId/role',
        data: {'role': newRole},
      );
      return const Right(null);
    } catch (e, st) {
      return Left(_handleError(e, st));
    }
  }

  /// **Create User**
  ///
  /// Creates a new user in the organization.
  ///
  /// **Endpoint**: `POST /api/v1/admin/users`
  Future<Either<AppError, void>> createUser(UserCreateDto data) async {
    try {
      await _client.post<void>('/admin/users', data: data.toJson());
      return const Right(null);
    } catch (e, st) {
      return Left(_handleError(e, st));
    }
  }

  /// **Update User**
  ///
  /// Updates an existing user's details.
  ///
  /// **Endpoint**: `PATCH /api/v1/admin/users/{userId}`
  Future<Either<AppError, void>> updateUser({
    required String userId,
    required UserUpdateDto data,
  }) async {
    try {
      await _client.patch<void>('/admin/users/$userId', data: data.toJson());
      return const Right(null);
    } catch (e, st) {
      return Left(_handleError(e, st));
    }
  }

  /// **Delete User**
  ///
  /// Deletes a user from the system.
  ///
  /// **Endpoint**: `DELETE /api/v1/admin/users/{userId}`
  /// **Safeguards**: Checks for LAST_ADMIN_PROTECTION (409).
  Future<Either<AppError, void>> deleteUser(String userId) async {
    try {
      await _client.delete<void>('/admin/users/$userId');
      return const Right(null);
    } catch (e, st) {
      return Left(_handleError(e, st));
    }
  }

  /// **Get Queue Statistics**
  ///
  /// Fetches real-time status of the system job queue (ArQ).
  ///
  /// **Endpoint**: `GET /api/v1/admin/system/queue`
  Future<Either<AppError, QueueStats>> getQueueStats() async {
    try {
      final response = await _client.get<Map<String, dynamic>>(
        '/admin/system/queue',
      );
      final data = response.data;
      if (data == null) throw Exception('Response data is null');
      return Right(QueueStats.fromJson(data));
    } catch (e, st) {
      return Left(_handleError(e, st));
    }
  }

  /// **Centralized Error Handler**
  ///
  /// Maps Dio exceptions to domain [AppError]s.
  AppError _handleError(Object e, StackTrace st) {
    if (e is DioException) {
      final response = e.response;
      if (response != null) {
        final statusCode = response.statusCode;
        final data = response.data;

        // 1. Check for specific business rule violations
        if (statusCode == 409 && data is Map<String, dynamic>) {
          // New APIError Schema Support
          if (data['message'] == 'LAST_ADMIN_PROTECTION' ||
              (data['details'] is Map &&
                  data['details']['error_code'] == 'LAST_ADMIN_PROTECTION')) {
            return const AppError.validation(
              ValidationErrorReason.demoteLastAdmin,
            );
          }

          // Legacy Support (keep for transition if needed, or remove if strict)
          if (data.containsKey('detail')) {
            final detail = data['detail'];
            if (detail is Map &&
                detail['error_code'] == 'LAST_ADMIN_PROTECTION') {
              return const AppError.validation(
                ValidationErrorReason.demoteLastAdmin,
              );
            }
            if (detail == 'LAST_ADMIN_PROTECTION') {
              return const AppError.validation(
                ValidationErrorReason.demoteLastAdmin,
              );
            }
          }
        }

        // 2. Generic Status Codes
        switch (statusCode) {
          case 401:
            return const AppError.unauthorized();
          case 403:
            // Map 403 to unauthorized per requirement
            return const AppError.unauthorized();
          case 404:
            return AppError.notFound(
              data is Map ? data['detail'].toString() : 'Resource not found',
            );
          case 400:
          case 422:
            return const AppError.validation(ValidationErrorReason.unknown);
          case 500:
          default:
            return AppError.server(
              data is Map ? data['detail'].toString() : 'Server Error',
              statusCode,
            );
        }
      }
      return const AppError.network();
    }
    return AppError.unknown(e, st);
  }
}
