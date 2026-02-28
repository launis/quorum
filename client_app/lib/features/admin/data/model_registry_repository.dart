import 'package:dio/dio.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import '../../../../api/api_client.dart';
import '../../../../core/error/app_error.dart';
import 'package:fpdart/fpdart.dart';
import '../domain/models/model_registry.dart';

class ModelRegistryRepository {
  final Dio _client;

  ModelRegistryRepository(this._client);

  Future<Either<AppError, List<LLMProviderConfig>>> getProviders() async {
    try {
      final response = await _client.get<List<dynamic>>('/v1/config/models');
      final data = response.data;
      if (data == null) return const Right([]);

      final providers =
          data
              .map((e) => LLMProviderConfig.fromJson(e as Map<String, dynamic>))
              .toList();
      return Right(providers);
    } catch (e, st) {
      return Left(_handleError(e, st));
    }
  }

  Future<Either<AppError, LLMProviderConfig>> updateProvider(
    String providerId,
    LLMProviderConfig config,
  ) async {
    try {
      final response = await _client.put<Map<String, dynamic>>(
        '/v1/config/models/$providerId',
        data: config.toJson(),
      );
      final data = response.data;
      if (data == null) throw Exception('Response data is null');

      return Right(LLMProviderConfig.fromJson(data));
    } catch (e, st) {
      return Left(_handleError(e, st));
    }
  }

  Future<Either<AppError, Unit>> deleteProvider(String providerId) async {
    try {
      await _client.delete<void>('/v1/config/models/$providerId');
      return const Right(unit);
    } catch (e, st) {
      return Left(_handleError(e, st));
    }
  }

  Future<Either<AppError, AdHocTestResult>> runAdHocTest(
    AdHocTestRequest request,
  ) async {
    try {
      final response = await _client.post<Map<String, dynamic>>(
        '/v1/config/models/test',
        data: request.toJson(),
        options: Options(receiveTimeout: const Duration(seconds: 120)),
      );
      final data = response.data;
      if (data == null) throw Exception('Response data is null');

      return Right(AdHocTestResult.fromJson(data));
    } catch (e, st) {
      return Left(_handleError(e, st));
    }
  }

  Future<Either<AppError, Map<String, List<String>>>> getModelOptions() async {
    try {
      final response = await _client.get<Map<String, dynamic>>(
        '/v1/config/models/options',
        options: Options(receiveTimeout: const Duration(seconds: 60)),
      );
      final data = response.data;
      if (data == null) return const Right({});

      // STRICT SSOT: Backend sends ModelOptionsResponse(options=...)
      final optionsMap = data['options'];
      if (optionsMap is! Map) {
        // Fallback or returned empty?
        return const Right({});
      }

      final map = <String, List<String>>{};
      optionsMap.forEach((key, value) {
        if (value is List) {
          map[key.toString()] =
              (value as List).map((e) => e.toString()).toList();
        }
      });
      return Right(map);
    } catch (e, st) {
      return Left(_handleError(e, st));
    }
  }

  Future<Either<AppError, Map<String, ({String? strategyId, String name})>>>
  getAgentMappings() async {
    try {
      final response = await _client.get<List<dynamic>>(
        '/v1/config/models/mappings',
      );
      final data = response.data;
      if (data == null) return const Right({});

      final map = <String, ({String? strategyId, String name})>{};
      for (final item in data) {
        if (item is Map<String, dynamic>) {
          final agentId = item['agent_id'] as String;
          final strategyId = item['strategy_id']?.toString();
          final name = item['name']?.toString() ?? agentId;
          map[agentId] = (strategyId: strategyId, name: name);
        }
      }
      return Right(map);
    } catch (e, st) {
      return Left(_handleError(e, st));
    }
  }

  Future<Either<AppError, Map<String, ({String? strategyId, String name})>>>
  updateAgentMapping(
    String agentId,
    String strategyId, {
    String name = '',
  }) async {
    try {
      await _client.put<Map<String, dynamic>>(
        '/v1/config/models/mappings',
        data: {'agent_id': agentId, 'strategy_id': strategyId},
      );

      // We rely on optimistic update mostly, so we can just return a localized map segment
      // or rely on a full refresh if need be. The backend returns `{agent_id, strategy_id}` for this route.
      return Right({agentId: (strategyId: strategyId, name: name)});
    } catch (e, st) {
      return Left(_handleError(e, st));
    }
  }

  AppError _handleError(Object e, StackTrace st) {
    if (e is DioException) {
      if (e.error is AppError) {
        return e.error as AppError;
      }
      if (e.type == DioExceptionType.connectionError ||
          e.type == DioExceptionType.connectionTimeout) {
        return const AppError.network();
      }
      if (e.type == DioExceptionType.cancel) {
        return const AppError.cancelled();
      }
      final response = e.response;
      if (response != null) {
        final statusCode = response.statusCode;
        final data = response.data;
        switch (statusCode) {
          case 401:
            return const AppError.unauthorized();
          case 404:
            return AppError.notFound(data.toString());
          default:
            return AppError.server(data.toString(), statusCode);
        }
      }
    }
    return AppError.unknown(e, st);
  }
}

// Provider defined in presentation/providers/model_registry_providers.dart
