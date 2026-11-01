import 'dart:typed_data';
import 'package:client_app/core/api/reports_client.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/reports/models/report_artifact.dart';
import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:json_annotation/json_annotation.dart';
import 'package:mocktail/mocktail.dart';

class MockDio extends Mock implements Dio {}

class MockLoggerService extends Mock implements LoggerService {}

void main() {
  late ReportsClient client;
  late MockDio mockDio;
  late MockLoggerService mockLogger;

  setUp(() {
    mockDio = MockDio();
    mockLogger = MockLoggerService();
    when(
      () => mockDio.options,
    ).thenReturn(BaseOptions(baseUrl: 'https://api.test/api/v2///'));
    client = ReportsClient(mockDio, mockLogger);
  });

  group('ReportsClient Unit & ISTQB Boundary Tests', () {
    const testExecutionId = 'exe_0195f3a0000070008000000000000001';
    const testReportId = 'rep_0195f3a0000070008000000000000002';
    const testWorkflowId = 'wf_0195f3a0000070008000000000000003';
    const testProfileId = 'op_0195f3a0000070008000000000000004';
    const testRegistryId = 'reg_0195f3a0000070008000000000000005';

    final testSummaryJson = <String, Object?>{
      'id': testReportId,
      'execution_id': testExecutionId,
      'profile_id': testProfileId,
      'locale': 'fi',
      'title': 'Test Report',
      'status': 'ready',
      'created_at': '2026-09-21T12:00:00.000Z',
      'updated_at': '2026-09-21T12:00:00.000Z',
    };

    test(
      'Positive 1: createReport sends expected payload and returns ReportArtifactSummary',
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
            data: testSummaryJson,
            statusCode: 200,
          ),
        );

        const request = CreateReportRequest(
          profileId: testProfileId,
          locale: 'fi',
          forceResynthesis: false,
          customPrefaceMd: 'Custom preface',
          modelRegistryId: testRegistryId,
        );

        final result = await client.createReport(
          executionId: testExecutionId,
          request: request,
        );

        expect(result.id, equals(testReportId));
        expect(result.executionId, equals(testExecutionId));
        expect(result.profileId, equals(testProfileId));
        expect(result.status, equals(ReportStatus.ready));
        verify(
          () => mockDio.post<Map<String, Object?>>(
            '/executions/$testExecutionId/reports',
            data: request.toJson(),
          ),
        ).called(1);
      },
    );

    test(
      'Positive 2: listReports fetches reports and maps list of summaries',
      () async {
        when(
          () => mockDio.get<List<Object?>>(
            '/executions/$testExecutionId/reports',
          ),
        ).thenAnswer(
          (_) async => Response<List<Object?>>(
            requestOptions: RequestOptions(
              path: '/executions/$testExecutionId/reports',
            ),
            data: <Object?>[testSummaryJson],
            statusCode: 200,
          ),
        );

        final result = await client.listReports(testExecutionId);
        expect(result.length, equals(1));
        expect(result.first.id, equals(testReportId));
        verify(
          () => mockDio.get<List<Object?>>(
            '/executions/$testExecutionId/reports',
          ),
        ).called(1);
      },
    );

    test('Positive 3: getReport fetches report artifact detail', () async {
      final reportDetailJson = <String, Object?>{
        'id': testReportId,
        'execution_id': testExecutionId,
        'workflow_id': testWorkflowId,
        'profile_id': testProfileId,
        'locale': 'fi',
        'title': 'Test Report',
        'status': 'ready',
        'storage_paths': <String, Object?>{
          'pdf_path': '/files/test.pdf',
          'excel_path': '/files/test.xlsx',
          'csv_path': '/files/test.csv',
          'sdui_json_path': '/files/test.json',
        },
        'metadata': <String, Object?>{'duration_ms': 1234},
        'created_at': '2026-09-21T12:00:00.000Z',
        'updated_at': '2026-09-21T12:00:00.000Z',
      };

      when(
        () => mockDio.get<Map<String, Object?>>('/reports/$testReportId'),
      ).thenAnswer(
        (_) async => Response<Map<String, Object?>>(
          requestOptions: RequestOptions(path: '/reports/$testReportId'),
          data: reportDetailJson,
          statusCode: 200,
        ),
      );

      final result = await client.getReport(testReportId);
      expect(result.id, equals(testReportId));
      expect(result.title, equals('Test Report'));
      expect(result.status, equals(ReportStatus.ready));
      verify(
        () => mockDio.get<Map<String, Object?>>('/reports/$testReportId'),
      ).called(1);
    });

    test(
      'Positive 4: getReportSdui fetches report data dto via safeIsolateRun',
      () async {
        final sduiJson = <String, Object?>{
          'execution_id': testExecutionId,
          'workflow_id': testWorkflowId,
          'profile_id': testProfileId,
        };

        when(
          () =>
              mockDio.get<Map<String, Object?>>('/reports/$testReportId/sdui'),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(path: '/reports/$testReportId/sdui'),
            data: sduiJson,
            statusCode: 200,
          ),
        );

        final result = await client.getReportSdui(testReportId);
        expect(result.executionId, equals(testExecutionId));
        expect(result.profileId, equals(testProfileId));
        verify(
          () =>
              mockDio.get<Map<String, Object?>>('/reports/$testReportId/sdui'),
        ).called(1);
      },
    );

    test(
      'Positive 5: getReportRows fetches and maps list of ReportRowItem via safeIsolateRun',
      () async {
        final rowJson = <String, Object?>{
          'execution_id': testExecutionId,
          'report_id': testReportId,
          'metric_key': 'm_1',
          'metric_label': 'Metric 1',
          'score': 4.5,
          'max_scale': 5.0,
          'weight': 1.0,
          'is_inverse_evidence': false,
        };

        when(
          () => mockDio.get<List<Object?>>('/reports/$testReportId/rows'),
        ).thenAnswer(
          (_) async => Response<List<Object?>>(
            requestOptions: RequestOptions(path: '/reports/$testReportId/rows'),
            data: <Object?>[rowJson],
            statusCode: 200,
          ),
        );

        final result = await client.getReportRows(testReportId);
        expect(result.length, equals(1));
        expect(result.first.metricKey, equals('m_1'));
        expect(result.first.score, equals(4.5));
        verify(
          () => mockDio.get<List<Object?>>('/reports/$testReportId/rows'),
        ).called(1);
      },
    );

    test(
      'Positive 6: regenerateReport posts to regenerate endpoint and returns summary',
      () async {
        when(
          () => mockDio.post<Map<String, Object?>>(
            '/reports/$testReportId/regenerate',
          ),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(
              path: '/reports/$testReportId/regenerate',
            ),
            data: testSummaryJson,
            statusCode: 200,
          ),
        );

        final result = await client.regenerateReport(testReportId);
        expect(result.id, equals(testReportId));
        expect(result.status, equals(ReportStatus.ready));
        verify(
          () => mockDio.post<Map<String, Object?>>(
            '/reports/$testReportId/regenerate',
          ),
        ).called(1);
      },
    );

    test(
      'Positive 7: deleteReport sends DELETE request for reportId',
      () async {
        when(() => mockDio.delete<void>('/reports/$testReportId')).thenAnswer(
          (_) async => Response<void>(
            requestOptions: RequestOptions(path: '/reports/$testReportId'),
            statusCode: 204,
          ),
        );

        await client.deleteReport(testReportId);
        verify(() => mockDio.delete<void>('/reports/$testReportId')).called(1);
      },
    );

    test(
      'Positive 8: download binary methods return Uint8List bytes and URL builders normalize trailing slashes',
      () async {
        final bytes = <int>[1, 2, 3, 4, 5];
        when(
          () => mockDio.get<List<int>>(any(), options: any(named: 'options')),
        ).thenAnswer(
          (_) async => Response<List<int>>(
            requestOptions: RequestOptions(path: '/reports/$testReportId/pdf'),
            data: bytes,
            statusCode: 200,
          ),
        );

        final pdfBytes = await client.downloadPdf(testReportId);
        expect(pdfBytes, equals(Uint8List.fromList(bytes)));

        final excelBytes = await client.downloadExcel(testReportId);
        expect(excelBytes, equals(Uint8List.fromList(bytes)));

        final csvBytes = await client.downloadCsv(testReportId);
        expect(csvBytes, equals(Uint8List.fromList(bytes)));

        expect(
          client.getPdfDownloadUrl(testReportId),
          equals('https://api.test/api/v2/reports/$testReportId/pdf'),
        );
        expect(
          client.getExcelDownloadUrl(testReportId),
          equals('https://api.test/api/v2/reports/$testReportId/excel'),
        );
        expect(
          client.getCsvDownloadUrl(testReportId),
          equals('https://api.test/api/v2/reports/$testReportId/csv'),
        );
      },
    );

    test(
      'Negative Test 1 (BVA): fails fast with AppException before HTTP call on invalid 32-hex Opaque Stripe IDs (empty, 16-hex, 31-hex min-1, 33-hex max+1)',
      () async {
        const invalidIds = <String>[
          '',
          'rep_1234567890abcdef', // legacy 16-hex
          'rep_0195f3a000007000800000000000000', // 31 hex chars (min-1)
          'rep_0195f3a00000700080000000000000012', // 33 hex chars (max+1)
          'r_0195f3a0000070008000000000000001', // 1-char prefix (min-1)
          'report_0195f3a0000070008000000000000001', // 6-char prefix (max+1)
        ];

        for (final invalidId in invalidIds) {
          expect(
            () => client.createReport(
              executionId: invalidId,
              request: const CreateReportRequest(profileId: testProfileId),
            ),
            throwsA(
              isA<AppException>().having(
                (e) => e.errorCode,
                'errorCode',
                equals('VALIDATION_FAILED'),
              ),
            ),
          );
          expect(
            () => client.listReports(invalidId),
            throwsA(isA<AppException>()),
          );
          expect(
            () => client.getReport(invalidId),
            throwsA(isA<AppException>()),
          );
          expect(
            () => client.getReportSdui(invalidId),
            throwsA(isA<AppException>()),
          );
          expect(
            () => client.getReportRows(invalidId),
            throwsA(isA<AppException>()),
          );
          expect(
            () => client.regenerateReport(invalidId),
            throwsA(isA<AppException>()),
          );
          expect(
            () => client.deleteReport(invalidId),
            throwsA(isA<AppException>()),
          );
          expect(
            () => client.downloadPdf(invalidId),
            throwsA(isA<AppException>()),
          );
          expect(
            () => client.downloadExcel(invalidId),
            throwsA(isA<AppException>()),
          );
          expect(
            () => client.downloadCsv(invalidId),
            throwsA(isA<AppException>()),
          );
          expect(
            () => client.getPdfDownloadUrl(invalidId),
            throwsA(isA<AppException>()),
          );
          expect(
            () => client.getExcelDownloadUrl(invalidId),
            throwsA(isA<AppException>()),
          );
          expect(
            () => client.getCsvDownloadUrl(invalidId),
            throwsA(isA<AppException>()),
          );
        }

        // Also test invalid profileId and modelRegistryId in CreateReportRequest
        expect(
          () => client.createReport(
            executionId: testExecutionId,
            request: const CreateReportRequest(profileId: 'prf_invalid_16hex'),
          ),
          throwsA(isA<AppException>()),
        );
        expect(
          () => client.createReport(
            executionId: testExecutionId,
            request: const CreateReportRequest(
              profileId: testProfileId,
              modelRegistryId: 'reg_invalid_16hex',
            ),
          ),
          throwsA(isA<AppException>()),
        );

        verify(
          () => mockLogger.error('ReportsClient', any(), any(), any()),
        ).called(invalidIds.length * 13 + 2);
        verifyNever(() => mockDio.get<Map<String, Object?>>(any()));
        verifyNever(() => mockDio.get<List<Object?>>(any()));
        verifyNever(
          () => mockDio.post<Map<String, Object?>>(
            any(),
            data: any(named: 'data'),
          ),
        );
        verifyNever(() => mockDio.delete<void>(any()));
      },
    );

    test(
      'Negative Test 2: createReport propagates DioException on network/HTTP error',
      () async {
        when(
          () => mockDio.post<Map<String, Object?>>(
            '/executions/$testExecutionId/reports',
            data: any(named: 'data'),
          ),
        ).thenThrow(
          DioException(
            requestOptions: RequestOptions(
              path: '/executions/$testExecutionId/reports',
            ),
            response: Response<Map<String, Object?>>(
              requestOptions: RequestOptions(
                path: '/executions/$testExecutionId/reports',
              ),
              statusCode: 400,
            ),
            type: DioExceptionType.badResponse,
          ),
        );

        expect(
          () => client.createReport(
            executionId: testExecutionId,
            request: const CreateReportRequest(profileId: testProfileId),
          ),
          throwsA(isA<DioException>()),
        );
      },
    );

    test(
      'Negative Test 3: fails fast with CheckedFromJsonException or AppException on unrecognized keys, null payload, or non-Map list elements',
      () async {
        // 1. Unrecognized keys in createReport response
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
            data: <String, Object?>{'invalid': 'payload'},
            statusCode: 200,
          ),
        );

        expect(
          () => client.createReport(
            executionId: testExecutionId,
            request: const CreateReportRequest(profileId: testProfileId),
          ),
          throwsA(isA<CheckedFromJsonException>()),
        );

        // 2. Null payload in getReport
        when(
          () => mockDio.get<Map<String, Object?>>('/reports/$testReportId'),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(path: '/reports/$testReportId'),
            data: null,
            statusCode: 200,
          ),
        );

        expect(
          () => client.getReport(testReportId),
          throwsA(
            isA<AppException>().having(
              (e) => e.errorCode,
              'errorCode',
              equals('VALIDATION_FAILED'),
            ),
          ),
        );

        // 3. Non-map element in getReportRows list
        when(
          () => mockDio.get<List<Object?>>('/reports/$testReportId/rows'),
        ).thenAnswer(
          (_) async => Response<List<Object?>>(
            requestOptions: RequestOptions(path: '/reports/$testReportId/rows'),
            data: <Object?>['not_a_map'],
            statusCode: 200,
          ),
        );

        expect(
          () => client.getReportRows(testReportId),
          throwsA(
            isA<AppException>().having(
              (e) => e.errorCode,
              'errorCode',
              equals('VALIDATION_FAILED'),
            ),
          ),
        );

        // 4. Null binary payload in downloadPdf
        when(
          () => mockDio.get<List<int>>(
            '/reports/$testReportId/pdf',
            options: any(named: 'options'),
          ),
        ).thenAnswer(
          (_) async => Response<List<int>>(
            requestOptions: RequestOptions(path: '/reports/$testReportId/pdf'),
            data: null,
            statusCode: 200,
          ),
        );

        expect(
          () => client.downloadPdf(testReportId),
          throwsA(
            isA<AppException>().having(
              (e) => e.errorCode,
              'errorCode',
              equals('VALIDATION_FAILED'),
            ),
          ),
        );
      },
    );
  });
}
