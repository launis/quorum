import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/features/execution/controllers/report_controller.dart';
import 'package:client_app/features/execution/views/widgets/report_renderer_v2_widget.dart';
import 'package:client_app/core/theme/app_spacing.dart';

import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/network/api_client.dart';
import 'package:dio/dio.dart';
import 'package:file_saver/file_saver.dart';
import 'dart:typed_data';
import 'package:client_app/features/execution/models/report_data_v2_dto.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/error/app_error_ext.dart';
import 'dart:convert';

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
  bool _isDownloadingExcel = false;

  void _downloadExcel() async {
    setState(() {
      _isDownloadingExcel = true;
    });

    try {
      final dio = ref.read(apiClientProvider);
      final response = await dio.get<List<int>>(
        '/execution/executions/${widget.executionId}/export',
        options: Options(responseType: ResponseType.bytes),
      );

      final bytes = Uint8List.fromList(response.data!);
      await FileSaver.instance
          .saveAs(
            name: 'Execution_Export_${widget.executionId}',
            bytes: bytes,
            fileExtension: 'xlsx',
            mimeType: MimeType.microsoftExcel,
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
          .error('ReportView', 'Failed to download Excel export', e, st);

      if (mounted) {
        final l10n = AppLocalizations.of(context)!;
        String errorMessage = AppExceptionX.extractLocalizedHint(e, l10n);

        if (e is DioException &&
            e.response?.data != null &&
            e.response!.data is List<int>) {
          try {
            final decodedString = utf8.decode(e.response!.data as List<int>);
            final jsonMap = jsonDecode(decodedString) as Map<String, dynamic>;
            if (jsonMap.containsKey('detail')) {
              errorMessage = jsonMap['detail'] as String;
            }
          } catch (_) {
            // Ignore decoding errors and fallback to default message
          }
        }

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(errorMessage),
            backgroundColor: Theme.of(context).colorScheme.error,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isDownloadingExcel = false;
        });
      }
    }
  }

  void _downloadPdf() async {
    setState(() {
      _isDownloadingPdf = true;
    });

    try {
      final targetDate = DateTime.now();

      final localTimeStr =
          '${targetDate.year}-${targetDate.month.toString().padLeft(2, '0')}-${targetDate.day.toString().padLeft(2, '0')} ${targetDate.hour.toString().padLeft(2, '0')}:${targetDate.minute.toString().padLeft(2, '0')}';

      final queryParams = {
        'format': 'pdf',
        'profile_id': widget.variant,
        'local_time_str': localTimeStr,
      };

      final dio = ref.read(apiClientProvider);
      final response = await dio.get<List<int>>(
        '/execution/executions/${widget.executionId}/render',
        queryParameters: queryParams,
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
      backgroundColor: Theme.of(context).colorScheme.surface,
      appBar: AppBar(
        title: _buildAppBarTitle(context, reportAsync.value, locale),
        centerTitle: true,
        actions: [
          _isDownloadingContext
              ? const Padding(
                  padding: AppSpacing.p16,
                  child: SizedBox(
                    width: AppSpacing.s24,
                    height: AppSpacing.s24,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  ),
                )
              : IconButton(
                  icon: const Icon(Icons.policy),
                  tooltip: AppLocalizations.of(
                    context,
                  )!.downloadFrozenContextTooltip,
                  onPressed: _downloadFrozenContext,
                ),
          _isDownloadingPdf
              ? const Padding(
                  padding: AppSpacing.p16,
                  child: SizedBox(
                    width: AppSpacing.s24,
                    height: AppSpacing.s24,
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
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _isDownloadingExcel ? null : _downloadExcel,
        icon: _isDownloadingExcel
            ? SizedBox(
                width: AppSpacing.s24,
                height: AppSpacing.s24,
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  color: Theme.of(context).colorScheme.onPrimary,
                ),
              )
            : const Icon(Icons.table_chart),
        label: Text(AppLocalizations.of(context)!.downloadExcelBtn),
      ),
      body: switch (reportAsync) {
        AsyncData(:final value) => SingleChildScrollView(
          child: Column(
            children: [
              ReportRendererV2Widget(
                payload: value,
                executionId: widget.executionId,
              ),
            ],
          ),
        ),
        AsyncError(:final error, :final stackTrace) => Builder(
          builder: (ctx) {
            final logger = ref.read(loggerServiceProvider);
            logger.error(
              'SDUI Builder',
              'VALIDATION_FAILED: Failed to parse or fetch payload',
              error,
              stackTrace,
            );
            return ErrorView(
              error: error,
              stackTrace: stackTrace,
              onRetry: () => ref.invalidate(
                reportControllerProvider(
                  widget.executionId,
                  lang: locale,
                  variant: widget.variant,
                ),
              ),
            );
          },
        ),
        _ => Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const CircularProgressIndicator(),
              AppSpacing.h16,
              Consumer(
                builder: (context, ref, child) {
                  final statusMsg = ref.watch(renderStatusProvider);
                  return Text(
                    statusMsg ?? '',
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: Theme.of(context).colorScheme.onSurfaceVariant,
                    ),
                  );
                },
              ),
            ],
          ),
        ),
      },
    );
  }

  Widget _buildAppBarTitle(
    BuildContext context,
    ReportDataDto? payload,
    String locale,
  ) {
    return Text(
      '${AppLocalizations.of(context)!.report}: ${widget.executionId}${widget.variant != 'default' ? ' (${widget.variant})' : ''}',
      style: Theme.of(context).textTheme.titleMedium,
    );
  }
}
