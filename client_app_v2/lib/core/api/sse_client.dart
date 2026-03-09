import 'dart:convert';
import 'dart:isolate';
import 'package:dio/dio.dart';
import 'package:client_app/core/network/api_client.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'sse_client.g.dart';

/// SSE API Client Provider
@riverpod
SseClient sseClient(Ref ref) {
  return SseClient(ref.watch(apiClientProvider));
}

/// Client for interacting with Server-Sent Events (SSE).
///
/// Strictly adheres to V2 De-Generator policy. Yields raw Maps.
class SseClient {
  final Dio _dio;

  SseClient(this._dio);

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
      throw Exception('Failed to establish SSE connection');
    }

    // Process the raw byte stream into lines, then extract SSE data payload
    await for (final rawData in stream) {
      final chunk = utf8.decode(rawData);
      final lines = chunk.split('\n');

      for (final line in lines) {
        if (line.startsWith('data: ')) {
          final dataStr = line.substring(6).trim();
          if (dataStr.isNotEmpty) {
            try {
              // Mandate 5.3: Concurrency & Performance via Isolate.run
              final Map<String, dynamic> payload = await Isolate.run(
                () => jsonDecode(dataStr),
              );
              yield payload;
            } catch (e) {
              // Log but graceful degradation: ignore malformed chunk
              // Exception to Fail-Fast since SSE chunks can sometimes fragment.
            }
          }
        }
      }
    }
  }
}
