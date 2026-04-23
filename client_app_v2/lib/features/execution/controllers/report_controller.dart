import 'dart:isolate';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:client_app/core/api/execution_client.dart';
import 'package:client_app/features/execution/models/report_data_dto.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/core/error/app_exception.dart';

part 'report_controller.g.dart';

/// Fetch and parse the dynamically assembled SDUI render blueprint for an execution.
///
/// NOTE (Architecture): Parsing is offloaded to a background isolate utilizing `Isolate.run`
/// to prevent the 60fps UI thread from stuttering when hydrating large blueprint graphs.
@riverpod
class ReportController extends _$ReportController {
  @override
  Future<ReportDataDTO> build(
    String executionId, {
    String lang = 'fi',
    String variant = 'default',
  }) async {
    final client = ref.watch(executionClientProvider);

    // Epic 14 M4: Omni-Channel Polling for 202 Accepted Background Tasks
    int attempts = 0;
    final maxAttempts = SystemConcurrency.pollingMaxAttempts.value;

    while (true) {
      final rawData = await client.renderExecution(
        executionId,
        lang: lang,
        variant: variant,
      );

      if (rawData.containsKey('status') && rawData['status'] == 'pending') {
        attempts++;
        if (attempts >= maxAttempts) {
          throw AppException.network(
            'Timeout waiting for synthesis to complete.',
          ).copyWith(extensions: const {'error_code': 'UPSTREAM_TIMEOUT'});
        }
        // Poll every 2 seconds while the Arq Worker generates profile syntheses
        await Future.delayed(const Duration(seconds: 2));
        continue;
      }

      return await Isolate.run(() => ReportDataDTO.fromJson(rawData));
    }
  }
}
