import 'package:dio/dio.dart';
import 'package:fpdart/fpdart.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:client_app/api/api_client.dart';
import 'package:client_app/core/error/app_error.dart';
import 'package:client_app/features/usage/domain/models/usage_report.dart';

part 'usage_repository.g.dart';

@Riverpod(keepAlive: true)
UsageRepository usageRepository(Ref ref) {
  return UsageRepository(ref.watch(apiClientProvider));
}

class UsageRepository {
  final Dio _client;

  UsageRepository(this._client);

  Future<Either<AppError, UsageReport>> fetchSystemUsage() async {
    return _fetchUsageReport('/v1/usage/system');
  }

  Future<Either<AppError, UsageReport>> fetchOrganizationUsage(
    String orgId,
  ) async {
    return _fetchUsageReport('/v1/usage/organization/$orgId');
  }

  Future<Either<AppError, UsageReport>> fetchUserUsage() async {
    return _fetchUsageReport('/v1/usage/user/me');
  }

  Future<Either<AppError, UsageReport>> _fetchUsageReport(
    String endpoint,
  ) async {
    try {
      final response = await _client.get<Map<String, dynamic>>(endpoint);
      final data = response.data;
      if (data == null) throw Exception('Response data is null');
      return Right(UsageReport.fromJson(data));
    } catch (e, st) {
      if (e is DioException) {
        final response = e.response;
        if (response != null) {
          final statusCode = response.statusCode;
          if (statusCode == 401) return const Left(AppError.unauthorized());
          if (statusCode == 403) return const Left(AppError.unauthorized());
          if (statusCode == 404)
            return const Left(AppError.notFound('Usage not found'));
        }
        return const Left(AppError.network());
      }
      return Left(AppError.unknown(e, st));
    }
  }
}
