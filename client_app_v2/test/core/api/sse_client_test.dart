import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';
import 'package:client_app/core/api/sse_client.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/features/execution/models/execution_record.dart';
import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

class MockDio extends Mock implements Dio {}

class MockLoggerService extends Mock implements LoggerService {}

void main() {
  late MockDio mockDio;
  late MockLoggerService mockLogger;
  late SseClient sseClient;

  const validExecutionId = 'exe_9cbe266a998d43b485bce03cf2b72234';

  setUp(() {
    mockDio = MockDio();
    mockLogger = MockLoggerService();
    sseClient = SseClient(mockDio, mockLogger);
  });

  group('SseClient SSE Deserialization, Boundary & Negative Tests', () {
    test(
      'Positive 1: subscribeToExecution preserves target_locale and non-heavy fields so ExecutionRecord parses successfully',
      () async {
        const backendPayload = {
          'id': validExecutionId,
          'workflow_id': 'wf_9d68c573802341db',
          'target_locale': 'fi',
          'status': 'RUNNING',
          'duration_ms': 1200,
          'cost_estimate': 0.045,
          'step_states': {
            'sr_f0a26d17cc9b48a7': {
              'id': 'sr_f0a26d17cc9b48a7',
              'label': 'sr_f0a26d17cc9b48a7',
              'status': 'RUNNING',
            },
          },
          'frozen_context': {
            'version_id': 'v_initial',
            'heavy_snapshot_data': {'some': 'large_nested_data'},
          },
        };

        final sseDataString = 'data: ${jsonEncode(backendPayload)}\n\n';
        final streamController = StreamController<Uint8List>();

        when(
          () => mockDio.get<ResponseBody>(
            '/execution/executions/$validExecutionId/stream',
            options: any(named: 'options'),
          ),
        ).thenAnswer(
          (_) async => Response<ResponseBody>(
            data: ResponseBody(
              streamController.stream,
              200,
              headers: {
                Headers.contentTypeHeader: ['text/event-stream'],
              },
            ),
            statusCode: 200,
            requestOptions: RequestOptions(
              path: '/execution/executions/$validExecutionId/stream',
            ),
          ),
        );

        final emittedFuture = sseClient
            .subscribeToExecution(validExecutionId)
            .first;

        streamController.add(Uint8List.fromList(utf8.encode(sseDataString)));
        await streamController.close();

        final update = await emittedFuture;

        expect(update['id'], validExecutionId);
        expect(update['workflow_id'], 'wf_9d68c573802341db');
        expect(update['target_locale'], 'fi');
        expect(update['frozen_context'], {'version_id': 'v_initial'});

        // Verify that ExecutionRecord parses without CheckedFromJsonException
        final record = ExecutionRecord.fromJson(update);
        expect(record.id, validExecutionId);
        expect(record.targetLocale, 'fi');
        expect(record.status, 'RUNNING');
      },
    );

    test(
      'Positive 2 (Boundary): ignores non-data SSE comments, empty data lines, and nullifies frozen_context lacking version_id',
      () async {
        const backendPayload = {
          'id': validExecutionId,
          'workflow_id': 'wf_9d68c573802341db',
          'target_locale': 'en',
          'status': 'PASSED',
          'frozen_context': {'unexpected_key': 'no_version'},
        };

        final rawSseStream =
            ': keep-alive\n'
            'event: message\n'
            'data:    \n'
            'data: ${jsonEncode(backendPayload)}\n\n';
        final streamController = StreamController<Uint8List>();

        when(
          () => mockDio.get<ResponseBody>(
            '/execution/executions/$validExecutionId/stream',
            options: any(named: 'options'),
          ),
        ).thenAnswer(
          (_) async => Response<ResponseBody>(
            data: ResponseBody(streamController.stream, 200),
            statusCode: 200,
            requestOptions: RequestOptions(
              path: '/execution/executions/$validExecutionId/stream',
            ),
          ),
        );

        final updatesFuture = sseClient
            .subscribeToExecution(validExecutionId)
            .toList();

        streamController.add(Uint8List.fromList(utf8.encode(rawSseStream)));
        await streamController.close();

        final updates = await updatesFuture;
        expect(updates, hasLength(1));
        expect(updates.first['frozen_context'], isNull);
      },
    );

    test(
      'Negative 1 (Boundary): throws AppException.validation and logs error when executionId violates 32-hex Opaque Stripe ID format',
      () async {
        for (final invalidId in [
          '',
          'exe_9cbe266a998d43b4', // 16-hex truncated (min-1 length boundary)
          'exe_9cbe266a998d43b485bce03cf2b722345', // 33-hex (max+1 length boundary)
          'invalid-id',
        ]) {
          await expectLater(
            sseClient.subscribeToExecution(invalidId).first,
            throwsA(isA<AppException>()),
          );
        }

        verify(
          () => mockLogger.error(any(), any(), any(), any()),
        ).called(4);
        verifyNever(
          () => mockDio.get<ResponseBody>(
            any(),
            options: any(named: 'options'),
          ),
        );
      },
    );

    test(
      'Negative 2: throws AppException.network and logs error when response.data is null',
      () async {
        when(
          () => mockDio.get<ResponseBody>(
            '/execution/executions/$validExecutionId/stream',
            options: any(named: 'options'),
          ),
        ).thenAnswer(
          (_) async => Response<ResponseBody>(
            data: null,
            statusCode: 200,
            requestOptions: RequestOptions(
              path: '/execution/executions/$validExecutionId/stream',
            ),
          ),
        );

        await expectLater(
          sseClient.subscribeToExecution(validExecutionId).first,
          throwsA(
            isA<AppException>().having(
              (e) => e.detail,
              'detail',
              contains('Failed to establish SSE connection'),
            ),
          ),
        );

        verify(
          () => mockLogger.error(
            'SseClient',
            any(that: contains('Failed to establish SSE connection')),
            any(),
            any(),
          ),
        ).called(1);
      },
    );

    test(
      'Negative 3: logs error via LoggerService and rethrows on malformed JSON SSE chunk',
      () async {
        final streamController = StreamController<Uint8List>();

        when(
          () => mockDio.get<ResponseBody>(
            '/execution/executions/$validExecutionId/stream',
            options: any(named: 'options'),
          ),
        ).thenAnswer(
          (_) async => Response<ResponseBody>(
            data: ResponseBody(streamController.stream, 200),
            statusCode: 200,
            requestOptions: RequestOptions(
              path: '/execution/executions/$validExecutionId/stream',
            ),
          ),
        );

        final streamFuture = sseClient
            .subscribeToExecution(validExecutionId)
            .toList();

        streamController.add(
          Uint8List.fromList(utf8.encode('data: {malformed_json\n\n')),
        );
        await streamController.close();

        await expectLater(streamFuture, throwsA(isA<FormatException>()));

        verify(
          () => mockLogger.error(
            'SseClient',
            'Malformed SSE chunk received or processing failed',
            any(),
            any(),
          ),
        ).called(1);
      },
    );
  });
}
