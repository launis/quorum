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
    final client = dio ?? Dio();

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

        // Split by double newlines (\n\n) which separate SSE events
        while (buffer.contains('\n\n')) {
          final index = buffer.indexOf('\n\n');
          final eventBlock = buffer.substring(0, index);
          buffer = buffer.substring(index + 2);

          // Process lines within the event block
          final lines = LineSplitter.split(eventBlock);

          for (final line in lines) {
            // Filter lines starting with data:
            if (line.startsWith('data:')) {
              final rawData = line.substring(5).trim();

              if (rawData.isNotEmpty) {
                try {
                  final json = jsonDecode(rawData);
                  if (json is Map<String, dynamic>) {
                    yield parser(json);
                  }
                } catch (e) {
                  // Ignore malformed JSON strings as per "Parse valid JSON strings" instruction
                }
              }
            }
          }
        }
      }
    } on DioException catch (e) {
      // Re-throw DioException as AppError.network
      throw AppError.network(e);
    } catch (e) {
      // Re-throw if it's already an AppError, otherwise wrap in unknown
      if (e is AppError) rethrow;
      throw AppError.unknown(e);
    }
  }
}
