import 'package:dio/dio.dart';
import 'package:fpdart/fpdart.dart';
import 'package:client_app/core/error/app_error.dart';
import 'package:client_app/features/admin/domain/models/system_preview.dart';

class SystemRepository {
  final Dio _client;

  SystemRepository(this._client);

  /// **Get Step Preview**
  ///
  /// Generates a preview for a specific Step.
  ///
  /// **Endpoint**: `POST /builder/steps/{stepId}/preview`
  Future<Either<AppError, SystemPreview>> getStepPreview(String stepId) async {
    try {
      final response = await _client.post<Map<String, dynamic>>(
        '/builder/steps/$stepId/preview',
      );
      final data = response.data;
      if (data == null) throw Exception('Response data is null');
      return Right(SystemPreview.fromJson(data));
    } catch (e, st) {
      return Left(_handleError(e, st));
    }
  }

  /// **Get Chain Preview**
  ///
  /// Generates a preview for the entire Workflow Chain.
  ///
  /// **Endpoint**: `GET /builder/workflows/{workflowId}/chain-preview`
  Future<Either<AppError, ChainPreview>> getChainPreview(
    String workflowId,
  ) async {
    try {
      final response = await _client.get<Map<String, dynamic>>(
        '/builder/workflows/$workflowId/chain-preview',
      );
      final data = response.data;
      if (data == null) throw Exception('Response data is null');
      return Right(ChainPreview.fromJson(data));
    } catch (e, st) {
      return Left(_handleError(e, st));
    }
  }

  /// **Centralized Error Handler**
  AppError _handleError(Object e, StackTrace st) {
    if (e is DioException) {
      final response = e.response;
      if (response != null) {
        final statusCode = response.statusCode;
        final data = response.data;

        switch (statusCode) {
          case 401:
          case 403:
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
