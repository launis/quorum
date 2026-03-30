import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/core/network/api_client.dart';
import 'package:client_app/utils/safe_cast.dart';
import 'package:client_app/router/router.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

import 'package:client_app/core/error/app_error_ext.dart';
import 'package:client_app/features/execution/views/new_execution_view.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:file_saver/file_saver.dart';
import 'dart:typed_data';
import 'package:dio/dio.dart';

import 'dart:async'; // Add dart:async for Timer

/// Centralized settings for the Execution Dashboard
class DashboardSettings {
  const DashboardSettings._();

  /// Auto-refresh interval for the continuous background polling
  static const Duration refreshRate = Duration(seconds: 10);

  /// Global timeout for the PDF streams
  static const Duration downloadTimeout = Duration(seconds: 15);
}

// Provider to fetch executions using SafeCast (No Freezed API DTOs)
final executionListProvider =
    FutureProvider.autoDispose<List<Map<String, dynamic>>>((ref) async {
      // 1. Riverpod Polling (Auto-Refresh)
      // Poll backend every 10 seconds to keep the Execution Dashboard alive and fresh,
      // bypassing the StatefulShellRoute cache stagnation issue.
      final timer = Timer(DashboardSettings.refreshRate, () {
        ref.invalidateSelf();
      });
      ref.onDispose(timer.cancel);

      final dio = ref.watch(apiClientProvider);
      final response = await dio.get('/execution/executions');

      final List<dynamic> data = SafeCast.safeList(response.data);
      return data.map((e) => SafeCast.safeMap(e)).toList();
    });

class DashboardView extends ConsumerStatefulWidget {
  const DashboardView({super.key});

  @override
  ConsumerState<DashboardView> createState() => _DashboardViewState();
}

class _DashboardViewState extends ConsumerState<DashboardView> with RouteAware {
  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    final route = ModalRoute.of(context);
    if (route != null) {
      routeObserver.subscribe(this, route);
    }
  }

  @override
  void dispose() {
    routeObserver.unsubscribe(this);
    super.dispose();
  }

  @override
  void didPopNext() {
    // Called when the top route has been popped off, and the current route shows up.
    // E.g., user returns from ExecutionView to DashboardView.
    // We aggressively invalidate the cache here so it fetches fresh status.
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) {
        ref.invalidate(executionListProvider);
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    // 1. Initial aggressive load logic
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) {
        // ref.invalidate(executionListProvider);
      }
    });

    final asyncExecutions = ref.watch(executionListProvider);
    final asyncWorkflows = ref.watch(availableWorkflowsProvider);

    return Scaffold(
      appBar: AppBar(
        title: Text(AppLocalizations.of(context)!.executionsDashboardTitle),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () => ref.invalidate(executionListProvider),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => const NewExecutionRoute().go(context),
        icon: const Icon(Icons.add),
        label: Text(AppLocalizations.of(context)!.newAnalysis),
      ),
      body: asyncExecutions.when(
        data: (executions) {
          if (executions.isEmpty) {
            return Center(
              child: Text(AppLocalizations.of(context)!.noExecutions),
            );
          }
          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: executions.length,
            itemBuilder: (context, index) {
              final exec = executions[index];
              final id = SafeCast.safeString(exec['id']);
              final status = SafeCast.safeString(exec['status']);
              final workflowId = SafeCast.safeString(exec['workflow_id']);
              final createdAt = SafeCast.safeString(exec['created_at']);

              // Formatting date
              String dateStr = createdAt;
              if (createdAt.isNotEmpty) {
                try {
                  final dt = DateTime.parse(createdAt).toLocal();
                  dateStr =
                      '${dt.year}-${dt.month.toString().padLeft(2, '0')}-${dt.day.toString().padLeft(2, '0')} ${dt.hour.toString().padLeft(2, '0')}:${dt.minute.toString().padLeft(2, '0')}';
                } catch (e, st) {
                  ref
                      .read(loggerServiceProvider)
                      .error(
                        'DashboardView',
                        'Failed to parse createdAt date: $createdAt',
                        e,
                        st,
                      );
                  throw AppException.validation(
                    'Corrupted DateTime string in execution data: $createdAt',
                  );
                }
              }

              // Metrics
              final costEstimate = SafeCast.safeDouble(exec['cost_estimate']);
              final totalTokens = SafeCast.safeInt(exec['total_tokens']);

              String metricsStr = '';
              if (totalTokens > 0 || costEstimate > 0) {
                final l10n = AppLocalizations.of(context)!;
                metricsStr =
                    '\n${l10n.executionCostEstimate(costEstimate.toStringAsFixed(6))} | ${l10n.tokensUsed(totalTokens)}';
              }

              // Resolve Workflow Name
              String workflowDisplay = AppLocalizations.of(
                context,
              )!.workflowPrefixLabel(workflowId);
              if (asyncWorkflows is AsyncData && asyncWorkflows.value != null) {
                final workflows = asyncWorkflows.value!;
                final wf = workflows
                    .where((w) => SafeCast.safeString(w['id']) == workflowId)
                    .firstOrNull;
                if (wf != null) {
                  final nameMap = SafeCast.safeMap(wf['name']);
                  final titleStr = nameMap.isNotEmpty
                      ? (nameMap['translations']?[nameMap['default_locale']] ??
                            nameMap['default_locale'] ??
                            workflowId)
                      : (SafeCast.safeString(wf['name']).isNotEmpty
                            ? SafeCast.safeString(wf['name'])
                            : workflowId);
                  workflowDisplay = AppLocalizations.of(
                    context,
                  )!.workflowPrefixLabel(titleStr);
                }
              }

              return Card(
                margin: const EdgeInsets.only(bottom: 12),
                child: ListTile(
                  title: Text(
                    workflowDisplay,
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                  subtitle: Text(
                    '${AppLocalizations.of(context)!.executionIdLabel(id)}\n${AppLocalizations.of(context)!.created}: $dateStr$metricsStr',
                  ),
                  trailing: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      _buildStatusChip(status),
                      const SizedBox(width: 8),
                      if (status.toLowerCase() == 'completed') ...[
                        IconButton(
                          icon: Icon(
                            Icons.print,
                            color: Theme.of(context).colorScheme.primary,
                          ),
                          tooltip: AppLocalizations.of(
                            context,
                          )!.printVariantSelectorTitle,
                          onPressed: () => _showVariantSelector(
                            context,
                            id,
                            workflowId,
                            asyncWorkflows,
                          ),
                        ),
                        const SizedBox(width: 8),
                      ],
                      IconButton(
                        icon: Icon(
                          Icons.delete,
                          color: Theme.of(context).colorScheme.error,
                        ),
                        tooltip: AppLocalizations.of(
                          context,
                        )!.deleteExecutionTooltip,
                        onPressed: () => _confirmDelete(context, ref, id),
                      ),
                    ],
                  ),
                  isThreeLine: true,
                  onTap: () {
                    // Navigate to details safely using GoRouter codegen
                    if (status.toLowerCase() == 'completed') {
                      ExecutionReportRoute(executionId: id).go(context);
                    } else {
                      ExecutionRoute(executionId: id).go(context);
                    }
                  },
                ),
              );
            },
          );
        },
        error: (err, stack) => ErrorView(
          error: err,
          stackTrace: stack,
          onRetry: () => ref.invalidate(executionListProvider),
        ),
        loading: () => const Center(child: CircularProgressIndicator()),
      ),
    );
  }

  void _showVariantSelector(
    BuildContext context,
    String executionId,
    String workflowId,
    AsyncValue<List<Map<String, dynamic>>> asyncWorkflows,
  ) {
    if (workflowId.isEmpty) return;

    final workflows = asyncWorkflows.asData?.value ?? [];
    final wf = workflows.firstWhere(
      (w) => SafeCast.safeString(w['id']) == workflowId,
      orElse: () => <String, dynamic>{},
    );

    if (wf.isEmpty) {
      _downloadPdf(executionId, 'default');
      return;
    }

    final outputProfiles = SafeCast.safeMap(wf['output_profiles']);
    final variants = outputProfiles.keys.toList();
    if (variants.isEmpty) variants.add('default');

    if (variants.length == 1) {
      ExecutionReportRoute(
        executionId: executionId,
        variant: variants.first,
      ).go(context);
      return;
    }

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (ctx) {
        return SafeArea(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Padding(
                padding: const EdgeInsets.all(16.0),
                child: Text(
                  AppLocalizations.of(context)!.printVariantSelectorTitle,
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              Padding(
                padding: const EdgeInsets.only(
                  left: 16.0,
                  right: 16.0,
                  bottom: 16.0,
                ),
                child: Text(
                  AppLocalizations.of(context)!.printVariantSelectorDescription,
                ),
              ),
              const Divider(height: 1),
              Flexible(
                child: SingleChildScrollView(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: variants
                        .map(
                          (v) => ListTile(
                            leading: Icon(
                              v == 'default' ? Icons.star : Icons.description,
                              color: Colors.blue,
                            ),
                            title: Text(v),
                            onTap: () {
                              Navigator.of(ctx).pop();
                              ExecutionReportRoute(
                                executionId: executionId,
                                variant: v,
                              ).go(context);
                            },
                          ),
                        )
                        .toList(),
                  ),
                ),
              ),
              const SizedBox(height: 16),
            ],
          ),
        );
      },
    );
  }

  Future<void> _downloadPdf(String executionId, String profileId) async {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(AppLocalizations.of(context)!.processingStatus)),
    );

    try {
      final dio = ref.read(apiClientProvider);
      final response = await dio.get<List<int>>(
        '/execution/executions/$executionId/render',
        queryParameters: {'format': 'pdf', 'profile_id': profileId},
        options: Options(responseType: ResponseType.bytes),
      );

      final bytes = Uint8List.fromList(response.data!);
      await FileSaver.instance
          .saveAs(
            name: 'Report_${executionId}_$profileId',
            bytes: bytes,
            fileExtension: 'pdf',
            mimeType: MimeType.pdf,
          )
          .timeout(
            DashboardSettings.downloadTimeout,
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
      if (mounted) {
        ref
            .read(loggerServiceProvider)
            .error('DashboardView', 'Failed to download PDF', e, st);

        final l10n = AppLocalizations.of(context)!;
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(AppExceptionX.extractLocalizedHint(e, l10n)),
            backgroundColor: Theme.of(context).colorScheme.error,
          ),
        );
      }
    }
  }

  Future<void> _confirmDelete(
    BuildContext context,
    WidgetRef ref,
    String id,
  ) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(AppLocalizations.of(context)!.confirmDeletionTitle),
        content: Text(AppLocalizations.of(context)!.confirmDeletionMessage),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(false),
            child: Text(AppLocalizations.of(context)!.cancel),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: Theme.of(context).colorScheme.error,
              foregroundColor: Theme.of(context).colorScheme.onError,
            ),
            onPressed: () => Navigator.of(ctx).pop(true),
            child: Text(AppLocalizations.of(context)!.delete),
          ),
        ],
      ),
    );

    if (confirmed == true && context.mounted) {
      try {
        final dio = ref.read(apiClientProvider);
        await dio.delete('/execution/executions/$id');
        ref.invalidate(executionListProvider);
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(
                AppLocalizations.of(context)!.executionDeletedSuccessfully,
              ),
            ),
          );
        }
      } catch (e, st) {
        ref
            .read(loggerServiceProvider)
            .error(
              'DashboardView',
              'DELETE_FAILED: Failed to delete execution',
              e,
              st,
            );
        if (context.mounted) {
          final l10n = AppLocalizations.of(context)!;
          final errorMsg = AppExceptionX.extractLocalizedHint(e, l10n);
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(l10n.failedToDeleteExecution(errorMsg)),
              backgroundColor: Theme.of(context).colorScheme.error,
            ),
          );
        }
      }
    }
  }

  Widget _buildStatusChip(String status) {
    Color bgColor = Theme.of(context).colorScheme.surfaceContainerHighest;
    Color textColor = Theme.of(context).colorScheme.onSurfaceVariant;
    final s = status.toLowerCase();

    if (s == 'completed') {
      bgColor = Theme.of(context).colorScheme.primaryContainer;
      textColor = Theme.of(context).colorScheme.onPrimaryContainer;
    } else if (s == 'failed') {
      bgColor = Theme.of(context).colorScheme.error;
      textColor = Theme.of(context).colorScheme.onError;
    } else if (s == 'running' || s == 'pending') {
      bgColor = Theme.of(context).colorScheme.primary;
      textColor = Theme.of(context).colorScheme.onPrimary;
    }

    return Chip(
      label: Text(
        status.toUpperCase(),
        style: TextStyle(
          color: textColor,
          fontSize: 12,
          fontWeight: FontWeight.bold,
        ),
      ),
      backgroundColor: bgColor,
      side: BorderSide.none,
    );
  }
}
