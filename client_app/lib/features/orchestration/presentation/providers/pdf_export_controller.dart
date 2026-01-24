// ignore_for_file: argument_type_not_assignable
import 'dart:async';
import 'dart:typed_data';

import 'package:client_app/core/network/sse_client.dart';
import 'package:dio/dio.dart';
import 'package:printing/printing.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'pdf_export_controller.g.dart';

@riverpod
class PdfExportController extends _$PdfExportController {
  @visibleForTesting
  Dio dio = Dio();

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

      final response = await dio.get(
        downloadUrl,
        cancelToken: _cancelToken,
        options: Options(
          validateStatus: (status) => status != null && status < 500,
          responseType: ResponseType.bytes,
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

    try {
      final stream = SseClient.connect<double>(
        url: progressUrl,
        parser: (json) => (json['progress'] as num).toDouble(),
        cancelToken: _cancelToken,
        dio: dio,
      );

      await for (final progress in stream) {
        state = AsyncData(progress);
        if (progress >= 1.0) {
          await _performFinalDownload(executionId);
          return;
        }
      }

      // If stream closes and we haven't returned (e.g. didn't hit 1.0 but closed),
      // we might want to check if it's done or just failed silently?
      // Requirement says: "When stream closes (or progress == 1.0), verify file availability"
      // So we generally proceed to final download check.
      if (state.valueOrNull != 1.0) {
        await _performFinalDownload(executionId);
      }
    } catch (e, st) {
      if (e is DioException && CancelToken.isCancel(e)) {
        state = const AsyncData(0.0); // Reset on cancel
      } else {
        state = AsyncError(e, st);
      }
    }
  }

  Future<void> _performFinalDownload(String executionId) async {
    // Ensure we don't redownload if we are just verifying availability,
    // but typically we need the bytes.
    // 200 OK via GET /executions/$id/pdf/download
    final response = await dio.get(
      '/executions/$executionId/pdf/download',
      options: Options(responseType: ResponseType.bytes),
      cancelToken: _cancelToken,
    );

    if (response.statusCode == 200) {
      await _saveFile(response.data, "report_$executionId");
      state = const AsyncData(1.0);
    } else {
      throw Exception(
        'Final download failed with status: ${response.statusCode}',
      );
    }
  }

  Future<void> _saveFile(dynamic data, String name) async {
    final list = (data as List<dynamic>).cast<int>();
    final bytes = Uint8List.fromList(list);

    await Printing.sharePdf(bytes: bytes, filename: '$name.pdf');
  }

  Future<void> cancelDownload(String executionId) async {
    _cancelToken?.cancel();
    _cancelToken = null;
    try {
      await dio.delete('/executions/$executionId/pdf/cancel');
    } catch (_) {}
    state = const AsyncData(0.0);
  }
}
