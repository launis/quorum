import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:client_app/core/state/mutation.dart';
import 'package:client_app/features/studio/controllers/studio_controller.dart';
import 'package:client_app/features/studio/models/workflow.dart';

import 'package:client_app/core/error/app_error_ext.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/features/studio/controllers/mcp_gateways_controller.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/core/error/app_error_boundary.dart';
import 'package:client_app/core/logging/logger_service.dart';

import 'widgets/workflow/workflow_general_tab.dart';
import 'widgets/workflow/workflow_inputs_tab.dart';
import 'widgets/workflow/workflow_steps_tab.dart';

/// **Workflow DAG Builder (Gold Standard Phase 9)**
///
/// CRUD interface for managing Semantic Routing & DAG structures.
/// Admin can define global inputs (`expected_inputs`) and sequence
/// processing steps (`steps`) including `depends_on` and `input_mappings`.
/// Componentized to enforce Flat MVC architecture using the Sub-Tabs pattern.
final _workflowClonePayload =
    NotifierProvider<WorkflowClonePayloadNotifier, Workflow?>(
      WorkflowClonePayloadNotifier.new,
    );

class WorkflowClonePayloadNotifier extends Notifier<Workflow?> {
  @override
  Workflow? build() => null;
  void setPayload(Workflow? payload) => state = payload;
}

class WorkflowBuilderView extends HookConsumerWidget {
  final String? id;
  final String? slug;

  const WorkflowBuilderView({super.key, this.id, this.slug});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final wfId = (id ?? '').isEmpty ? 'new' : id!;

    final formState = ref.watch(workflowFormProvider(wfId));
    final stepsAsync = ref.watch(stepsControllerProvider);
    final mcpGatewaysAsync = ref.watch(mcpGatewaysControllerProvider);

    return switch (formState) {
      AsyncData(:final value) => () {
        // Absolute Fail-Fast
        if (stepsAsync.hasError) throw stepsAsync.error!;
        if (mcpGatewaysAsync.hasError) throw mcpGatewaysAsync.error!;
        if (!stepsAsync.hasValue || !mcpGatewaysAsync.hasValue) {
          return const Scaffold(
            body: Center(child: CircularProgressIndicator()),
          );
        }

        return _BuilderScaffoldWrapper(
          wfId: wfId,
          payload: value,
          blueprints: stepsAsync.value!,
          mcpGateways: mcpGatewaysAsync.value ?? [],
          l10n: l10n,
        );
      }(),
      AsyncError(:final error, :final stackTrace) => Scaffold(
        appBar: AppBar(title: Text(l10n.workflowEditTitle)),
        body: ErrorView(
          error: error,
          stackTrace: stackTrace,
          compact: false,
          onRetry: () => ref.invalidate(workflowFormProvider(wfId)),
        ),
      ),
      _ => Scaffold(
        appBar: AppBar(title: Text(l10n.workflowEditTitle)),
        body: const Center(child: CircularProgressIndicator()),
      ),
    };
  }
}

class _BuilderScaffoldWrapper extends HookConsumerWidget {
  final String wfId;
  final Workflow payload;
  final List<NodeStrategy> blueprints;
  final List<Map<String, dynamic>> mcpGateways;
  final AppLocalizations l10n;

  const _BuilderScaffoldWrapper({
    required this.wfId,
    required this.payload,
    required this.blueprints,
    required this.mcpGateways,
    required this.l10n,
  });

  void _cloneWorkflow(
    BuildContext context,
    WidgetRef ref,
    Workflow currentPayload,
  ) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(l10n.workflowCloneBtn),
        content: Text(l10n.workflowSharedBlueprintWarning),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: Text(l10n.cancel),
          ),
          FilledButton(
            onPressed: () async {
              Navigator.of(ctx).pop();
              final messenger = ScaffoldMessenger.of(context);

              try {
                // SSoT Mandate: Backend performs the cloning to generate valid sr_ opaque IDs.
                final clonedWorkflow = await ref
                    .read(workflowsControllerProvider.notifier)
                    .cloneWorkflow(currentPayload.id);

                ref
                    .read(_workflowClonePayload.notifier)
                    .setPayload(clonedWorkflow); // keep track for snapshot

                if (context.mounted) {
                  final fallbackSlug = clonedWorkflow.slug.isNotEmpty
                      ? clonedWorkflow.slug
                      : 'copy';
                  context.go(
                    '/admin/workflow/edit/${clonedWorkflow.id}/$fallbackSlug',
                  );
                }

                messenger.showSnackBar(
                  SnackBar(content: Text(l10n.workflowCloneSuccess)),
                );
              } catch (e) {
                final errorMsg = e is AppException
                    ? AppExceptionX.extractLocalizedHint(e, l10n)
                    : e.toString();
                if (context.mounted) {
                  ref
                      .read(loggerServiceProvider)
                      .error('Studio', 'Failed to clone workflow: $e', e);
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text(errorMsg),
                      backgroundColor: Theme.of(context).colorScheme.error,
                    ),
                  );
                }
              }
            },
            child: Text(l10n.workflowCloneBtn),
          ),
        ],
      ),
    );
  }

  void _deleteWorkflow(
    BuildContext context,
    WidgetRef ref,
    MutationState<void> deleteMutation,
  ) {
    final idStr = payload.id;
    if (idStr.isEmpty) return;

    final nameToDisplay =
        payload.name.translations['fi'] ??
        payload.name.translations['en'] ??
        idStr;

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(l10n.workflowDeleteConfirmTitle),
        content: Text(l10n.workflowDeleteConfirmDesc(nameToDisplay)),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: Text(l10n.cancel),
          ),
          MutationButton<void>(
            mutation: deleteMutation,
            label: l10n.delete,
            action: () async {
              await ref
                  .read(workflowsControllerProvider.notifier)
                  .deleteWorkflow(idStr);
              if (ctx.mounted) Navigator.pop(ctx);
            },
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final idController = useTextEditingController(text: payload.id);
    final slugController = useTextEditingController(text: payload.slug);

    // Hydrate clone payload exactly once if it's a clone process
    useEffect(() {
      final cloneData = ref.read(_workflowClonePayload);
      if (cloneData != null && wfId == 'new') {
        if (payload.id.isEmpty) {
          Future.microtask(() {
            idController.text = cloneData.id;
            slugController.text = cloneData.slug;

            // Clear clone payload so it doesn't trigger again
            ref.read(_workflowClonePayload.notifier).setPayload(null);
            ref
                .read(workflowFormProvider(wfId).notifier)
                .forceRebuild(cloneData);
          });
        }
      }
      return null;
    }, const []);

    final validateMutation = useMutation<Map<String, dynamic>>(
      onSuccess: (data) {
        if (context.mounted) {
          final isValid = data['valid'] == true;
          final errors = List<dynamic>.from(
            data['errors'] ?? [],
          ).map((e) => e.toString()).toList();
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(
                isValid
                    ? l10n.simulatorValidDag
                    : l10n.simulatorDagErrors(errors.join(', ')),
              ),
              backgroundColor: isValid
                  ? const Color(0xFF2E7D32)
                  : Theme.of(context).colorScheme.error,
            ),
          );
        }
      },
      onError: (e) {
        if (context.mounted) {
          ref
              .read(loggerServiceProvider)
              .error('Studio', 'Failed to validate workflow: $e', e);
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(l10n.simulatorFailedError(e.toString())),
              backgroundColor: Theme.of(context).colorScheme.error,
            ),
          );
        }
      },
    );

    final deleteMutation = useMutation<void>(
      onSuccess: (_) {
        if (context.mounted) {
          ScaffoldMessenger.of(
            context,
          ).showSnackBar(SnackBar(content: Text(l10n.delete)));
          context.pop();
        }
      },
      onError: (e) {
        if (context.mounted) {
          final errorMsg = AppExceptionX.extractLocalizedHint(e, l10n);
          ref
              .read(loggerServiceProvider)
              .error('Studio', 'Failed to delete workflow: $e', e);
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(errorMsg),
              backgroundColor: Theme.of(context).colorScheme.error,
            ),
          );
        }
      },
    );

    Future<void> saveWorkflow() async {
      final id = idController.text.trim();
      final slug = slugController.text.trim();
      if (id.isEmpty) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(l10n.idRequiredError),
            backgroundColor: Theme.of(context).colorScheme.error,
          ),
        );
        return;
      }

      final newWorkflow = payload.copyWith(id: id, slug: slug);

      try {
        await ref.read(workflowFormProvider(wfId).notifier).submit(newWorkflow);
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text(
                'Workflow saved successfully',
              ), // Using hardcoded or localized
              backgroundColor: Color(0xFF2E7D32),
            ),
          );
          context.pop();
        }
      } catch (e) {
        if (context.mounted) {
          final errorMsg = e is AppException
              ? AppExceptionX.extractLocalizedHint(e, l10n)
              : e.toString();
          ref
              .read(loggerServiceProvider)
              .error('Studio', 'Failed to save workflow: $e', e);
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(errorMsg),
              backgroundColor: Theme.of(context).colorScheme.error,
            ),
          );
        }
      }
    }

    void triggerUpdate(Workflow updated) {
      ref.read(workflowFormProvider(wfId).notifier).forceRebuild(updated);
    }

    return DefaultTabController(
      length: 3,
      child: AppExceptionBoundary(
        child: Scaffold(
          appBar: AppBar(
            leading: IconButton(
              icon: const Icon(Icons.arrow_back),
              tooltip: 'Back to Studio',
              onPressed: () => context.go('/admin'),
            ),
            title: Builder(
              builder: (context) {
                final titleStr =
                    payload.name.translations['fi'] ??
                    payload.name.translations['en'] ??
                    payload.name.defaultLocale;

                if (titleStr.isEmpty && payload.id.isNotEmpty) {
                  return Text(
                    l10n.workflowNameMissingError,
                    style: TextStyle(
                      color: Theme.of(context).colorScheme.error,
                    ),
                  );
                }
                return Text(
                  titleStr.isEmpty ? l10n.workflowEditTitle : titleStr,
                );
              },
            ),
            actions: [
              if (payload.id.isNotEmpty) ...[
                IconButton(
                  onPressed: () => _cloneWorkflow(context, ref, payload),
                  icon: const Icon(Icons.content_copy),
                  tooltip: l10n.workflowCloneBtn,
                ),
                IconButton(
                  onPressed: () =>
                      _deleteWorkflow(context, ref, deleteMutation),
                  icon: Icon(
                    Icons.delete,
                    color: Theme.of(context).colorScheme.error,
                  ),
                  tooltip: l10n.delete,
                ),
              ],
              IconButton(
                onPressed: validateMutation.isLoading
                    ? null
                    : () {
                        validateMutation.mutate(() async {
                          return await ref
                              .read(workflowsControllerProvider.notifier)
                              .simulateWorkflow(payload);
                        });
                      },
                icon: validateMutation.isLoading
                    ? const SizedBox(
                        width: 16,
                        height: 16,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : Icon(
                        Icons.bug_report,
                        color: Theme.of(context).colorScheme.primary,
                      ),
                tooltip: l10n.validateDagBtn,
              ),
              TextButton.icon(
                onPressed: saveWorkflow,
                icon: const Icon(Icons.save),
                label: Text(l10n.studioSaveButton),
              ),
              const SizedBox(width: 16),
            ],
            bottom: TabBar(
              tabs: [
                Tab(
                  icon: const Icon(Icons.settings),
                  text: l10n.workflowTabGeneral,
                ),
                Tab(
                  icon: const Icon(Icons.input),
                  text: l10n.workflowTabInputs,
                ),
                Tab(
                  icon: const Icon(Icons.account_tree),
                  text: l10n.workflowTabSteps,
                ),
              ],
            ),
          ),
          body: TabBarView(
            children: [
              WorkflowGeneralTab(
                workflow: payload,
                idController: idController,
                slugController: slugController,
                onChanged: triggerUpdate,
              ),
              WorkflowInputsTab(workflow: payload, onChanged: triggerUpdate),
              WorkflowStepsTab(
                workflow: payload,
                blueprints: blueprints,
                mcpGateways: mcpGateways,
                onChanged: triggerUpdate,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
