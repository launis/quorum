import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';
import 'package:client_app/core/api/sse_client.dart';
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

  setUp(() {
    mockDio = MockDio();
    mockLogger = MockLoggerService();
    sseClient = SseClient(mockDio, mockLogger);
  });

  group('SseClient SSE Deserialization & Field Parity', () {
    test(
      'subscribeToExecution preserves target_locale and non-heavy fields so ExecutionRecord parses successfully',
      () async {
        const backendPayload = {
          'id': 'exe_9cbe266a998d43b485bce03cf2b72234',
          'workflow_id': 'wf_9d68c573802341db',
          'target_locale': 'fi',
          'status': 'RUNNING',
          'trace_version': '1.0',
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
            '/execution/executions/exe_9cbe266a998d43b485bce03cf2b72234/stream',
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
              path:
                  '/execution/executions/exe_9cbe266a998d43b485bce03cf2b72234/stream',
            ),
          ),
        );

        final emittedFuture = sseClient
            .subscribeToExecution('exe_9cbe266a998d43b485bce03cf2b72234')
            .first;

        streamController.add(Uint8List.fromList(utf8.encode(sseDataString)));
        await streamController.close();

        final update = await emittedFuture;

        expect(update['id'], 'exe_9cbe266a998d43b485bce03cf2b72234');
        expect(update['workflow_id'], 'wf_9d68c573802341db');
        expect(update['target_locale'], 'fi');

        // Verify that ExecutionRecord parses without CheckedFromJsonException
        final record = ExecutionRecord.fromJson(update);
        expect(record.id, 'exe_9cbe266a998d43b485bce03cf2b72234');
        expect(record.targetLocale, 'fi');
        expect(record.status, 'RUNNING');
      },
    );
  });
}
