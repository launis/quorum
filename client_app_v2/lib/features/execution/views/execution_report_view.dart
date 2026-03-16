import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/features/execution/controllers/report_controller.dart';
import 'package:client_app/features/sdui/widgets/sdui_renderer.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/network/api_client.dart';
import 'package:dio/dio.dart';
import 'package:file_saver/file_saver.dart';
import 'dart:typed_data';

/// Render the execution report leveraging the Server-Driven UI (SDUI) framework.
class ExecutionReportView extends ConsumerStatefulWidget {
  final String executionId;

  const ExecutionReportView({super.key, required this.executionId});

  @override
  ConsumerState<ExecutionReportView> createState() =>
      _ExecutionReportViewState();
}

class _ExecutionReportViewState extends ConsumerState<ExecutionReportView> {
  bool _isDownloading = false;

  void _downloadPdf() async {
    setState(() {
      _isDownloading = true;
    });

    try {
      final dio = ref.read(apiClientProvider);
      final response = await dio.get<List<int>>(
        '/execution/executions/${widget.executionId}/render',
        queryParameters: {'format': 'pdf'},
        options: Options(responseType: ResponseType.bytes),
      );

      final bytes = Uint8List.fromList(response.data!);
      await FileSaver.instance.saveAs(
        name: 'Report_${widget.executionId}',
        bytes: bytes,
        ext: 'pdf',
        mimeType: MimeType.pdf,
      );

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(AppLocalizations.of(context)!.downloadSuccess),
          ),
        );
      }
    } catch (e, st) {
      ref
          .read(loggerServiceProvider)
          .error('ReportView', 'Failed to download PDF', e, st);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(AppLocalizations.of(context)!.errorUnknown),
            backgroundColor: Theme.of(context).colorScheme.error,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isDownloading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    // Determine target locale safely via Localizations or explicit parameter
    final locale =
        Localizations.localeOf(context).languageCode == 'fi' ? 'fi' : 'en';

    final reportAsync = ref.watch(
      reportControllerProvider(widget.executionId, lang: locale),
    );

    return Scaffold(
      backgroundColor: const Color(0xFFF8F9FA),
      appBar: AppBar(
        title: Text(
          '${AppLocalizations.of(context)!.report}: ${widget.executionId}',
          style: const TextStyle(fontSize: 16),
        ),
        centerTitle: true,
        actions: [
          _isDownloading
              ? const Padding(
                padding: EdgeInsets.all(16.0),
                child: SizedBox(
                  width: 20,
                  height: 20,
                  child: CircularProgressIndicator(strokeWidth: 2),
                ),
              )
              : IconButton(
                icon: const Icon(Icons.picture_as_pdf),
                tooltip: AppLocalizations.of(context)!.downloadReportTooltip,
                onPressed: _downloadPdf,
              ),
        ],
      ),
      body: reportAsync.when(
        data: (payload) {
          return Center(child: SduiRenderer(payload: payload));
        },
        error: (err, stack) {
          final logger = ref.read(loggerServiceProvider);
          logger.error(
            'SDUI Builder',
            'VALIDATION_FAILED: Failed to parse or fetch payload',
            err,
            stack,
          );
          return ErrorView(
            error: err,
            stackTrace: stack,
            onRetry:
                () => ref.invalidate(
                  reportControllerProvider(widget.executionId, lang: locale),
                ),
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
      ),
    );
  }
}
