import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:client_app/core/state/mutation.dart';
import 'package:client_app/features/studio/controllers/studio_controller.dart';
import 'package:client_app/router/router.dart';
import 'package:client_app/features/studio/views/widgets/i18n_text_field.dart';
import 'package:client_app/features/studio/views/widgets/expected_input_editor_box.dart';
import 'package:client_app/utils/safe_cast.dart';
import 'package:client_app/features/studio/utils/workflow_cloner.dart';
import 'package:client_app/core/error/app_error_ext.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/features/studio/views/widgets/dag_canvas_view.dart';
import 'package:client_app/features/studio/views/widgets/inspector_pane.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/ui/error_view.dart';

/// **Workflow DAG Builder**
///
/// CRUD interface for managing Semantic Routing & DAG structures.
/// Admin can define global inputs (`expected_inputs`) and sequence
/// processing steps (`steps`) including `depends_on` and `input_mappings`.
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
  String? _selectedNodeId;

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

  void _addExpectedInput() {
    setState(() {
      final inputs = SafeCast.safeList(_editableWorkflow['expected_inputs']);
      inputs.add({
        'input_key': 'new_input_key',
        'label': {
          'default_locale': 'en',
          'translations': {'en': ''},
        },
        'description': {
          'default_locale': 'en',
          'translations': {'en': ''},
        },
        'ai_description': {
          'default_locale': 'en',
          'translations': {'en': ''},
        },
        'required': false,
        'is_chat_history': false,
        'input_modes': ['file'],
        'questionnaire_definition': [],
      });
      _editableWorkflow['expected_inputs'] = inputs;
    });
  }

  void _addStep() {
    setState(() {
      final steps = SafeCast.safeList(_editableWorkflow['steps']);
      steps.add({
        'id': 'step_${steps.length + 1}',
        'task_blueprint': '',
        'depends_on': <String>[],
        'input_mappings': <String, dynamic>{'inputs': '\$inputs'},
      });
      _editableWorkflow['steps'] = steps;
    });
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
                        translations['en'] = 'Copy of ${translations['en']}';
                      }
                      if (translations.containsKey('fi')) {
                        translations['fi'] = 'Kopio - ${translations['fi']}';
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

    // Absolute Fail-Fast: Do not use `?? []` to mask data loading or corruption.
    if (stepsAsync.hasError) throw stepsAsync.error!;
    if (!stepsAsync.hasValue) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }
    final stepsList = stepsAsync.value!;

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
              content: Text('${l10n.errorUnknown}: $errorMsg'),
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
                isValid ? 'DAG is Valid!' : 'DAG Errors: ${errors.join(', ')}',
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

    return Scaffold(
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
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Metadata
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        l10n.workflowConfigTitle,
                        style: const TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 16),
                      TextField(
                        controller: _idController,
                        decoration: InputDecoration(
                          labelText: l10n.workflowIdLabel,
                          border: const OutlineInputBorder(),
                        ),
                        enabled:
                            widget.workflow['id'] == null ||
                            widget.workflow['id'].toString().isEmpty,
                      ),
                      const SizedBox(height: 16),
                      TextField(
                        controller: _slugController,
                        decoration: InputDecoration(
                          // Fallback to English if generation fails during dev
                          labelText:
                              (l10n as dynamic).workflowSlugLabel ??
                              'Workflow Slug (URL Path)',
                          border: const OutlineInputBorder(),
                        ),
                        onChanged: (val) => _editableWorkflow['slug'] = val,
                      ),
                      const SizedBox(height: 16),
                      I18nTextField(
                        label: l10n.workflowNameLabel,
                        initialData: SafeCast.safeMap(
                          _editableWorkflow['name'],
                        ),
                        onChanged: (val) => _editableWorkflow['name'] = val,
                      ),
                      const SizedBox(height: 16),
                      DropdownButtonFormField<String>(
                        initialValue: SafeCast.safeString(
                          _editableWorkflow['model_strategy'],
                          'fast',
                        ),
                        decoration: const InputDecoration(
                          labelText: 'Model Strategy (Cost/Cognition Profile)',
                          border: OutlineInputBorder(),
                        ),
                        items: const [
                          DropdownMenuItem(
                            value: 'fast',
                            child: Text('Fast (o3-mini / GPT-4o-mini)'),
                          ),
                          DropdownMenuItem(
                            value: 'deep',
                            child: Text('Deep (GPT-4o / Claude 3.5)'),
                          ),
                          DropdownMenuItem(
                            value: 'strict',
                            child: Text('Strict (O1)'),
                          ),
                          DropdownMenuItem(
                            value: 'precise',
                            child: Text('Precise (O3-mini-high)'),
                          ),
                        ],
                        onChanged: (val) {
                          if (val != null) {
                            setState(
                              () => _editableWorkflow['model_strategy'] = val,
                            );
                          }
                        },
                      ),
                    ],
                  ),
                ),
              ),

              const SizedBox(height: 16),

              // Output Mapping (MVC Rules)
              Text(
                l10n.blueprintTabTitle, // Keep translation key active
                style: const TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 16),
              Card(
                color: Theme.of(context).colorScheme.surfaceContainerHighest,
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Text(
                            'Report Output Profiles (V2)',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                          IconButton.filled(
                            onPressed: () {
                              ProfileEditorRoute(
                                workflowSlug: SafeCast.safeString(
                                  _editableWorkflow['id'],
                                ),
                              ).push(context);
                            },
                            icon: const Icon(Icons.edit_document),
                            tooltip: 'Manage Output Profiles',
                            padding: const EdgeInsets.symmetric(
                              horizontal: 24,
                              vertical: 12,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 16),
                      Builder(
                        builder: (context) {
                          final outputProfiles = SafeCast.safeMap(
                            _editableWorkflow['output_profiles'],
                          );
                          final profileKeys = outputProfiles.keys.toList();
                          if (profileKeys.isEmpty) profileKeys.add('default');

                          final currentDefault = SafeCast.safeString(
                            _editableWorkflow['default_profile_id'],
                            'default',
                          );
                          final safeDefault =
                              profileKeys.contains(currentDefault)
                                  ? currentDefault
                                  : profileKeys.first;

                          return DropdownButtonFormField<String>(
                            initialValue: safeDefault,
                            decoration: const InputDecoration(
                              labelText: 'Default Fallback Profile',
                              border: OutlineInputBorder(),
                              isDense: true,
                            ),
                            items:
                                profileKeys.map((key) {
                                  final profileData = SafeCast.safeMap(
                                    outputProfiles[key],
                                  );
                                  final nameMap = SafeCast.safeMap(
                                    profileData['name'],
                                  );
                                  final title =
                                      nameMap['fi'] ?? nameMap['en'] ?? key;
                                  return DropdownMenuItem(
                                    value: key,
                                    child: Text('$title ($key)'),
                                  );
                                }).toList(),
                            onChanged: (val) {
                              if (val != null) {
                                setState(() {
                                  _editableWorkflow['default_profile_id'] = val;
                                });
                              }
                            },
                          );
                        },
                      ),
                    ],
                  ),
                ),
              ),

              const SizedBox(height: 24),

              // Expected Inputs
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    l10n.workflowInputsTitle,
                    style: const TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  OutlinedButton.icon(
                    onPressed: _addExpectedInput,
                    icon: const Icon(Icons.add),
                    label: Text(l10n.workflowAddInputBtn),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              ...SafeCast.safeList(
                _editableWorkflow['expected_inputs'],
              ).asMap().entries.map((entry) {
                return _buildInputCard(
                  entry.key,
                  SafeCast.safeMap(entry.value),
                  l10n,
                );
              }),

              // DAG Steps Canvas (V2 V3 Architecture)
              const SizedBox(height: 16),
              Container(
                height: 600,
                decoration: BoxDecoration(
                  border: Border.all(color: Colors.grey.shade300),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    Expanded(
                      flex: 3,
                      child: DagCanvasView(
                        workflow: _editableWorkflow,
                        onNodeSelected:
                            (id) => setState(() => _selectedNodeId = id),
                        onWorkflowUpdated:
                            (updated) =>
                                setState(() => _editableWorkflow = updated),
                      ),
                    ),
                    const VerticalDivider(width: 1),
                    InspectorPane(
                      selectedStepId: _selectedNodeId,
                      workflow: _editableWorkflow,
                      availableBlueprints: stepsList,
                      onStepUpdated: (id, mutatedStep) {
                        setState(() {
                          final steps = SafeCast.safeList(
                            _editableWorkflow['steps'],
                          );
                          final i = steps.indexWhere((s) {
                            final sMap = SafeCast.safeMap(s);
                            final cId = SafeCast.safeString(
                              sMap['id'],
                              sMap['step_id'],
                            );
                            return cId == id;
                          });
                          if (i >= 0) steps[i] = mutatedStep;
                          _editableWorkflow['steps'] = steps;
                        });
                      },
                      onAddStep: _addStep,
                      onDeleteStep: (id) {
                        setState(() {
                          final steps = SafeCast.safeList(
                            _editableWorkflow['steps'],
                          );
                          steps.removeWhere((s) {
                            final sMap = SafeCast.safeMap(s);
                            final cId = SafeCast.safeString(
                              sMap['id'],
                              sMap['step_id'],
                            );
                            return cId == id;
                          });
                          _editableWorkflow['steps'] = steps;
                          _selectedNodeId = null;
                        });
                      },
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildInputCard(
    int index,
    Map<String, dynamic> inputDef,
    AppLocalizations l10n,
  ) {
    return ExpectedInputEditorBox(
      inputDef: inputDef,
      onDelete: () {
        setState(() {
          SafeCast.safeList(
            _editableWorkflow['expected_inputs'],
          ).removeAt(index);
        });
      },
      onChanged: () {
        setState(() {
          // Trigger rebuild if necessary deep within
        });
      },
    );
  }
}
