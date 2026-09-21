import 'dart:typed_data';
import 'package:client_app/core/api/reports_client.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

class MockDio extends Mock implements Dio {}

void main() {
  late ReportsClient client;
  late MockDio mockDio;

  setUp(() {
    mockDio = MockDio();
    when(() => mockDio.options).thenReturn(BaseOptions(baseUrl: 'https://api.test/api/v2'));
    client = ReportsClient(mockDio);
  });

  group('ReportsClient', () {
    const testExecutionId = 'exe_1234567890abcdef';
    const testReportId = 'rep_1234567890abcdef';

    final testSummaryJson = {
      'id': testReportId,
      'execution_id': testExecutionId,
      'profile_id': 'prf_default',
      'locale': 'fi',
      'title': 'Test Report',
      'status': 'ready',
      'created_at': '2026-09-21T12:00:00.000Z',
      'updated_at': '2026-09-21T12:00:00.000Z',
    };

    test('createReport sends expected payload and returns ReportArtifactSummary', () async {
      when(
        () => mockDio.post(
          '/executions/$testExecutionId/reports',
          data: {
            'profile_id': 'prf_default',
            'locale': 'fi',
            'custom_preface_md': 'Custom preface',
            'model_registry_id': 'reg_123',
          },
        ),
      ).thenAnswer(
        (_) async => Response(
          requestOptions: RequestOptions(path: '/executions/$testExecutionId/reports'),
          data: testSummaryJson,
          statusCode: 200,
        ),
      );

      final result = await client.createReport(
        executionId: testExecutionId,
        profileId: 'prf_default',
        locale: 'fi',
        customPrefaceMd: 'Custom preface',
        modelRegistryId: 'reg_123',
      );

      expect(result.id, equals(testReportId));
      expect(result.executionId, equals(testExecutionId));
      expect(result.status, equals(ReportStatus.ready));
      verify(
        () => mockDio.post(
          '/executions/$testExecutionId/reports',
          data: {
            'profile_id': 'prf_default',
            'locale': 'fi',
            'custom_preface_md': 'Custom preface',
            'model_registry_id': 'reg_123',
          },
        ),
      ).called(1);
    });

    test('Negative Test 1: createReport propagates DioException on network/HTTP error', () async {
      when(
        () => mockDio.post(
          '/executions/$testExecutionId/reports',
          data: any(named: 'data'),
        ),
      ).thenThrow(
        DioException(
          requestOptions: RequestOptions(path: '/executions/$testExecutionId/reports'),
          response: Response(
            requestOptions: RequestOptions(path: '/executions/$testExecutionId/reports'),
            statusCode: 400,
          ),
          type: DioExceptionType.badResponse,
        ),
      );

      expect(
        () => client.createReport(
          executionId: testExecutionId,
          profileId: 'prf_default',
        ),
        throwsA(isA<DioException>()),
      );
    });

    test('Negative Test 2: createReport throws when server returns malformed JSON missing required keys', () async {
      when(
        () => mockDio.post(
          '/executions/$testExecutionId/reports',
          data: any(named: 'data'),
        ),
      ).thenAnswer(
        (_) async => Response(
          requestOptions: RequestOptions(path: '/executions/$testExecutionId/reports'),
          data: {'invalid': 'payload'},
          statusCode: 200,
        ),
      );

      expect(
        () => client.createReport(
          executionId: testExecutionId,
          profileId: 'prf_default',
        ),
        throwsA(anything),
      );
    });

    test('listReports fetches reports and maps list of summaries', () async {
      when(() => mockDio.get('/executions/$testExecutionId/reports')).thenAnswer(
        (_) async => Response(
          requestOptions: RequestOptions(path: '/executions/$testExecutionId/reports'),
          data: [testSummaryJson],
          statusCode: 200,
        ),
      );

      final result = await client.listReports(testExecutionId);
      expect(result.length, equals(1));
      expect(result.first.id, equals(testReportId));
      verify(() => mockDio.get('/executions/$testExecutionId/reports')).called(1);
    });

    test('getReport fetches report artifact detail', () async {
      final reportDetailJson = {
        'id': testReportId,
        'execution_id': testExecutionId,
        'workflow_id': 'wf_default',
        'profile_id': 'prf_default',
        'locale': 'fi',
        'title': 'Test Report',
        'status': 'ready',
        'storage_paths': {
          'pdf_path': '/files/test.pdf',
          'excel_path': '/files/test.xlsx',
          'csv_path': '/files/test.csv',
          'sdui_json_path': '/files/test.json',
        },
        'metadata': {
          'duration_ms': 1234,
        },
        'created_at': '2026-09-21T12:00:00.000Z',
        'updated_at': '2026-09-21T12:00:00.000Z',
      };

      when(() => mockDio.get('/reports/$testReportId')).thenAnswer(
        (_) async => Response(
          requestOptions: RequestOptions(path: '/reports/$testReportId'),
          data: reportDetailJson,
          statusCode: 200,
        ),
      );

      final result = await client.getReport(testReportId);
      expect(result.id, equals(testReportId));
      expect(result.title, equals('Test Report'));
      expect(result.status, equals(ReportStatus.ready));
      verify(() => mockDio.get('/reports/$testReportId')).called(1);
    });

    test('getReportSdui fetches report data dto', () async {
      final sduiJson = {
        'execution_id': testExecutionId,
        'workflow_id': 'wf_123',
        'profile_id': 'prf_default',
      };

      when(() => mockDio.get('/reports/$testReportId/sdui')).thenAnswer(
        (_) async => Response(
          requestOptions: RequestOptions(path: '/reports/$testReportId/sdui'),
          data: sduiJson,
          statusCode: 200,
        ),
      );

      final result = await client.getReportSdui(testReportId);
      expect(result.executionId, equals(testExecutionId));
      expect(result.profileId, equals('prf_default'));
      verify(() => mockDio.get('/reports/$testReportId/sdui')).called(1);
    });

    test('download binary methods return Uint8List bytes', () async {
      final bytes = [1, 2, 3, 4, 5];
      when(
        () => mockDio.get<List<int>>(
          any(),
          options: any(named: 'options'),
        ),
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
    });

    test('URL builders construct normalized download links', () {
      expect(client.getPdfDownloadUrl(testReportId), equals('https://api.test/api/v2/reports/$testReportId/pdf'));
      expect(client.getExcelDownloadUrl(testReportId), equals('https://api.test/api/v2/reports/$testReportId/excel'));
      expect(client.getCsvDownloadUrl(testReportId), equals('https://api.test/api/v2/reports/$testReportId/csv'));
    });
  });
}
