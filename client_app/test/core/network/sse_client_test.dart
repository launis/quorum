import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';
import 'package:client_app/core/error/app_error.dart';
import 'package:client_app/core/network/sse_client.dart';
import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

class MockDio extends Mock implements Dio {}

void main() {
  late MockDio mockDio;

  setUp(() {
    mockDio = MockDio();
    registerFallbackValue(Options());
    registerFallbackValue(RequestOptions(path: ''));
    registerFallbackValue(CancelToken());
  });

  test('connect emits parsed objects from stream', () async {
    final streamController = StreamController<Uint8List>();
    final responseBody = ResponseBody(streamController.stream, 200);

    when(
      () => mockDio.get<ResponseBody>(
        any(),
        queryParameters: any(named: 'queryParameters'),
        cancelToken: any(named: 'cancelToken'),
        options: any(named: 'options'),
      ),
    ).thenAnswer(
      (_) async => Response<ResponseBody>(
        requestOptions: RequestOptions(path: '/test'),
        data: responseBody,
        statusCode: 200,
      ),
    );

    final stream = SseClient.connect<Map<String, int>>(
      url: '/test',
      parser: (json) => {'val': json['val'] as int},
      dio: mockDio,
    );

    final expectation = expectLater(
      stream,
      emitsInOrder([
        {'val': 1},
        {'val': 2},
        emitsDone,
      ]),
    );

    // Simulate SSE chunks
    streamController.add(Uint8List.fromList(utf8.encode('data: {"val": 1}\n\n')));
    // Small delay to ensure stream processing
    await Future.delayed(const Duration(milliseconds: 10));

    streamController.add(Uint8List.fromList(utf8.encode('data: {"val": 2}\n\n')));
    await streamController.close();

    await expectation;
  });

  test('connect rethrows DioException as AppError', () async {
    when(
      () => mockDio.get<ResponseBody>(
        any(),
        queryParameters: any(named: 'queryParameters'),
        cancelToken: any(named: 'cancelToken'),
        options: any(named: 'options'),
      ),
    ).thenThrow(
      DioException(
        requestOptions: RequestOptions(path: '/test'),
        type: DioExceptionType.connectionError,
        error: 'Connection failed',
      ),
    );

    final stream = SseClient.connect<void>(
      url: '/test',
      parser: (_) {},
      dio: mockDio,
    );

    await expectLater(stream, emitsError(isA<AppError>()));
  });

  test('connect handles multiline and fragmented events', () async {
    final streamController = StreamController<Uint8List>();
    final responseBody = ResponseBody(streamController.stream, 200);

    when(
      () => mockDio.get<ResponseBody>(
        any(),
        queryParameters: any(named: 'queryParameters'),
        cancelToken: any(named: 'cancelToken'),
        options: any(named: 'options'),
      ),
    ).thenAnswer(
      (_) async => Response<ResponseBody>(
        requestOptions: RequestOptions(path: '/test'),
        data: responseBody,
        statusCode: 200,
      ),
    );

    final stream = SseClient.connect<int>(
      url: '/test',
      parser: (json) => json['val'] as int,
      dio: mockDio,
    );

    final expectation = expectLater(stream, emitsInOrder([1, 2, emitsDone]));

    // Split event across chunks
    streamController.add(Uint8List.fromList(utf8.encode('data: {"v')));
    await Future.delayed(const Duration(milliseconds: 10));
    streamController.add(Uint8List.fromList(utf8.encode('al": 1}\n\n')));

    // Multiple events in one chunk
    streamController.add(Uint8List.fromList(utf8.encode('data: {"val": 2}\n\n')));

    await streamController.close();
    await expectation;
  });
}
