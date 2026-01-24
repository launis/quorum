// ignore_for_file: argument_type_not_assignable
import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';

import 'package:dio/dio.dart';
import 'package:printing/printing.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'pdf_export_controller.g.dart';

@riverpod
class PdfExportController extends _$PdfExportController {
  final Dio _dio = Dio(); 
  CancelToken? _cancelToken;

  @override
  AsyncValue<double> build() {
    return const AsyncData(0.0);
  }

  Future<void> downloadPdf(String executionId) async {
    state = const AsyncLoading();
    _cancelToken = CancelToken();

    try {
      final downloadUrl = '/executions/$executionId/pdf/download';
      
      final response = await _dio.get(
        downloadUrl, 
        cancelToken: _cancelToken,
        options: Options(
          validateStatus: (status) => status != null && status < 500,
          responseType: ResponseType.bytes 
        ),
      );

      if (response.statusCode == 200) {
        await _saveFile(response.data, "report_$executionId");
        state = const AsyncData(1.0);
        return;
      }

      if (response.statusCode == 202) {
        await _listenToProgress(executionId);
        return;
      }

      throw Exception('Failed to download: ${response.statusCode}');

    } catch (e, st) {
      if (e is DioException && CancelToken.isCancel(e)) {
         state = const AsyncData(0.0);
      } else {
         state = AsyncError(e, st);
      }
    }
  }

  Future<void> _listenToProgress(String executionId) async {
    final progressUrl = '/executions/$executionId/pdf/progress';
    final sseDio = Dio();
    
    try {
      final response = await sseDio.get(
        progressUrl,
        options: Options(
          responseType: ResponseType.stream,
          headers: {'Accept': 'text/event-stream'}
        ),
        cancelToken: _cancelToken
      );

      final stream = response.data.stream;
      
      await for (final chunk in stream) {
         final String chunkStr = utf8.decode(chunk);
         final lines = chunkStr.split('\n');
         
         for (final line in lines) {
           if (line.startsWith('data: ')) {
             final jsonStr = line.substring(6);
             try {
                final data = jsonDecode(jsonStr);
                final p = (data['progress'] as num).toDouble();
                state = AsyncData(p);
                
                if (p >= 1.0) {
                   await _performFinalDownload(executionId);
                   return; 
                }
             } catch (_) {}
           }
         }
      }
    } catch (e) {
      if (!CancelToken.isCancel(e)) {
         state = AsyncError(e, StackTrace.current);
      }
    }
  }

  Future<void> _performFinalDownload(String executionId) async {
      final response = await _dio.get(
        '/executions/$executionId/pdf/download',
        options: Options(responseType: ResponseType.bytes),
      );
      if (response.statusCode == 200) {
         await _saveFile(response.data, "report_$executionId");
         state = const AsyncData(1.0);
      }
  }

  Future<void> _saveFile(dynamic data, String name) async {
     // Ensure safe casting
     final list = (data as List<dynamic>).cast<int>();
     final bytes = Uint8List.fromList(list);
     
     await Printing.sharePdf(
       bytes: bytes,
       filename: '$name.pdf'
     );
  }

  Future<void> cancelDownload(String executionId) async {
    _cancelToken?.cancel();
    _cancelToken = null;
    try {
      await _dio.delete('/executions/$executionId/pdf/cancel');
    } catch (_) {}
    state = const AsyncData(0.0);
  }
}
