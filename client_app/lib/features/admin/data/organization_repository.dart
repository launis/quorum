import 'package:client_app/api/api_client.dart';
import 'package:client_app/core/error/app_error.dart';
import 'package:client_app/features/admin/domain/models/organization.dart';
import 'package:dio/dio.dart';
import 'package:fpdart/fpdart.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'organization_repository.g.dart';

@Riverpod(keepAlive: true)
OrganizationRepository organizationRepository(Ref ref) {
  return OrganizationRepository(ref.watch(apiClientProvider));
}

class OrganizationRepository {
  final Dio _client;

  OrganizationRepository(this._client);

  /// Fetch all organizations.
  /// GET /api/v1/organizations
  Future<Either<AppError, List<Organization>>> fetchOrganizations() async {
    try {
      final response = await _client.get<List<dynamic>>('/organizations');

      if (response.data == null) {
        return right([]);
      }

      final organizations =
          response.data!
              .map(
                (json) => Organization.fromJson(json as Map<String, dynamic>),
              )
              .toList();

      return right(organizations);
    } on DioException catch (e) {
      if (e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.receiveTimeout ||
          e.type == DioExceptionType.sendTimeout ||
          e.type == DioExceptionType.connectionError) {
        return left(AppError.network(e));
      }
      return left(AppError.server(e.message, e.response?.statusCode));
    } catch (e, stackTrace) {
      return left(AppError.unknown(e, stackTrace));
    }
  }

  /// Update an organization.
  /// PATCH /api/v1/organizations/{id}
  Future<Either<AppError, Organization>> updateOrganization(
    String id,
    Map<String, dynamic> data,
  ) async {
    try {
      final response = await _client.patch<Map<String, dynamic>>(
        '/organizations/$id',
        data: data,
      );

      if (response.data == null) {
        return left(const AppError.server('Response data was null'));
      }

      return right(Organization.fromJson(response.data!));
    } on DioException catch (e) {
      if (e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.receiveTimeout ||
          e.type == DioExceptionType.sendTimeout ||
          e.type == DioExceptionType.connectionError) {
        return left(AppError.network(e));
      }
      return left(AppError.server(e.message, e.response?.statusCode));
    } catch (e, stackTrace) {
      return left(AppError.unknown(e, stackTrace));
    }
  }

  /// Create a new organization.
  /// POST /api/v1/organizations
  Future<Either<AppError, Organization>> createOrganization(
    Map<String, dynamic> data,
  ) async {
    try {
      final response = await _client.post<Map<String, dynamic>>(
        '/organizations/',
        data: data,
      );

      if (response.data == null) {
        return left(const AppError.server('Response data was null'));
      }

      return right(Organization.fromJson(response.data!));
    } on DioException catch (e) {
      if (e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.receiveTimeout ||
          e.type == DioExceptionType.sendTimeout ||
          e.type == DioExceptionType.connectionError) {
        return left(AppError.network(e));
      }
      return left(AppError.server(e.message, e.response?.statusCode));
    } catch (e, stackTrace) {
      return left(AppError.unknown(e, stackTrace));
    }
  }

  /// Delete an organization.
  /// DELETE /api/v1/organizations/{id}?force={true|false}
  Future<Either<AppError, Unit>> deleteOrganization(
    String id, {
    bool force = false,
  }) async {
    try {
      await _client.delete<Unit>(
        '/organizations/$id',
        queryParameters: {'force': force},
      );
      return right(unit);
    } on DioException catch (e) {
      if (e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.receiveTimeout ||
          e.type == DioExceptionType.sendTimeout ||
          e.type == DioExceptionType.connectionError) {
        return left(AppError.network(e));
      }
      String? message = e.message;
      final data = e.response?.data;

      if (data != null) {
        if (data is Map) {
          if (data['detail'] != null) {
            message = data['detail'].toString();
          } else if (data['message'] != null) {
            message = data['message'].toString();
          }
        } else if (data is String) {
          message = data;
        }
      }
      return left(AppError.server(message, e.response?.statusCode));
    } catch (e, stackTrace) {
      return left(AppError.unknown(e, stackTrace));
    }
  }

  /// Get usage stats for an organization.
  /// GET /api/v1/organizations/{id}/usage
  Future<Either<AppError, Map<String, dynamic>>> getUsage(String id) async {
    try {
      final response = await _client.get<Map<String, dynamic>>(
        '/organizations/$id/usage',
      );

      if (response.data == null) {
        return left(const AppError.server('Response data was null'));
      }

      return right(response.data!);
    } on DioException catch (e) {
      if (e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.receiveTimeout ||
          e.type == DioExceptionType.sendTimeout ||
          e.type == DioExceptionType.connectionError) {
        return left(AppError.network(e));
      }
      return left(AppError.server(e.message, e.response?.statusCode));
    } catch (e, stackTrace) {
      return left(AppError.unknown(e, stackTrace));
    }
  }

  /// Get detailed usage stats for an organization.
  /// GET /api/v1/organizations/{id}/usage/detailed
  Future<Either<AppError, Map<String, dynamic>>> getDetailedUsage(
    String id, {
    String scope = 'org',
  }) async {
    try {
      final response = await _client.get<Map<String, dynamic>>(
        '/organizations/$id/usage/detailed',
        queryParameters: {'scope': scope},
      );

      if (response.data == null) {
        return left(const AppError.server('Response data was null'));
      }

      return right(response.data!);
    } on DioException catch (e) {
      if (e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.receiveTimeout ||
          e.type == DioExceptionType.sendTimeout ||
          e.type == DioExceptionType.connectionError) {
        return left(AppError.network(e));
      }
      return left(AppError.server(e.message, e.response?.statusCode));
    } catch (e, stackTrace) {
      return left(AppError.unknown(e, stackTrace));
    }
  }
}
