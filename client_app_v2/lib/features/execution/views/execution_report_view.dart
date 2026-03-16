import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/features/execution/controllers/report_controller.dart';
import 'package:client_app/features/sdui/widgets/sdui_renderer.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/core/logging/logger_service.dart';

/// Render the execution report leveraging the Server-Driven UI (SDUI) framework.
class ExecutionReportView extends ConsumerWidget {
  final String executionId;

  const ExecutionReportView({
    super.key,
    required this.executionId,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Determine target locale safely via Localizations or explicit parameter
    final locale = Localizations.localeOf(context).languageCode == 'fi' ? 'fi' : 'en';

    final reportAsync = ref.watch(reportControllerProvider(executionId, lang: locale));

    return Scaffold(
      backgroundColor: const Color(0xFFF8F9FA),
      appBar: AppBar(
        title: Text('${AppLocalizations.of(context)!.report}: $executionId', style: const TextStyle(fontSize: 16)),
        centerTitle: true,
      ),
      body: reportAsync.when(
        data: (payload) {
          return Center(
            child: SduiRenderer(payload: payload),
          );
        },
        error: (err, stack) {
          final logger = ref.read(loggerServiceProvider);
          logger.error('SDUI Builder', 'VALIDATION_FAILED: Failed to parse or fetch payload', err, stack);
          return ErrorView(
            error: err,
            stackTrace: stack,
            onRetry: () => ref.invalidate(reportControllerProvider(executionId, lang: locale)),
          );
        },
        loading: () => const Center(
          child: CircularProgressIndicator(),
        ),
      ),
    );
  }
}

