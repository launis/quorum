import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:client_app/core/state/mutation.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/features/studio/controllers/studio_controller.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/features/studio/models/mcp_gateway.dart';
import 'package:client_app/features/studio/models/step_simulation.dart';
import 'package:client_app/features/studio/models/workflow_simulation.dart';

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
import 'widgets/workflow/workflow_strictness_tab.dart';

/// CRUD interface for managing Semantic Routing & DAG structures.
/// Admin configures global inputs (`expected_inputs`) and sequences
/// processing steps (`steps`) including `depends_on` and `input_mappings`.
class WorkflowBuilderView extends HookConsumerWidget {
  final String? id;
  final String? slug;

  const WorkflowBuilderView({super.key, this.id, this.slug});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final wfId = (id == null || id!.isEmpty) ? 'new' : id!;

    final formState = ref.watch(workflowFormProvider(wfId));
    final stepsAsync = ref.watch(allBlueprintsProvider);
    final mcpGatewaysAsync = ref.watch(mcpGatewaysControllerProvider);

    return AppErrorBoundary(
      child: switch (formState) {
        AsyncData(:final value) => switch ((stepsAsync, mcpGatewaysAsync)) {
          (AsyncError(:final error, :final stackTrace), _) => Scaffold(
            appBar: AppBar(title: Text(l10n.workflowEditTitle)),
            body: ErrorView(
              error: error,
              stackTrace: stackTrace,
              compact: false,
              onRetry: () => ref.invalidate(allBlueprintsProvider),
            ),
          ),
          (_, AsyncError(:final error, :final stackTrace)) => Scaffold(
            appBar: AppBar(title: Text(l10n.workflowEditTitle)),
            body: ErrorView(
              error: error,
              stackTrace: stackTrace,
              compact: false,
              onRetry: () => ref.invalidate(mcpGatewaysControllerProvider),
            ),
          ),
          (
            AsyncData(value: final blueprints),
            AsyncData(value: final mcpGateways),
          ) =>
            _BuilderScaffoldWrapper(
              wfId: wfId,
              payload: value,
              blueprints: blueprints,
              mcpGateways: mcpGateways,
              l10n: l10n,
            ),
          _ => const Scaffold(body: Center(child: CircularProgressIndicator())),
        },
        AsyncError(:final error, :final stackTrace) => Scaffold(
          appBar: AppBar(title: Text(l10n.workflowEditTitle)),
          body: ErrorView(
            error: error,
            stackTrace: stackTrace,
            compact: false,
            onRetry: () => ref.invalidate(workflowFormProvider(wfId)),
          ),
        ),
        AsyncLoading() => Scaffold(
          appBar: AppBar(title: Text(l10n.workflowEditTitle)),
          body: const Center(child: CircularProgressIndicator()),
        ),
      },
    );
  }
}

class _BuilderScaffoldWrapper extends HookConsumerWidget {
  final String wfId;
  final Workflow payload;
  final List<NodeStrategy> blueprints;
  final List<McpGateway> mcpGateways;
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
    showDialog<void>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(l10n.workflowCloneBtn),
        content: Text(l10n.workflowSharedBlueprintWarning),
        actions: [
          TextButton(
            style: TextButton.styleFrom(
              enabledMouseCursor: SystemMouseCursors.click,
            ),
            onPressed: () => Navigator.of(ctx).pop(),
            child: Text(l10n.cancel),
          ),
          FilledButton(
            style: FilledButton.styleFrom(
              enabledMouseCursor: SystemMouseCursors.click,
            ),
            onPressed: () async {
              Navigator.of(ctx).pop();

              try {
                final clonedWorkflow = await ref
                    .read(workflowsControllerProvider.notifier)
                    .cloneWorkflow(currentPayload.id);

                if (!context.mounted) return;
                final fallbackSlug = clonedWorkflow.slug.isNotEmpty
                    ? clonedWorkflow.slug
                    : 'copy';
                context.go(
                  '/admin/workflow/edit/${clonedWorkflow.id}/$fallbackSlug',
                );
                ScaffoldMessenger.of(context).showSnackBar(
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

    final currentLocale = Localizations.localeOf(context).languageCode;
    final nameToDisplay = payload.name.get(currentLocale);

    showDialog<void>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(l10n.workflowDeleteConfirmTitle),
        content: Text(l10n.workflowDeleteConfirmDesc(nameToDisplay)),
        actions: [
          TextButton(
            style: TextButton.styleFrom(
              enabledMouseCursor: SystemMouseCursors.click,
            ),
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
    final syncedWorkflowId = useRef<String?>(null);

    useEffect(() {
      if (syncedWorkflowId.value != payload.id) {
        idController.text = payload.id;
        slugController.text = payload.slug;
        syncedWorkflowId.value = payload.id;
      }
      return null;
    }, [payload.id, payload.slug]);

    final simulationBanner = useState<WorkflowSimulationResponse?>(null);

    final validateMutation = useMutation<WorkflowSimulationResponse>(
      onSuccess: (data) {
        simulationBanner.value = data;
      },
      onError: (e) {
        if (context.mounted) {
          ref
              .read(loggerServiceProvider)
              .error('Studio', 'Failed to validate workflow: $e', e);
          simulationBanner.value = WorkflowSimulationResponse(
            valid: false,
            errors: [e.toString()],
            stepStatus: const {},
            executionOrder: const [],
            trace: const StepSimulationTraceDto(),
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
            SnackBar(
              content: Text(l10n.workflowSavedSuccess),
              backgroundColor: Theme.of(context).colorScheme.primary,
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
      length: 4,
      child: Scaffold(
        appBar: AppBar(
          leading: IconButton(
            mouseCursor: SystemMouseCursors.click,
            icon: const Icon(Icons.arrow_back),
            tooltip: l10n.backToStudioTooltip,
            onPressed: () => context.go('/admin'),
          ),
          title: Builder(
            builder: (context) {
              final currentLocale = Localizations.localeOf(
                context,
              ).languageCode;
              final hasValidName =
                  payload.name.has(currentLocale) || payload.name.has('en');

              if (!hasValidName) {
                if (payload.id.isNotEmpty) {
                  return Text(
                    l10n.workflowNameMissingError,
                    overflow: TextOverflow.ellipsis,
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      color: Theme.of(context).colorScheme.error,
                    ),
                  );
                }
                return Text(
                  l10n.workflowEditTitle,
                  overflow: TextOverflow.ellipsis,
                );
              }

              final titleStr = payload.name.get(currentLocale);
              return Text(titleStr, overflow: TextOverflow.ellipsis);
            },
          ),
          actions: [
            if (payload.id.isNotEmpty) ...[
              IconButton(
                mouseCursor: SystemMouseCursors.click,
                onPressed: () => _cloneWorkflow(context, ref, payload),
                icon: const Icon(Icons.content_copy),
                tooltip: l10n.workflowCloneBtn,
              ),
              IconButton(
                mouseCursor: SystemMouseCursors.click,
                onPressed: () => _deleteWorkflow(context, ref, deleteMutation),
                icon: Icon(
                  Icons.delete,
                  color: Theme.of(context).colorScheme.error,
                ),
                tooltip: l10n.delete,
              ),
            ],
            IconButton(
              mouseCursor: SystemMouseCursors.click,
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
                      width: AppSpacing.s16,
                      height: AppSpacing.s16,
                      child: CircularProgressIndicator(
                        strokeWidth: AppSpacing.s2,
                      ),
                    )
                  : Icon(
                      Icons.bug_report,
                      color: Theme.of(context).colorScheme.primary,
                    ),
              tooltip: l10n.validateDagBtn,
            ),
            TextButton.icon(
              style: TextButton.styleFrom(
                enabledMouseCursor: SystemMouseCursors.click,
              ),
              onPressed: saveWorkflow,
              icon: const Icon(Icons.save),
              label: Text(l10n.studioSaveButton),
            ),
            AppSpacing.w16,
          ],
          bottom: TabBar(
            tabs: [
              Tab(
                icon: const Icon(Icons.settings),
                text: l10n.workflowTabGeneral,
              ),
              Tab(icon: const Icon(Icons.input), text: l10n.workflowTabInputs),
              Tab(
                icon: const Icon(Icons.account_tree),
                text: l10n.workflowTabSteps,
              ),
              Tab(
                icon: const Icon(Icons.balance),
                text: l10n.workflowTabStrictness,
              ),
            ],
          ),
        ),
        body: Align(
          alignment: Alignment.topCenter,
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 1200),
            child: Column(
              children: [
                if (simulationBanner.value != null) ...[
                  MaterialBanner(
                    content: Text(
                      simulationBanner.value!.valid
                          ? l10n.simulatorValidDag
                          : l10n.simulatorDagErrors(
                              simulationBanner.value!.errors.join(', '),
                            ),
                    ),
                    backgroundColor: simulationBanner.value!.valid
                        ? Theme.of(context).colorScheme.primaryContainer
                        : Theme.of(context).colorScheme.errorContainer,
                    contentTextStyle: Theme.of(context).textTheme.bodyMedium
                        ?.copyWith(
                          color: simulationBanner.value!.valid
                              ? Theme.of(context).colorScheme.onPrimaryContainer
                              : Theme.of(context).colorScheme.onErrorContainer,
                        ),
                    actions: [
                      TextButton(
                        style: TextButton.styleFrom(
                          enabledMouseCursor: SystemMouseCursors.click,
                        ),
                        onPressed: () => simulationBanner.value = null,
                        child: Text(l10n.cancelButton),
                      ),
                    ],
                  ),
                ],
                Expanded(
                  child: TabBarView(
                    children: [
                      WorkflowGeneralTab(
                        workflow: payload,
                        idController: idController,
                        slugController: slugController,
                        onChanged: triggerUpdate,
                      ),
                      WorkflowInputsTab(
                        workflow: payload,
                        onChanged: triggerUpdate,
                      ),
                      WorkflowStepsTab(
                        workflow: payload,
                        blueprints: blueprints,
                        mcpGateways: mcpGateways,
                        onChanged: triggerUpdate,
                      ),
                      WorkflowStrictnessTab(
                        workflow: payload,
                        onChanged: triggerUpdate,
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
