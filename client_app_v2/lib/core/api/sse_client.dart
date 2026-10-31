import 'dart:convert';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/core/network/api_client.dart';
import 'package:client_app/core/utils/safe_isolate.dart';
import 'package:client_app/utils/json_converters.dart';
import 'package:dio/dio.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'sse_client.g.dart';

/// SSE API Client Provider
@Riverpod(keepAlive: true)
SseClient sseClient(Ref ref) {
  return SseClient(
    ref.watch(apiClientProvider),
    ref.watch(loggerServiceProvider),
  );
}

/// Client for interacting with Server-Sent Events (SSE).
///
/// Yields decoded JSON payload maps for downstream DTO hydration.
class SseClient {
  final Dio _dio;
  final LoggerService _logger;
  static const StrictOpaqueIdConverter _idValidator = StrictOpaqueIdConverter();

  SseClient(this._dio, this._logger);

  void _validateOpaqueId(String id, String fieldName, String methodName) {
    try {
      _idValidator.fromJson(id);
    } on AppException catch (e, st) {
      _logger.error(
        'SseClient',
        'Invalid $fieldName format "$id" for $methodName',
        e,
        st,
      );
      rethrow;
    }
  }

  /// Subscribes to an execution's live SSE stream.
  ///
  /// Yields maps representing the current execution state or results.
  /// Fails fast if the identifier is invalid or the stream cannot be established.
  Stream<Map<String, Object?>> subscribeToExecution(String executionId) async* {
    _validateOpaqueId(executionId, 'executionId', 'subscribeToExecution');

    final response = await _dio.get<ResponseBody>(
      '/execution/executions/$executionId/stream',
      options: Options(
        responseType: ResponseType.stream,
        headers: {'Accept': 'text/event-stream', 'Cache-Control': 'no-cache'},
        receiveTimeout: Duration(
          seconds: SystemConcurrency.sseTimeoutSeconds.value,
        ),
      ),
    );

    final stream = response.data?.stream;
    if (stream == null) {
      final error = AppException.network('Failed to establish SSE connection');
      _logger.error(
        'SseClient',
        'Failed to establish SSE connection: null stream for $executionId',
        error,
        StackTrace.current,
      );
      throw error;
    }

    // Process the raw byte stream into continuous lines to prevent fragmentation
    final lineStream = stream
        .cast<List<int>>()
        .transform(utf8.decoder)
        .transform(const LineSplitter());

    await for (final line in lineStream) {
      if (line.startsWith('data: ')) {
        final dataStr = line.replaceFirst('data: ', '').trim();
        if (dataStr.isNotEmpty) {
          try {
            // Offload payload decoding and strip heavy snapshot data outside version_id
            final Map<String, Object?> payload = await safeIsolateRun(() {
              final raw = jsonDecode(dataStr) as Map<String, Object?>;
              final result = Map<String, Object?>.from(raw);
              if (raw.containsKey('frozen_context')) {
                final fc = raw['frozen_context'];
                result['frozen_context'] =
                    (fc is Map && fc.containsKey('version_id'))
                    ? {'version_id': fc['version_id']}
                    : null;
              }
              return result;
            });
            yield payload;
          } catch (e, st) {
            // Dual-Reporting Mandate: First log structurally before failing fast
            _logger.error(
              'SseClient',
              'Malformed SSE chunk received or processing failed',
              e,
              st,
            );
            // Fail-fast and terminate the stream on fragment corruption
            rethrow;
          }
        }
      }
    }
  }
}
