import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';

import 'package:client_app/features/orchestration/presentation/providers/pdf_export_controller.dart';
import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';
import 'package:riverpod/riverpod.dart';

@GenerateMocks([Dio])
import 'pdf_export_controller_test.mocks.dart';

void main() {
  late MockDio mockDio;

  setUp(() {
    mockDio = MockDio();

    // Mock Printing channel to avoid MissingPluginException
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMethodCallHandler(const MethodChannel('net.nfet.printing'), (
          call,
        ) async {
          return 1;
        });
  });

  tearDown(() {
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMethodCallHandler(
          const MethodChannel('net.nfet.printing'),
          null,
        );
  });

  test('downloadPdf handles 200 OK immediately', () async {
    final container = ProviderContainer();
    final controller = container.read(pdfExportControllerProvider.notifier);
    controller.dio = mockDio;

    when(
      mockDio.get(
        any,
        cancelToken: any,
        options: any,
      ),
    ).thenAnswer(
      (_) async => Response(
        requestOptions: RequestOptions(path: ''),
        statusCode: 200,
        data: [1, 2, 3], // Bytes
      ),
    );

    await controller.downloadPdf('123');

    expect(container.read(pdfExportControllerProvider), const AsyncData(1.0));
  });

  test('downloadPdf handles 202 Accepted and streams progress via SseClient', () async {
    final container = ProviderContainer();
    final controller = container.read(pdfExportControllerProvider.notifier);
    controller.dio = mockDio;

    final streamController = StreamController<Uint8List>();
    final responseBody = ResponseBody(streamController.stream, 200);

    var downloadCallCount = 0;

    // Mock Download Endpoint
    when(
      mockDio.get(
        '/executions/123/pdf/download',
        queryParameters: any,
        cancelToken: any,
        options: any,
      ),
    ).thenAnswer((invocation) async {
      downloadCallCount++;
      if (downloadCallCount == 1) {
           return Response(
            requestOptions: RequestOptions(path: '/executions/123/pdf/download'),
            statusCode: 202,
           );
      } else {
           return Response(
            requestOptions: RequestOptions(path: '/executions/123/pdf/download'),
            statusCode: 200,
            data: [1, 2, 3],
           );
      }
    });

    // Mock Progress Endpoint
    when(
      mockDio.get<ResponseBody>(
        '/executions/123/pdf/progress',
        queryParameters: any,
        cancelToken: any,
        options: any,
      ),
    ).thenAnswer((invocation) async {
         return Response<ResponseBody>(
          requestOptions: RequestOptions(path: '/executions/123/pdf/progress'),
          data: responseBody,
          statusCode: 200,
         );
    });

    // Start the process
    final future = controller.downloadPdf('123');

    // Simulate SSE progress
    // Wait a tick for connection
    await Future.delayed(Duration.zero);

    streamController.add(
      Uint8List.fromList(utf8.encode('data: {"progress": 0.5}\n\n')),
    );
    await Future.delayed(const Duration(milliseconds: 10));

    // Check intermediate state
    expect(container.read(pdfExportControllerProvider).value, 0.5);

    // Finish
    streamController.add(
      Uint8List.fromList(utf8.encode('data: {"progress": 1.0}\n\n')),
    );
    await streamController.close();

    await future;

    expect(container.read(pdfExportControllerProvider), const AsyncData(1.0));
  });
}
