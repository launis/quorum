import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/core/network/api_client.dart';

import 'package:client_app/router/router.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

import 'package:client_app/core/error/app_error_ext.dart';
import 'package:client_app/features/execution/views/new_execution_view.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/error/app_exception.dart';

import 'package:client_app/features/execution/controllers/execution_controller.dart';

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
      body: switch (asyncExecutions) {
        AsyncData(:final value) =>
          value.isEmpty
              ? Center(child: Text(AppLocalizations.of(context)!.noExecutions))
              : ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: value.length,
                  itemBuilder: (context, index) {
                    final exec = value[index];
                    final id = exec.id;
                    final status = exec.status;
                    final workflowId = exec.workflowId;
                    final createdAt = exec.createdAt ?? '';

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
                    final costEstimate = exec.costEstimate ?? 0.0;
                    final metadata = exec.metadata ?? {};
                    final totalTokens =
                        (metadata['total_tokens'] as num?)?.toInt() ?? 0;
                    final promptTokens =
                        (metadata['prompt_tokens'] as num?)?.toInt() ?? 0;
                    final completionTokens =
                        (metadata['completion_tokens'] as num?)?.toInt() ?? 0;

                    String metricsStr = '';
                    if (totalTokens > 0 ||
                        promptTokens > 0 ||
                        completionTokens > 0 ||
                        costEstimate > 0) {
                      final l10n = AppLocalizations.of(context)!;
                      String tokensStr;
                      if (promptTokens > 0 || completionTokens > 0) {
                        tokensStr =
                            '${l10n.reportPromptTokens(promptTokens.toString())} | ${l10n.reportCompletionTokens(completionTokens.toString())}';
                      } else {
                        tokensStr = l10n.tokensUsed(totalTokens);
                      }
                      metricsStr =
                          '\n${l10n.executionCostEstimate(costEstimate.toStringAsFixed(6))} | $tokensStr';
                    }

                    // Resolve Workflow Name
                    String workflowDisplay = AppLocalizations.of(
                      context,
                    )!.workflowPrefixLabel(workflowId);
                    if (asyncWorkflows is AsyncData &&
                        asyncWorkflows.value != null) {
                      final workflows = asyncWorkflows.value!;
                      final wf = workflows
                          .where((w) => w['id']?.toString() == workflowId)
                          .firstOrNull;
                      if (wf != null) {
                        final nameMapRaw = wf['name'];
                        final nameMap = nameMapRaw is Map ? nameMapRaw : {};
                        final titleStr = nameMap.isNotEmpty
                            ? (nameMap['translations']?[nameMap['default_locale']] ??
                                  nameMap['default_locale'] ??
                                  (throw AppException.validation(
                                    'Fail-Fast: Missing required translation.',
                                  )))
                            : ((wf['name']?.toString() ?? '').isNotEmpty
                                  ? wf['name']?.toString() ?? ''
                                  : (throw AppException.validation(
                                      'Fail-Fast: Missing required translation.',
                                    )));
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
                            if (status.toLowerCase() == 'passed' ||
                                status.toLowerCase() == 'completed') ...[
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
                                Icons.replay,
                                color: Theme.of(context).colorScheme.primary,
                              ),
                              tooltip: AppLocalizations.of(
                                context,
                              )!.rerunExecutionTooltip,
                              onPressed: () =>
                                  _cloneAndRunExecution(context, ref, id),
                            ),
                            const SizedBox(width: 8),
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
                          if (status.toLowerCase() == 'passed' ||
                              status.toLowerCase() == 'completed') {
                            ExecutionReportRoute(executionId: id).go(context);
                          } else {
                            ExecutionRoute(executionId: id).go(context);
                          }
                        },
                      ),
                    );
                  },
                ),
        AsyncError(:final error, :final stackTrace) => ErrorView(
          error: error,
          stackTrace: stackTrace,
          onRetry: () => ref.invalidate(executionListProvider),
        ),
        _ => const Center(child: CircularProgressIndicator()),
      },
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
      (w) => w['id']?.toString() == workflowId,
      orElse: () => <String, dynamic>{},
    );

    if (wf.isEmpty) {
      throw AppException.validation(
        'CRITICAL FAIL-FAST: Workflow $workflowId is not found in the payload for execution $executionId.',
      );
    }

    final opRaw = wf['output_profiles'];
    final outputProfiles = opRaw is Map ? opRaw : {};
    final variants = outputProfiles.keys.toList();

    if (variants.isEmpty) {
      // Epic 14: Graceful Degradation for Workflow Builder (No-String Mandate compliant)
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(AppLocalizations.of(context)!.errorValidation),
          backgroundColor: Colors.red,
        ),
      );
      return; // Do not crash the UI, just abort opening the modal.
    }

    // Navigation short-circuit removed to enforce modal appearance,
    // ensuring the user always has access to the "Clear profile synthesis" action.

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
                            title: Text(
                              _getVariantDisplayName(
                                context,
                                v,
                                outputProfiles,
                              ),
                            ),
                            trailing: IconButton(
                              icon: Icon(
                                Icons.refresh,
                                color: Theme.of(context).colorScheme.primary,
                              ),
                              tooltip: AppLocalizations.of(
                                context,
                              )!.regenerateProfileTooltip,
                              onPressed: () async {
                                Navigator.of(ctx).pop();
                                await _clearProfileCache(
                                  context,
                                  ref,
                                  executionId,
                                  v,
                                );
                                if (ctx.mounted) {
                                  ExecutionReportRoute(
                                    executionId: executionId,
                                    variant: v,
                                  ).go(context);
                                }
                              },
                            ),
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

  String _getVariantDisplayName(
    BuildContext context,
    String key,
    Map outputProfiles,
  ) {
    if (key == 'default') {
      return AppLocalizations.of(context)!.reportTitleMain;
    }

    final profile = outputProfiles[key];
    if (profile is Map) {
      final nameObj = profile['name'];
      if (nameObj is Map) {
        final translations = nameObj['translations'];
        final locale = Localizations.localeOf(context).languageCode;

        if (translations is Map) {
          return translations[locale]?.toString() ??
              translations['en']?.toString() ??
              (throw AppException.validation(
                'Fail-Fast: Missing required translation for key $key.',
              ));
        }
      }
    }
    throw AppException.validation(
      'Fail-Fast: Missing required translation for key $key.',
    );
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

  Future<void> _cloneAndRunExecution(
    BuildContext context,
    WidgetRef ref,
    String id,
  ) async {
    final l10n = AppLocalizations.of(context)!;
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(SnackBar(content: Text(l10n.processingStatus)));

    try {
      final dio = ref.read(apiClientProvider);

      // 1. Fetch old execution
      final getResponse = await dio.get('/execution/executions/$id');
      final Map<String, dynamic> oldExec = getResponse.data is Map
          ? getResponse.data as Map<String, dynamic>
          : throw AppException.network(
              'Invalid response from server',
            ).copyWith(extensions: const {'error_code': 'INVALID_RESPONSE'});

      // 2. Prepare payload
      final metadata = oldExec['metadata'] is Map
          ? oldExec['metadata'] as Map<String, dynamic>
          : {};
      final payload = {
        'workflow_id': oldExec['workflow_id'],
        'raw_inputs': oldExec['raw_inputs'],
        'profile_id':
            oldExec['output_profile_id'], // In Python it's output_profile_id inside ExecutionRecord
        'target_locale':
            metadata['target_locale'] ??
            Localizations.localeOf(context).languageCode,
      };

      // 3. Post to create new execution
      await dio.post('/execution/executions/', data: payload);

      // 4. Success UI & Invalidate Cache
      ref.invalidate(executionListProvider);
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(l10n.rerunExecutionSuccess),
            backgroundColor: Theme.of(context).colorScheme.primary,
          ),
        );
      }
    } catch (e, st) {
      if (context.mounted) {
        ref
            .read(loggerServiceProvider)
            .error(
              'DashboardView',
              'RERUN_FAILED: Failed to clone execution',
              e,
              st,
            );
        final errorMsg = AppExceptionX.extractLocalizedHint(
          e,
          AppLocalizations.of(context)!,
        );
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              AppLocalizations.of(context)!.rerunExecutionFailed(errorMsg),
            ),
            backgroundColor: Theme.of(context).colorScheme.error,
          ),
        );
      }
    }
  }

  Future<void> _clearProfileCache(
    BuildContext context,
    WidgetRef ref,
    String executionId,
    String profileId,
  ) async {
    final l10n = AppLocalizations.of(context)!;
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(SnackBar(content: Text(l10n.processingStatus)));

    try {
      final dio = ref.read(apiClientProvider);
      await dio.delete(
        '/execution/executions/$executionId/profiles/$profileId',
      );

      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(l10n.regenerateProfileSuccess),
            backgroundColor: Theme.of(context).colorScheme.primary,
          ),
        );
      }
    } catch (e, st) {
      if (context.mounted) {
        ref
            .read(loggerServiceProvider)
            .error(
              'DashboardView',
              'CLEAR_CACHE_FAILED: Failed to clear profile synthesis',
              e,
              st,
            );
        final errorMsg = AppExceptionX.extractLocalizedHint(
          e,
          AppLocalizations.of(context)!,
        );
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              AppLocalizations.of(context)!.regenerateProfileFailed(errorMsg),
            ),
            backgroundColor: Theme.of(context).colorScheme.error,
          ),
        );
      }
    }
  }

  Widget _buildStatusChip(String status) {
    Color bgColor = Theme.of(context).colorScheme.surfaceContainerHighest;
    Color textColor = Theme.of(context).colorScheme.onSurfaceVariant;
    final s = status.toLowerCase();

    if (s == 'passed' || s == 'completed') {
      bgColor = Theme.of(context).colorScheme.primaryContainer;
      textColor = Theme.of(context).colorScheme.onPrimaryContainer;
    } else if (s == 'failed') {
      bgColor = Theme.of(context).colorScheme.error;
      textColor = Theme.of(context).colorScheme.onError;
    } else if (s == 'running' || s == 'pending' || s == 'queued') {
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
