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
  bool _isDownloadingPdf = false;
  bool _isDownloadingContext = false;

  void _downloadPdf() async {
    setState(() {
      _isDownloadingPdf = true;
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
        fileExtension: 'pdf',
        mimeType: MimeType.pdf,
      ).timeout(
        const Duration(seconds: 15),
        onTimeout: () => throw Exception('Tiedoston tallennusikkuna ei vastannut (Timeout). Tarkista, jäikö ikkuna piiloon tai onko vanha PDF-tiedosto auki toisessa ohjelmassa.'),
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
        final errorMsg = e.toString().contains('Timeout') 
            ? e.toString().replaceAll('Exception: ', '')
            : AppLocalizations.of(context)!.errorUnknown;
            
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(errorMsg),
            backgroundColor: Theme.of(context).colorScheme.error,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isDownloadingPdf = false;
        });
      }
    }
  }

  void _downloadFrozenContext() async {
    setState(() {
      _isDownloadingContext = true;
    });

    try {
      final dio = ref.read(apiClientProvider);
      final response = await dio.get<List<int>>(
        '/execution/executions/${widget.executionId}/frozen_context',
        options: Options(responseType: ResponseType.bytes),
      );

      final bytes = Uint8List.fromList(response.data!);
      await FileSaver.instance.saveAs(
        name: 'FrozenContext_${widget.executionId}',
        bytes: bytes,
        fileExtension: 'json',
        mimeType: MimeType.json,
      ).timeout(
        const Duration(seconds: 15),
        onTimeout: () => throw Exception('Tiedoston tallennusikkuna ei vastannut (Timeout). Tarkista, jäikö ikkuna piiloon tai onko vanha JSON-tiedosto auki toisessa ohjelmassa.'),
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
          .error('ReportView', 'Failed to download Frozen Context', e, st);
      if (mounted) {
        final errorMsg = e.toString().contains('Timeout') 
            ? e.toString().replaceAll('Exception: ', '')
            : AppLocalizations.of(context)!.errorUnknown;
            
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(errorMsg),
            backgroundColor: Theme.of(context).colorScheme.error,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isDownloadingContext = false;
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
          _isDownloadingContext
              ? const Padding(
                padding: EdgeInsets.all(16.0),
                child: SizedBox(
                  width: 20,
                  height: 20,
                  child: CircularProgressIndicator(strokeWidth: 2),
                ),
              )
              : IconButton(
                icon: const Icon(Icons.policy),
                tooltip: 'Lataa Frozen Context',
                onPressed: _downloadFrozenContext,
              ),
          _isDownloadingPdf
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
