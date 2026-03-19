import 'dart:isolate';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:client_app/core/api/execution_client.dart';
import 'package:client_app/features/sdui/models/sdui_render_payload.dart';

part 'report_controller.g.dart';

/// Fetch and parse the dynamically assembled SDUI render blueprint for an execution.
///
/// NOTE (Architecture): Parsing is offloaded to a background isolate utilizing `Isolate.run`
/// to prevent the 60fps UI thread from stuttering when hydrating large blueprint graphs.
@riverpod
class ReportController extends _$ReportController {
  @override
  Future<SduiRenderPayload> build(
    String executionId, {
    String lang = 'fi',
    String variant = 'default',
  }) async {
    final client = ref.watch(executionClientProvider);
    final rawData = await client.renderExecution(
      executionId,
      lang: lang,
      variant: variant,
    );
    return await Isolate.run(() => SduiRenderPayload.fromJson(rawData));
  }
}
