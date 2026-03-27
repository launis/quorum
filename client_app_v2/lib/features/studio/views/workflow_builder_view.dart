import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:client_app/core/state/mutation.dart';
import 'package:client_app/features/studio/controllers/studio_controller.dart';
import 'package:client_app/utils/safe_cast.dart';
import 'package:client_app/features/studio/utils/workflow_cloner.dart';
import 'package:client_app/core/error/app_error_ext.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/features/studio/controllers/mcp_gateways_controller.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/ui/error_view.dart';

import 'widgets/workflow/workflow_general_tab.dart';
import 'widgets/workflow/workflow_inputs_tab.dart';
import 'widgets/workflow/workflow_steps_tab.dart';

/// **Workflow DAG Builder**
///
/// CRUD interface for managing Semantic Routing & DAG structures.
/// Admin can define global inputs (`expected_inputs`) and sequence
/// processing steps (`steps`) including `depends_on` and `input_mappings`.
/// Componentized to enforce Flat MVC architecture using the Sub-Tabs pattern.
class WorkflowBuilderView extends ConsumerWidget {
  final String? id;
  final String? slug;
  final Map<String, dynamic>? initialData;

  const WorkflowBuilderView({super.key, this.id, this.slug, this.initialData});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    if (initialData != null && initialData!.isNotEmpty) {
      return _WorkflowBuilderForm(workflow: initialData!);
    }
    if (id == null || id!.isEmpty || id == 'new') {
      return const _WorkflowBuilderForm(workflow: {});
    }

    final asyncData = ref.watch(workflowByIdProvider(id!));
    return asyncData.when(
      data: (wf) => _WorkflowBuilderForm(workflow: wf),
      loading:
          () =>
              const Scaffold(body: Center(child: CircularProgressIndicator())),
      error:
          (e, st) => ErrorView(
            error: e,
            stackTrace: st,
            onRetry: () => ref.invalidate(workflowByIdProvider(id!)),
          ),
    );
  }
}

class _WorkflowBuilderForm extends StatefulHookConsumerWidget {
  final Map<String, dynamic> workflow;

  const _WorkflowBuilderForm({required this.workflow});

  @override
  ConsumerState<_WorkflowBuilderForm> createState() =>
      _WorkflowBuilderFormState();
}

class _WorkflowBuilderFormState extends ConsumerState<_WorkflowBuilderForm> {
  late Map<String, dynamic> _editableWorkflow = {};
  late TextEditingController _idController;
  late TextEditingController _slugController;

  @override
  void initState() {
    super.initState();
    _editableWorkflow = Map<String, dynamic>.from(widget.workflow);
    _idController = TextEditingController(
      text: SafeCast.safeString(_editableWorkflow['id']),
    );
    _slugController = TextEditingController(
      text: SafeCast.safeString(_editableWorkflow['slug']),
    );

    if (!_editableWorkflow.containsKey('expected_inputs')) {
      _editableWorkflow['expected_inputs'] = [];
    }
    if (!_editableWorkflow.containsKey('steps')) {
      _editableWorkflow['steps'] = [];
    }

    // Drop legacy SDUI structures to prevent Pydantic Fail-Fast rejections
    _editableWorkflow.remove('render_blueprints');
    _editableWorkflow.remove('render_blueprint');
    _editableWorkflow.remove('output_mapping');

    // Ensure V2 strict output profiles dict exists
    if (!_editableWorkflow.containsKey('output_profiles')) {
      _editableWorkflow['output_profiles'] = <String, dynamic>{};
    }
  }

  @override
  void dispose() {
    _idController.dispose();
    _slugController.dispose();
    super.dispose();
  }

  void _triggerUpdate() {
    if (mounted) setState(() {});
  }

  void _cloneWorkflow(BuildContext context) {
    showDialog(
      context: context,
      builder:
          (ctx) => AlertDialog(
            title: Text(AppLocalizations.of(context)!.workflowCloneBtn),
            content: Text(
              AppLocalizations.of(context)!.workflowSharedBlueprintWarning,
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.of(ctx).pop(),
                child: Text(AppLocalizations.of(context)!.cancel),
              ),
              FilledButton(
                onPressed: () {
                  Navigator.of(ctx).pop();
                  try {
                    final original = Map<String, dynamic>.from(
                      _editableWorkflow,
                    );
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
                      SnackBar(
                        content: Text(
                          AppLocalizations.of(context)!.workflowCloneSuccess,
                        ),
                      ),
                    );
                  } catch (e) {
                    final errorMsg =
                        e is AppException
                            ? AppExceptionX.extractLocalizedHint(
                              e,
                              AppLocalizations.of(context)!,
                            )
                            : e.toString();
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text(errorMsg),
                        backgroundColor: Colors.red,
                      ),
                    );
                  }
                },
                child: Text(AppLocalizations.of(context)!.workflowCloneBtn),
              ),
            ],
          ),
    );
  }

  void _deleteWorkflow(
    BuildContext context,
    MutationState<void> deleteMutation,
  ) {
    final id = _idController.text.trim();
    if (id.isEmpty) return;

    showDialog(
      context: context,
      builder:
          (context) => AlertDialog(
            title: Text(
              AppLocalizations.of(context)!.workflowDeleteConfirmTitle,
            ),
            content: Text(
              AppLocalizations.of(context)!.workflowDeleteConfirmDesc(id),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.of(context).pop(),
                child: Text(AppLocalizations.of(context)!.cancel),
              ),
              MutationButton<void>(
                mutation: deleteMutation,
                label: AppLocalizations.of(context)!.delete,
                action: () async {
                  await ref
                      .read(workflowsControllerProvider.notifier)
                      .deleteWorkflow(id);
                },
              ),
            ],
          ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final stepsAsync = ref.watch(stepsControllerProvider);
    final mcpGatewaysAsync = ref.watch(mcpGatewaysControllerProvider);
    final mcpGateways = mcpGatewaysAsync.value ?? [];

    // Absolute Fail-Fast: Do not use `?? []` to mask data loading or corruption.
    if (stepsAsync.hasError) throw stepsAsync.error!;
    if (!stepsAsync.hasValue) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }
    final blueprints = stepsAsync.value!;

    final saveMutation = useMutation<Map<String, dynamic>>(
      onSuccess: (_) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Workflow saved successfully.')),
          );
          Navigator.of(context).pop();
        }
      },
      onError: (e) {
        if (mounted) {
          final l10n = AppLocalizations.of(context)!;
          final errorMsg = AppExceptionX.extractLocalizedHint(e, l10n);
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text("${l10n.errorUnknown}: $errorMsg"),
              backgroundColor: Colors.red,
            ),
          );
        }
      },
    );

    final validateMutation = useMutation<Map<String, dynamic>>(
      onSuccess: (data) {
        if (mounted) {
          final isValid = data['valid'] == true;
          final errors = SafeCast.safeList(data['errors']);
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(
                isValid ? 'DAG is Valid!' : "DAG Errors: ${errors.join(', ')}",
              ),
              backgroundColor: isValid ? Colors.green : Colors.red,
              duration: const Duration(seconds: 4),
            ),
          );
        }
      },
      onError: (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Simulation Error: $e'),
              backgroundColor: Colors.red,
            ),
          );
        }
      },
    );

    final deleteMutation = useMutation<void>(
      onSuccess: (_) {
        if (mounted) {
          ScaffoldMessenger.of(
            context,
          ).showSnackBar(const SnackBar(content: Text('Deleted successfully')));
          Navigator.of(context).pop();
        }
      },
      onError: (e) {
        if (mounted) {
          final l10n = AppLocalizations.of(context)!;
          final errorMsg = AppExceptionX.extractLocalizedHint(e, l10n);
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text(errorMsg), backgroundColor: Colors.red),
          );
        }
      },
    );

    return DefaultTabController(
      length: 3,
      child: Scaffold(
        appBar: AppBar(
          leading: IconButton(
            icon: const Icon(Icons.arrow_back),
            tooltip: 'Back to Studio',
            onPressed: () => context.go('/admin'),
          ),
          title: Builder(
            builder: (context) {
              final nameObj = SafeCast.safeMap(widget.workflow['name']);
              final translations = SafeCast.safeMap(nameObj['translations']);
              final titleStr = translations['fi'] ?? translations['en'];

              // New workflows might legitimately not have a name yet, but if it has an ID, the name MUST exist.
              if (titleStr == null && widget.workflow['id'] != null) {
                throw AppException.validation(
                  'Workflow name is missing for existing workflow.',
                );
              }
              return Text(titleStr?.toString() ?? l10n.workflowEditTitle);
            },
          ),
          actions: [
            if (widget.workflow['id']?.toString().isNotEmpty == true) ...[
              IconButton(
                onPressed: () => _cloneWorkflow(context),
                icon: const Icon(Icons.content_copy),
                tooltip: l10n.workflowCloneBtn,
              ),
              IconButton(
                onPressed: () => _deleteWorkflow(context, deleteMutation),
                icon: const Icon(Icons.delete, color: Colors.red),
                tooltip: 'Delete',
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
                              .simulateWorkflow(_editableWorkflow);
                        });
                      },
              icon:
                  validateMutation.isLoading
                      ? const SizedBox(
                        width: 16,
                        height: 16,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                      : const Icon(Icons.bug_report, color: Colors.green),
              tooltip: 'Validate DAG',
            ),
            MutationButton<Map<String, dynamic>>(
              mutation: saveMutation,
              label: 'Save',
              icon: Icons.save,
              action: () async {
                final id = _idController.text.trim();
                final slug = _slugController.text.trim();
                if (id.isEmpty) {
                  throw AppException.validation('ID is required');
                }
                _editableWorkflow['id'] = id;
                if (slug.isNotEmpty) {
                  _editableWorkflow['slug'] = slug;
                } else {
                  _editableWorkflow.remove('slug');
                }
                return ref
                    .read(workflowsControllerProvider.notifier)
                    .saveWorkflow(id, _editableWorkflow);
              },
            ),
            const SizedBox(width: 16),
          ],
          bottom: const TabBar(
            tabs: [
              Tab(icon: Icon(Icons.settings), text: '1. Yleiset & Tulosteet'),
              Tab(icon: Icon(Icons.input), text: '2. Syötteet'),
              Tab(
                icon: Icon(Icons.account_tree),
                text: '3. Stepit & Riippuvuudet',
              ),
            ],
          ),
        ),
        body: TabBarView(
          children: [
            WorkflowGeneralTab(
              workflow: _editableWorkflow,
              idController: _idController,
              slugController: _slugController,
              onChanged: _triggerUpdate,
            ),
            WorkflowInputsTab(
              workflow: _editableWorkflow,
              onChanged: _triggerUpdate,
            ),
            WorkflowStepsTab(
              workflow: _editableWorkflow,
              blueprints: blueprints,
              mcpGateways: mcpGateways,
              onChanged: _triggerUpdate,
            ),
          ],
        ),
      ),
    );
  }
}
