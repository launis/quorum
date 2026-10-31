import 'package:client_app/core/error/app_error_boundary.dart';
import 'package:client_app/core/error/app_error_ext.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/network/api_client.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/features/execution/controllers/execution_controller.dart';
import 'package:client_app/features/execution/models/execution_create_request_dto.dart';
import 'package:client_app/features/execution/models/execution_record.dart';
import 'package:client_app/features/execution/views/new_execution_view.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/router/router.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

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
      body: AppErrorBoundary(
        child: switch (asyncExecutions) {
          AsyncData(:final value) =>
            value.isEmpty
                ? Center(
                    child: Text(AppLocalizations.of(context)!.noExecutions),
                  )
                : ListView.builder(
                    padding: AppSpacing.p16,
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
                      final costEstimate =
                          (exec.costEstimate != null && exec.costEstimate! > 0)
                          ? exec.costEstimate!
                          : (exec.dagCostUsd +
                                (exec.cumulativeSynthesisCost ?? 0.0));
                      final promptTokens = exec.promptTokens;
                      final completionTokens = exec.completionTokens;
                      final reasoningTokens = exec.reasoningTokens;
                      final synthTokens = exec.cumulativeSynthesisTokens ?? 0;
                      final totalTokens =
                          promptTokens +
                          completionTokens +
                          reasoningTokens +
                          synthTokens;

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
                      if (asyncWorkflows case AsyncData(
                        value: final workflows,
                      )) {
                        final wf = workflows
                            .where((w) => w.id == workflowId)
                            .firstOrNull;
                        if (wf != null) {
                          final locale = Localizations.localeOf(
                            context,
                          ).languageCode;
                          final titleStr = wf.name.get(locale);
                          workflowDisplay = AppLocalizations.of(
                            context,
                          )!.workflowPrefixLabel(titleStr);
                        }
                      }

                      return Card(
                        margin: const EdgeInsets.only(bottom: AppSpacing.s12),
                        child: ListTile(
                          title: Text(
                            workflowDisplay,
                            style: Theme.of(context).textTheme.titleMedium
                                ?.copyWith(fontWeight: FontWeight.bold),
                          ),
                          subtitle: Text(
                            '${AppLocalizations.of(context)!.executionIdLabel(id)}\n${AppLocalizations.of(context)!.created}: $dateStr$metricsStr',
                          ),
                          trailing: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              _buildStatusChip(status),
                              AppSpacing.w8,
                              if (status.toLowerCase() == 'passed' ||
                                  status.toLowerCase() == 'completed') ...[
                                IconButton(
                                  icon: Icon(
                                    Icons.print,
                                    color: Theme.of(
                                      context,
                                    ).colorScheme.primary,
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
                                AppSpacing.w8,
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
                              AppSpacing.w8,
                              IconButton(
                                icon: Icon(
                                  Icons.delete,
                                  color: Theme.of(context).colorScheme.error,
                                ),
                                tooltip: AppLocalizations.of(
                                  context,
                                )!.deleteExecutionTooltip,
                                onPressed: () =>
                                    _confirmDelete(context, ref, id),
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
      ),
    );
  }

  void _showVariantSelector(
    BuildContext context,
    String executionId,
    String workflowId,
    AsyncValue<List<Workflow>> asyncWorkflows,
  ) {
    if (workflowId.isEmpty) return;

    final workflows = switch (asyncWorkflows) {
      AsyncData(:final value) => value,
      _ => const <Workflow>[],
    };
    final wf = workflows.where((w) => w.id == workflowId).firstOrNull;

    if (wf == null) {
      final error = AppException.validation(
        'CRITICAL FAIL-FAST: Workflow $workflowId is not found in the payload for execution $executionId.',
      );
      ref
          .read(loggerServiceProvider)
          .error(
            'DashboardView',
            'WORKFLOW_NOT_FOUND: Workflow $workflowId missing for execution $executionId',
            error,
            StackTrace.current,
          );
      throw error;
    }

    final outputProfiles = wf.outputProfiles;
    final variants = outputProfiles.keys.toList();

    if (variants.isEmpty) {
      // Graceful degradation when no output profiles are configured on the workflow
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(AppLocalizations.of(context)!.errorValidation),
          backgroundColor: Theme.of(context).colorScheme.error,
        ),
      );
      return; // Do not crash the UI, just abort opening the modal.
    }

    // Navigation short-circuit removed to enforce modal appearance,
    // ensuring the user always has access to the "Clear profile synthesis" action.

    showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(
          top: Radius.circular(AppSpacing.s16),
        ),
      ),
      builder: (ctx) {
        return SafeArea(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Padding(
                padding: AppSpacing.p16,
                child: Text(
                  AppLocalizations.of(context)!.printVariantSelectorTitle,
                  style: Theme.of(
                    context,
                  ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
                ),
              ),
              Padding(
                padding: const EdgeInsets.only(
                  left: AppSpacing.s16,
                  right: AppSpacing.s16,
                  bottom: AppSpacing.s16,
                ),
                child: Text(
                  AppLocalizations.of(context)!.printVariantSelectorDescription,
                ),
              ),
              const Divider(),
              Flexible(
                child: SingleChildScrollView(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: variants
                        .map(
                          (v) => ListTile(
                            leading: Icon(
                              v == 'default' ? Icons.star : Icons.description,
                              color: Theme.of(context).colorScheme.primary,
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
                                if (!context.mounted) return;
                                ExecutionReportRoute(
                                  executionId: executionId,
                                  variant: v,
                                ).go(context);
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
              AppSpacing.h16,
            ],
          ),
        );
      },
    );
  }

  String _getVariantDisplayName(
    BuildContext context,
    String key,
    Map<String, OutputProfile> outputProfiles,
  ) {
    if (key == 'default') {
      return AppLocalizations.of(context)!.reportTitleMain;
    }

    final profile = outputProfiles[key];
    if (profile != null) {
      final locale = Localizations.localeOf(context).languageCode;
      return profile.name.get(locale);
    }
    final error = AppException.validation(
      'Fail-Fast: Missing required translation for key $key.',
    );
    ref
        .read(loggerServiceProvider)
        .error(
          'DashboardView',
          'VARIANT_PROFILE_MISSING: Missing OutputProfile for key $key',
          error,
          StackTrace.current,
        );
    throw error;
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
        await dio.delete<void>('/execution/executions/$id');
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

      // 1. Fetch old execution and validate against ExecutionRecord schema
      final getResponse = await dio.get<Map<String, Object?>>(
        '/execution/executions/$id',
      );
      final oldExecData = getResponse.data;
      if (oldExecData == null) {
        final error = AppException.network(
          'Invalid response from server',
        ).copyWith(extensions: const {'error_code': 'INVALID_RESPONSE'});
        ref
            .read(loggerServiceProvider)
            .error(
              'DashboardView',
              'RERUN_NULL_PAYLOAD: Null response data when cloning execution $id',
              error,
              StackTrace.current,
            );
        throw error;
      }
      final oldExec = ExecutionRecord.fromJson(oldExecData);

      // 2. Prepare strongly typed request DTO
      final request = ExecutionCreateRequestDto(
        workflowId: oldExec.workflowId,
        targetLocale: oldExec.targetLocale,
        rawInputs: oldExec.rawInputs?.toJson() ?? const <String, Object?>{},
        profileId: oldExec.outputProfileId,
      );

      // 3. Post to create new execution
      await dio.post<Map<String, Object?>>(
        '/execution/executions/',
        data: request.toJson(),
      );

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
      await dio.delete<void>(
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
        style: Theme.of(context).textTheme.labelSmall?.copyWith(
          color: textColor,
          fontWeight: FontWeight.bold,
        ),
      ),
      backgroundColor: bgColor,
      side: BorderSide.none,
    );
  }
}
