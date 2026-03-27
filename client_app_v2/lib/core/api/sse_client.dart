import 'dart:convert';
import 'dart:isolate';
import 'package:dio/dio.dart';
import 'package:client_app/core/network/api_client.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'sse_client.g.dart';

/// SSE API Client Provider
@riverpod
SseClient sseClient(Ref ref) {
  return SseClient(
    ref.watch(apiClientProvider),
    ref.watch(loggerServiceProvider),
  );
}

/// Client for interacting with Server-Sent Events (SSE).
///
/// Strictly adheres to V2 De-Generator policy. Yields raw Maps.
class SseClient {
  final Dio _dio;
  final LoggerService _logger;

  SseClient(this._dio, this._logger);

  /// Subscribes to an execution's live SSE stream.
  ///
  /// Yields dynamic maps representing the current execution state or results.
  /// Fails fast if the stream cannot be established.
  Stream<Map<String, dynamic>> subscribeToExecution(String executionId) async* {
    final response = await _dio.get<ResponseBody>(
      '/execution/executions/$executionId/stream',
      options: Options(
        responseType: ResponseType.stream,
        headers: {'Accept': 'text/event-stream', 'Cache-Control': 'no-cache'},
      ),
    );

    final stream = response.data?.stream;
    if (stream == null) {
      throw AppException.network('Failed to establish SSE connection');
    }

    // Process the raw byte stream into continuous lines to prevent fragmentation
    final lineStream = stream
        .cast<List<int>>()
        .transform(utf8.decoder)
        .transform(const LineSplitter());

    await for (final line in lineStream) {
      if (line.startsWith('data: ')) {
        final dataStr = line.substring(6).trim();
        if (dataStr.isNotEmpty) {
          try {
            // Mandate 5.3: Concurrency & Performance via Isolate.run
            // V3: Refactor to Delta Signal exclusively. Only process lightweight changes.
            final Map<String, dynamic> payload = await Isolate.run(() {
              final raw = jsonDecode(dataStr) as Map<String, dynamic>;
              return {
                'id': raw['id'],
                'workflow_id': raw['workflow_id'],
                'status': raw['status'],
                'trace_version': raw['trace_version'],
                'logs': raw['logs'], // keep short logs if any
                'step_states':
                    raw['step_states'], // Lightweight Timeline status
                'frozen_context':
                    (raw['frozen_context'] is Map &&
                            (raw['frozen_context'] as Map).containsKey(
                              'version_id',
                            ))
                        ? {'version_id': raw['frozen_context']['version_id']}
                        : null, // Only version_id for Drift Warning, strip heavy context
              };
            });
            yield payload;
          } catch (e, st) {
            // Dual-Reporting Mandate: First log structurally before Graceful Degradation
            _logger.error(
              'SseClient',
              'Malformed SSE chunk received or processing failed',
              e,
              st,
            );
            // Absolute Death Mandate: Fail-fast and terminate the stream on fragment corruption
            rethrow;
          }
        }
      }
    }
  }
}
