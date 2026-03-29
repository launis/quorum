import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:client_app/core/state/mutation.dart';
import 'package:client_app/features/studio/controllers/studio_controller.dart';
import 'package:client_app/utils/safe_cast.dart';
import 'package:client_app/features/studio/utils/workflow_cloner.dart';
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
class WorkflowBuilderView extends HookConsumerWidget {
  final String? id;
  final String? slug;
  final Map<String, dynamic>? initialData;

  const WorkflowBuilderView({super.key, this.id, this.slug, this.initialData});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final wfId = (id ?? '').isEmpty ? 'new' : id!;

    final formState = ref.watch(workflowFormProvider(wfId));
    final stepsAsync = ref.watch(stepsControllerProvider);
    final mcpGatewaysAsync = ref.watch(mcpGatewaysControllerProvider);

    return formState.when(
      loading:
          () => Scaffold(
            appBar: AppBar(title: Text(l10n.workflowEditTitle)),
            body: const Center(child: CircularProgressIndicator()),
          ),
      error:
          (e, st) => Scaffold(
            appBar: AppBar(title: Text(l10n.workflowEditTitle)),
            body: ErrorView(
              error: e,
              stackTrace: st,
              compact: false,
              onRetry: () => ref.invalidate(workflowFormProvider(wfId)),
            ),
          ),
      data: (payload) {
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
          payload: payload,
          initialData: initialData,
          blueprints: stepsAsync.value!,
          mcpGateways: mcpGatewaysAsync.value ?? [],
          l10n: l10n,
        );
      },
    );
  }
}

class _BuilderScaffoldWrapper extends HookConsumerWidget {
  final String wfId;
  final Map<String, dynamic> payload;
  final Map<String, dynamic>? initialData;
  final List<Map<String, dynamic>> blueprints;
  final List<Map<String, dynamic>> mcpGateways;
  final AppLocalizations l10n;

  const _BuilderScaffoldWrapper({
    required this.wfId,
    required this.payload,
    this.initialData,
    required this.blueprints,
    required this.mcpGateways,
    required this.l10n,
  });

  void _cloneWorkflow(
    BuildContext context,
    WidgetRef ref,
    Map<String, dynamic> currentPayload,
  ) {
    showDialog(
      context: context,
      builder:
          (ctx) => AlertDialog(
            title: Text(l10n.workflowCloneBtn),
            content: Text(l10n.workflowSharedBlueprintWarning),
            actions: [
              TextButton(
                onPressed: () => Navigator.of(ctx).pop(),
                child: Text(l10n.cancel),
              ),
              FilledButton(
                onPressed: () {
                  Navigator.of(ctx).pop();
                  try {
                    final original = Map<String, dynamic>.from(currentPayload);
                    final cloned = WorkflowCloner.cloneDeep(original);

                    final nameMap = SafeCast.safeMap(cloned['name']);
                    if (nameMap.containsKey('translations')) {
                      final translations = SafeCast.safeMap(
                        nameMap['translations'],
                      );
                      if (translations.containsKey('en')) {
                        translations['en'] = "Copy of ${translations['en']}";
                      }
                      if (translations.containsKey('fi')) {
                        translations['fi'] = "Kopio - ${translations['fi']}";
                      }
                      nameMap['translations'] = translations;
                      cloned['name'] = nameMap;
                    }

                    Navigator.of(context).pushReplacement(
                      MaterialPageRoute(
                        builder:
                            (context) => WorkflowBuilderView(
                              initialData: cloned,
                              id: 'new',
                            ),
                      ),
                    );

                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text(l10n.workflowCloneSuccess)),
                    );
                  } catch (e) {
                    final errorMsg =
                        e is AppException
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
    final idStr = payload['id']?.toString() ?? '';
    if (idStr.isEmpty) return;

    showDialog(
      context: context,
      builder:
          (ctx) => AlertDialog(
            title: Text(l10n.workflowDeleteConfirmTitle),
            content: Text(l10n.workflowDeleteConfirmDesc(idStr)),
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
    final idController = useTextEditingController(
      text: SafeCast.safeString(payload['id']),
    );
    final slugController = useTextEditingController(
      text: SafeCast.safeString(payload['slug']),
    );

    // Hydrate initialData exactly once if it's a clone/new process
    useEffect(() {
      if (initialData != null && initialData!.isNotEmpty && wfId == 'new') {
        final currentId = SafeCast.safeString(payload['id']);
        if (currentId.isEmpty && initialData!.containsKey('name')) {
          Future.microtask(() {
            payload.addAll(initialData!);
            idController.text = SafeCast.safeString(payload['id']);
            slugController.text = SafeCast.safeString(payload['slug']);
            ref.read(workflowFormProvider(wfId).notifier).forceRebuild();
          });
        }
      }
      return null;
    }, const []);

    final validateMutation = useMutation<Map<String, dynamic>>(
      onSuccess: (data) {
        if (context.mounted) {
          final isValid = data['valid'] == true;
          final errors = SafeCast.safeList(data['errors']);
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(
                isValid
                    ? l10n.simulatorValidDag
                    : l10n.simulatorDagErrors(errors.join(', ')),
              ),
              backgroundColor:
                  isValid
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

      payload['id'] = id;
      if (slug.isNotEmpty) {
        payload['slug'] = slug;
      } else {
        payload.remove('slug');
      }

      try {
        await ref.read(workflowFormProvider(wfId).notifier).submit(payload);
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(l10n.workflowSavedSuccess),
              backgroundColor: const Color(0xFF2E7D32),
            ),
          );
          context.pop();
        }
      } catch (e) {
        if (context.mounted) {
          final errorMsg =
              e is AppException
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

    void triggerUpdate() {
      ref.read(workflowFormProvider(wfId).notifier).forceRebuild();
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
                final nameObj = SafeCast.safeMap(payload['name']);
                final translations = SafeCast.safeMap(nameObj['translations']);
                final titleStr = translations['fi'] ?? translations['en'];

                if (titleStr == null &&
                    payload['id'] != null &&
                    payload['id'].toString().isNotEmpty) {
                  throw AppException.validation(l10n.workflowNameMissingError);
                }
                return Text(titleStr?.toString() ?? l10n.workflowEditTitle);
              },
            ),
            actions: [
              if (payload['id']?.toString().isNotEmpty == true) ...[
                IconButton(
                  onPressed: () => _cloneWorkflow(context, ref, payload),
                  icon: const Icon(Icons.content_copy),
                  tooltip: l10n.workflowCloneBtn,
                ),
                IconButton(
                  onPressed:
                      () => _deleteWorkflow(context, ref, deleteMutation),
                  icon: Icon(
                    Icons.delete,
                    color: Theme.of(context).colorScheme.error,
                  ),
                  tooltip: l10n.delete,
                ),
              ],
              IconButton(
                onPressed:
                    validateMutation.isLoading
                        ? null
                        : () {
                          validateMutation.mutate(() async {
                            return await ref
                                .read(workflowsControllerProvider.notifier)
                                .simulateWorkflow(payload);
                          });
                        },
                icon:
                    validateMutation.isLoading
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
