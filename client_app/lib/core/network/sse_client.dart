import 'dart:async';
import 'dart:convert';
import 'package:dio/dio.dart';

/// **SSE Client**
///
/// Handles Server-Sent Events subscription using Dio.
/// Supports standard 'data: ...' event parsing.
class SseClient {
  final Dio _dio;

  SseClient(this._dio);

  /// Subscribes to an SSE endpoint.
  ///
  /// Yields decoded JSON objects or raw strings from the 'data' field.
  Stream<dynamic> subscribe(String url) async* {
    try {
      final response = await _dio.get<ResponseBody>(
        url,
        options: Options(
          responseType: ResponseType.stream,
          headers: {
            'Accept': 'text/event-stream',
            'Cache-Control': 'no-cache',
          },
        ),
      );

      final stream = response.data?.stream;
      if (stream == null) return;

      // Decode bytes to string, split by lines
      final lineStream = stream
          .cast<List<int>>() // Ensure it's typed as bytes
          .transform(utf8.decoder)
          .transform(const LineSplitter());

      await for (final line in lineStream) {
        if (line.startsWith('data:')) {
          final data = line.substring(5).trim();
          if (data.isEmpty) continue;

          try {
            yield jsonDecode(data);
          } catch (_) {
            yield data; // Return raw string if not JSON
          }
        }
        // Handle 'event:', 'id:', 'retry:' if needed later
      }
    } catch (e) {
      // Re-throw or handle disconnection
      throw Exception('SSE Connection failed: $e');
    }
  }
}
