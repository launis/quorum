import 'dart:async';
import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/core/network/api_client.dart';
import 'package:client_app/core/error/app_error.dart';

final sseClientProvider = Provider<SseClient>((ref) {
  return SseClient(ref.watch(apiClientProvider));
});

/// **Server-Sent Events (SSE) Client**
///
/// Responsible for establishing a streaming connection with the V2 Backend
/// for DAG execution (e.g. POST /api/v2/executions/run).
///
/// It converts the raw `data: {...}` lines emitted by the server into a typed
/// `Stream<Map<String, dynamic>>` for the Riverpod AsyncNotifier to consume.
class SseClient {
  final Dio _dio;

  SseClient(this._dio);

  /// Executes a DAG workflow and listens to the SSE stream.
  ///
  /// [url] the POST endpoint (e.g. /api/v2/executions/run).
  /// [data] the payload to send (initial expected_inputs and workflow ID).
  ///
  /// Returns a stream of parsed JSON objects. Each object represents
  /// a state update from the server (e.g. a node completing).
  Stream<Map<String, dynamic>> listenToPost(
    String url,
    Map<String, dynamic> data,
  ) async* {
    try {
      final response = await _dio.post<ResponseBody>(
        url,
        data: data,
        options: Options(
          responseType: ResponseType.stream,
          headers: {'Accept': 'text/event-stream'},
          // Disable timeouts for long-running DAG streams
          receiveTimeout: Duration.zero,
        ),
      );

      final stream = response.data?.stream;
      if (stream == null) {
        throw const AppError.serverParsingError('SSE stream was null.');
      }

      // Convert byte stream to string stream, splitting by lines
      final lineStream = stream
          .cast<List<int>>()
          .transform(utf8.decoder)
          .transform(const LineSplitter());

      await for (final line in lineStream) {
        if (line.isEmpty) continue;

        // Ensure it's an SSE data line
        if (line.startsWith('data:')) {
          final jsonString = line.substring(5).trim();

          if (jsonString.isEmpty) continue;

          try {
            final decoded = jsonDecode(jsonString);
            if (decoded is Map<String, dynamic>) {
              yield decoded;
            } else {
              // Graceful degradation / defense: log and ignore non-map lines
              // In V2, we enforce Map structures for UI hints.
            }
          } catch (e) {
            // Log parsing error but don't crash stream unless it's fatal
            // RFC 7807 Fail-Fast applies at the service boundary, but here
            // we are receiving a corrupted chunk. Let's yield an error object
            // or re-throw if needed.
            throw AppError.serverParsingError(
              'Failed to parse SSE line: $jsonString',
            );
          }
        }
      }
    } on DioException {
      // Caught Dio exceptions will be handled by the ErrorInterceptor
      // which attaches RFC 7807 problem details if available.
      rethrow;
    } catch (e) {
      throw AppError.networkError('SSE stream failed: $e');
    }
  }
}
