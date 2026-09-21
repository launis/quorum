import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:client_app/core/api/execution_client.dart';
import 'package:client_app/features/execution/models/report_data_v2_dto.dart';

part 'report_controller.g.dart';

@riverpod
class RenderStatus extends _$RenderStatus {
  @override
  String? build() => null;

  void updateStatus(String? msg) {
    if (state != msg) state = msg;
  }
}

/// Fetch and parse the dynamically assembled SDUI render blueprint for an execution.
@riverpod
class ReportController extends _$ReportController {
  @override
  Future<ReportDataDto> build(
    String executionId, {
    String lang = 'fi',
    String variant = 'default',
  }) async {
    final client = ref.watch(executionClientProvider);
    return await client.renderExecution(
      executionId,
      lang: lang,
      variant: variant,
      onProgress: (msg) {
        Future.microtask(() {
          ref.read(renderStatusProvider.notifier).updateStatus(msg);
        });
      },
    );
  }
}
