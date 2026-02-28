import 'dart:async';
import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:client_app/core/error/app_error.dart';

/// A reusable client for handling Server-Sent Events (SSE).
class SseClient {
  /// Connects to an SSE endpoint and maps the events to objects of type [T].
  ///
  /// [url] is the endpoint URL.
  /// [parser] is a function that converts the JSON map to [T].
  /// [cancelToken] can be used to cancel the request.
  /// [queryParameters] are optional query parameters for the request.
  /// [dio] is an optional Dio instance for testing or custom configuration.
  static Stream<T> connect<T>({
    required String url,
    required T Function(Map<String, dynamic>) parser,
    CancelToken? cancelToken,
    Map<String, dynamic>? queryParameters,
    Dio? dio,
  }) async* {
    final client =
        dio ??
        Dio(
          BaseOptions(
            connectTimeout: const Duration(seconds: 10),
            receiveTimeout: const Duration(seconds: 30),
          ),
        );

    try {
      final response = await client.get<ResponseBody>(
        url,
        queryParameters: queryParameters,
        cancelToken: cancelToken,
        options: Options(
          responseType: ResponseType.stream,
          headers: {'Accept': 'text/event-stream'},
        ),
      );

      final stream = response.data?.stream;
      if (stream == null) {
        throw const AppError.network('Failed to establish stream connection');
      }

      String buffer = '';

      // Decode the stream from bytes to UTF-8
      await for (final chunk in stream.cast<List<int>>().transform(
        utf8.decoder,
      )) {
        buffer += chunk;

        // Split by double newlines (\n\n or \r\n\r\n) which separate SSE events
        // Using a regex to robustly handle different line endings from server
        final delimiterRegex = RegExp(r'\r\n\r\n|\n\n');

        while (delimiterRegex.hasMatch(buffer)) {
          final match = delimiterRegex.firstMatch(buffer)!;
          final eventBlock = buffer.substring(0, match.start);
          buffer = buffer.substring(match.end);

          // Process lines within the event block
          final lines = LineSplitter.split(eventBlock);

          for (final line in lines) {
            if (line.isNotEmpty) {
              // Temporary Debug Logging
              // print('SSE RAW: $line');
            }
            // Filter lines starting with data:
            if (line.startsWith('data:')) {
              final rawData = line.substring(5).trim();

              if (rawData.isNotEmpty) {
                try {
                  final json = jsonDecode(rawData);
                  // print('SSE Decoded Type: ${json.runtimeType}');
                  if (json is Map<String, dynamic>) {
                    yield parser(json);
                  } else {
                    // print('SSE Type Mismatch: Expected Map<String, dynamic>, got ${json.runtimeType}');
                  }
                } catch (e) {
                  // print('SSE JSON Decode Error: $e');
                  // Ignore malformed JSON strings as per "Parse valid JSON strings" instruction
                }
              }
            }
          }
        }
      }
    } on DioException catch (e) {
      // Handle 404 explicitly for SSE
      if (e.response?.statusCode == 404) {
        throw AppError.notFound(e.message ?? 'Resource not found');
      }
      throw AppError.network(e);
    } catch (e) {
      if (e is AppError) rethrow;
      throw AppError.unknown(e);
    }
  }
}
