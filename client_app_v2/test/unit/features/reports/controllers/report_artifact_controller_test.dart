import 'package:client_app/core/api/reports_client.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/reports/controllers/report_artifact_controller.dart';
import 'package:client_app/features/reports/models/report_artifact.dart';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:json_annotation/json_annotation.dart';
import 'package:mocktail/mocktail.dart';

class MockDio extends Mock implements Dio {}

class MockLoggerService extends Mock implements LoggerService {}

void main() {
  const testExecutionId = 'exe_0195f3a0000070008000000000000001';
  const testReportId = 'rep_0195f3a0000070008000000000000002';
  const testWorkflowId = 'wfl_0195f3a0000070008000000000000003';
  const testProfileId = 'opf_0195f3a0000070008000000000000004';

  late MockDio mockDio;
  late MockLoggerService mockLogger;
  late ReportsClient reportsClient;
  late ProviderContainer container;

  final readySummaryJson = <String, Object?>{
    'id': testReportId,
    'execution_id': testExecutionId,
    'profile_id': testProfileId,
    'locale': 'fi',
    'title': 'Executive Synthesis Report',
    'status': 'ready',
    'created_at': '2026-10-01T12:00:00.000Z',
    'updated_at': '2026-10-01T12:05:00.000Z',
  };

  final readyReportDetailJson = <String, Object?>{
    'id': testReportId,
    'execution_id': testExecutionId,
    'workflow_id': testWorkflowId,
    'profile_id': testProfileId,
    'locale': 'fi',
    'title': 'Executive Synthesis Report',
    'status': 'ready',
    'storage_paths': <String, Object?>{
      'pdf_path': '/files/report.pdf',
      'sdui_json_path': '/files/report_sdui.json',
      'excel_path': '/files/report.xlsx',
      'csv_path': '/files/report.csv',
    },
    'metadata': <String, Object?>{
      'cost_usd': 0.042,
      'duration_ms': 1850,
      'tokens_used': 4200,
    },
    'created_at': '2026-10-01T12:00:00.000Z',
    'updated_at': '2026-10-01T12:05:00.000Z',
  };

  setUp(() {
    mockDio = MockDio();
    mockLogger = MockLoggerService();
    when(
      () => mockDio.options,
    ).thenReturn(BaseOptions(baseUrl: 'https://api.test/api/v2'));
    reportsClient = ReportsClient(mockDio, mockLogger);
    container = ProviderContainer(
      retry: (retryCount, error) => null,
      overrides: [
        reportsClientProvider.overrideWithValue(reportsClient),
        loggerServiceProvider.overrideWithValue(mockLogger),
      ],
    );
  });

  tearDown(() {
    container.dispose();
  });

  group('ReportArtifactController & Providers Unit Tests', () {
    test(
      'Positive 1: executionReportsProvider fetches summaries and reportDetailProvider invalidates SDUI and row providers when status is ready',
      () async {
        var sduiCallCount = 0;
        var rowsCallCount = 0;

        when(
          () => mockDio.get<List<Object?>>(
            '/executions/$testExecutionId/reports',
          ),
        ).thenAnswer(
          (_) async => Response<List<Object?>>(
            requestOptions: RequestOptions(
              path: '/executions/$testExecutionId/reports',
            ),
            data: <Object?>[readySummaryJson],
            statusCode: 200,
          ),
        );

        when(
          () => mockDio.get<Map<String, Object?>>('/reports/$testReportId'),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(path: '/reports/$testReportId'),
            data: readyReportDetailJson,
            statusCode: 200,
          ),
        );

        when(
          () =>
              mockDio.get<Map<String, Object?>>('/reports/$testReportId/sdui'),
        ).thenAnswer((_) async {
          sduiCallCount++;
          return Response<Map<String, Object?>>(
            requestOptions: RequestOptions(path: '/reports/$testReportId/sdui'),
            data: <String, Object?>{
              'execution_id': testExecutionId,
              'workflow_id': testWorkflowId,
              'profile_id': testProfileId,
            },
            statusCode: 200,
          );
        });

        when(
          () => mockDio.get<List<Object?>>('/reports/$testReportId/rows'),
        ).thenAnswer((_) async {
          rowsCallCount++;
          return Response<List<Object?>>(
            requestOptions: RequestOptions(path: '/reports/$testReportId/rows'),
            data: <Object?>[
              <String, Object?>{
                'execution_id': testExecutionId,
                'report_id': testReportId,
                'metric_key': 'm_1',
                'metric_label': 'Strategic Alignment',
                'score': 4.5,
                'max_scale': 5.0,
                'weight': 1.0,
                'is_inverse_evidence': false,
              },
            ],
            statusCode: 200,
          );
        });

        final summaries = await container.read(
          executionReportsProvider(testExecutionId).future,
        );
        expect(summaries, hasLength(1));
        expect(summaries.first.id, equals(testReportId));
        expect(summaries.first.status, equals(ReportStatus.ready));

        // Keep active listeners on SDUI and Rows providers to verify invalidation when reportDetail is ready
        final sduiSub = container.listen(
          reportSduiProvider(testReportId),
          (_, _) {},
        );
        final rowsSub = container.listen(
          reportRowsProvider(testReportId),
          (_, _) {},
        );
        addTearDown(() {
          sduiSub.close();
          rowsSub.close();
        });

        final sduiData = await container.read(
          reportSduiProvider(testReportId).future,
        );
        final rowsData = await container.read(
          reportRowsProvider(testReportId).future,
        );
        expect(sduiData.executionId, equals(testExecutionId));
        expect(rowsData.single.metricKey, equals('m_1'));
        expect(sduiCallCount, equals(1));
        expect(rowsCallCount, equals(1));

        // Reading reportDetail with ready status invalidates reportSdui and reportRows
        final detail = await container.read(
          reportDetailProvider(testReportId).future,
        );
        expect(detail.id, equals(testReportId));
        expect(detail.status, equals(ReportStatus.ready));

        await container.read(reportSduiProvider(testReportId).future);
        await container.read(reportRowsProvider(testReportId).future);
        expect(sduiCallCount, equals(2));
        expect(rowsCallCount, equals(2));
      },
    );

    test(
      'Positive 2: ReportArtifactActions createReport, regenerateReport, and deleteReport mutate state cleanly and invalidate target providers',
      () async {
        var listFetchCount = 0;
        when(
          () => mockDio.get<List<Object?>>(
            '/executions/$testExecutionId/reports',
          ),
        ).thenAnswer((_) async {
          listFetchCount++;
          return Response<List<Object?>>(
            requestOptions: RequestOptions(
              path: '/executions/$testExecutionId/reports',
            ),
            data: <Object?>[readySummaryJson],
            statusCode: 200,
          );
        });

        when(
          () => mockDio.post<Map<String, Object?>>(
            '/executions/$testExecutionId/reports',
            data: any(named: 'data'),
          ),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(
              path: '/executions/$testExecutionId/reports',
            ),
            data: readySummaryJson,
            statusCode: 201,
          ),
        );

        when(
          () => mockDio.post<Map<String, Object?>>(
            '/reports/$testReportId/regenerate',
          ),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(
              path: '/reports/$testReportId/regenerate',
            ),
            data: <String, Object?>{
              ...readySummaryJson,
              'status': 'generating',
            },
            statusCode: 200,
          ),
        );

        when(() => mockDio.delete<void>('/reports/$testReportId')).thenAnswer(
          (_) async => Response<void>(
            requestOptions: RequestOptions(path: '/reports/$testReportId'),
            statusCode: 204,
          ),
        );

        final reportsSub = container.listen(
          executionReportsProvider(testExecutionId),
          (_, _) {},
        );
        addTearDown(reportsSub.close);

        await container.read(executionReportsProvider(testExecutionId).future);
        expect(listFetchCount, equals(1));

        final actions = container.read(reportArtifactActionsProvider.notifier);

        final created = await actions.createReport(
          executionId: testExecutionId,
          request: const CreateReportRequest(profileId: testProfileId),
        );
        expect(created?.id, equals(testReportId));
        expect(
          container.read(reportArtifactActionsProvider),
          equals(const AsyncValue<void>.data(null)),
        );

        await container.read(executionReportsProvider(testExecutionId).future);
        expect(listFetchCount, equals(2));

        final regenerated = await actions.regenerateReport(
          reportId: testReportId,
          executionId: testExecutionId,
        );
        expect(regenerated?.status, equals(ReportStatus.generating));
        expect(
          container.read(reportArtifactActionsProvider),
          equals(const AsyncValue<void>.data(null)),
        );

        await actions.deleteReport(
          reportId: testReportId,
          executionId: testExecutionId,
        );
        expect(
          container.read(reportArtifactActionsProvider),
          equals(const AsyncValue<void>.data(null)),
        );
      },
    );

    test(
      'Negative 1 (ISTQB BVA): fails fast with AppException on malformed 32-hex Opaque Stripe IDs (empty, 31-hex min-1, 33-hex max+1) and logs error',
      () async {
        const boundaryInvalidIds = <String>[
          '',
          'rep_0195f3a000007000800000000000000', // 31 hex chars (min-1)
          'rep_0195f3a00000700080000000000000012', // 33 hex chars (max+1)
        ];

        final actions = container.read(reportArtifactActionsProvider.notifier);

        for (final invalidId in boundaryInvalidIds) {
          final sub = container.listen(
            executionReportsProvider(invalidId),
            (_, _) {},
          );
          await expectLater(
            container.read(executionReportsProvider(invalidId).future),
            throwsA(
              isA<AppException>().having(
                (e) => e.errorCode,
                'errorCode',
                equals('VALIDATION_FAILED'),
              ),
            ),
          );
          sub.close();

          await expectLater(
            actions.createReport(
              executionId: invalidId,
              request: const CreateReportRequest(profileId: testProfileId),
            ),
            throwsA(isA<AppException>()),
          );
          expect(
            container.read(reportArtifactActionsProvider).hasError,
            isTrue,
          );

          await expectLater(
            actions.regenerateReport(
              reportId: invalidId,
              executionId: testExecutionId,
            ),
            throwsA(isA<AppException>()),
          );
          expect(
            container.read(reportArtifactActionsProvider).hasError,
            isTrue,
          );

          await expectLater(
            actions.deleteReport(
              reportId: invalidId,
              executionId: testExecutionId,
            ),
            throwsA(isA<AppException>()),
          );
          expect(
            container.read(reportArtifactActionsProvider).hasError,
            isTrue,
          );
        }

        verify(
          () => mockLogger.error('ReportArtifactActions', any(), any(), any()),
        ).called(boundaryInvalidIds.length * 3);
      },
    );

    test(
      'Negative 2: transitions ReportArtifactActions to AsyncError, logs to LoggerService, and rethrows when backend returns unrecognized JSON keys or HTTP failure',
      () async {
        when(
          () => mockDio.post<Map<String, Object?>>(
            '/executions/$testExecutionId/reports',
            data: any(named: 'data'),
          ),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(
              path: '/executions/$testExecutionId/reports',
            ),
            data: <String, Object?>{
              ...readySummaryJson,
              'unrecognized_extra_key': 'forbidden',
            },
            statusCode: 200,
          ),
        );

        final actions = container.read(reportArtifactActionsProvider.notifier);

        await expectLater(
          actions.createReport(
            executionId: testExecutionId,
            request: const CreateReportRequest(profileId: testProfileId),
          ),
          throwsA(isA<CheckedFromJsonException>()),
        );

        final stateAfterSchemaError = container.read(
          reportArtifactActionsProvider,
        );
        expect(stateAfterSchemaError.hasError, isTrue);
        expect(stateAfterSchemaError.error, isA<CheckedFromJsonException>());

        verify(
          () => mockLogger.error(
            'ReportArtifactActions',
            any(that: contains('CREATE_REPORT_FAILED')),
            any(),
            any(),
          ),
        ).called(1);
      },
    );
  });
}
