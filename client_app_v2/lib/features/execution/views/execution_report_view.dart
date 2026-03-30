import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/features/execution/controllers/report_controller.dart';
import 'package:client_app/features/execution/views/widgets/report_renderer_widget.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/network/api_client.dart';
import 'package:dio/dio.dart';
import 'package:file_saver/file_saver.dart';
import 'dart:typed_data';
import 'package:client_app/router/router.dart';
import 'package:client_app/features/execution/models/report_data_dto.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/error/app_error_ext.dart';

/// Centralized settings for the Execution Report View
class ReportSettings {
  const ReportSettings._();

  /// Global timeout for the PDF and Context Download streams
  static const Duration downloadTimeout = Duration(seconds: 15);
}

/// Render the execution report leveraging the Server-Driven UI (SDUI) framework.
class ExecutionReportView extends ConsumerStatefulWidget {
  final String executionId;
  final String variant;

  const ExecutionReportView({
    super.key,
    required this.executionId,
    this.variant = 'default',
  });

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
        queryParameters: {'format': 'pdf', 'profile_id': widget.variant},
        options: Options(responseType: ResponseType.bytes),
      );

      final bytes = Uint8List.fromList(response.data!);
      await FileSaver.instance
          .saveAs(
            name: 'Report_${widget.executionId}',
            bytes: bytes,
            fileExtension: 'pdf',
            mimeType: MimeType.pdf,
          )
          .timeout(
            ReportSettings.downloadTimeout,
            onTimeout: () => throw AppException.timeout(
              AppLocalizations.of(context)!.errSaveTimeout,
            ),
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
        final l10n = AppLocalizations.of(context)!;
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(AppExceptionX.extractLocalizedHint(e, l10n)),
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
      await FileSaver.instance
          .saveAs(
            name: 'FrozenContext_${widget.executionId}',
            bytes: bytes,
            fileExtension: 'json',
            mimeType: MimeType.json,
          )
          .timeout(
            ReportSettings.downloadTimeout,
            onTimeout: () => throw AppException.timeout(
              AppLocalizations.of(context)!.errSaveTimeout,
            ),
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
        final l10n = AppLocalizations.of(context)!;
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(AppExceptionX.extractLocalizedHint(e, l10n)),
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
    final locale = Localizations.localeOf(context).languageCode == 'fi'
        ? 'fi'
        : 'en';

    final reportAsync = ref.watch(
      reportControllerProvider(
        widget.executionId,
        lang: locale,
        variant: widget.variant,
      ),
    );

    return Scaffold(
      backgroundColor: const Color(0xFFF8F9FA),
      appBar: AppBar(
        title: _buildAppBarTitle(context, reportAsync.value, locale),
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
          // Zero-math, logic-free static controller injection.
          return ReportRendererWidget(payload: payload);
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
            onRetry: () => ref.invalidate(
              reportControllerProvider(
                widget.executionId,
                lang: locale,
                variant: widget.variant,
              ),
            ),
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
      ),
    );
  }

  Widget _buildAppBarTitle(
    BuildContext context,
    ReportDataDTO? payload,
    String locale,
  ) {
    if (payload == null || payload.availableProfiles.length <= 1) {
      return Text(
        '${AppLocalizations.of(context)!.report}: ${widget.executionId}${widget.variant != 'default' ? ' (${widget.variant})' : ''}',
        style: const TextStyle(fontSize: 16),
      );
    }

    // Safely fallback to first available if variant not found
    final safeVariant = payload.availableProfiles.containsKey(widget.variant)
        ? widget.variant
        : payload.availableProfiles.keys.first;

    return DropdownButtonHideUnderline(
      child: DropdownButton<String>(
        value: safeVariant,
        icon: Icon(
          Icons.arrow_drop_down,
          color: Theme.of(context).colorScheme.onSurface,
        ),
        style: TextStyle(
          fontSize: 16,
          fontWeight: FontWeight.bold,
          color: Theme.of(context).colorScheme.onSurface,
        ),
        onChanged: (String? newValue) {
          if (newValue != null && newValue != widget.variant) {
            ExecutionReportRoute(
              executionId: widget.executionId,
              variant: newValue,
            ).go(context);
          }
        },
        items: payload.availableProfiles.entries.map((entry) {
          final translatedName = entry.value.get(locale);
          final profileName = translatedName.isEmpty
              ? entry.key
              : translatedName;
          return DropdownMenuItem<String>(
            value: entry.key,
            child: Text(
              '${AppLocalizations.of(context)!.report}: $profileName',
            ),
          );
        }).toList(),
      ),
    );
  }
}
