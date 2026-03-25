import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
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
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/ui/error_view.dart';

/// **Workflow DAG Builder**
///
/// CRUD interface for managing Semantic Routing & DAG structures.
/// Admin can define global inputs (`expected_inputs`) and sequence
/// processing steps (`steps`) including `depends_on` and `input_mappings`.
class WorkflowBuilderView extends ConsumerWidget {
  final String? slug;
  final Map<String, dynamic>? initialData;

  const WorkflowBuilderView({super.key, this.slug, this.initialData});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    if (initialData != null && initialData!.isNotEmpty) {
      return _WorkflowBuilderForm(workflow: initialData!);
    }
    if (slug == null || slug!.isEmpty || slug == 'new') {
      return const _WorkflowBuilderForm(workflow: {});
    }

    final asyncData = ref.watch(workflowBySlugProvider(slug!));
    return asyncData.when(
      data: (wf) => _WorkflowBuilderForm(workflow: wf),
      loading:
          () =>
              const Scaffold(body: Center(child: CircularProgressIndicator())),
      error:
          (e, st) => ErrorView(
            error: e,
            stackTrace: st,
            onRetry: () => ref.invalidate(workflowBySlugProvider(slug!)),
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
                              slug: 'new',
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
    final stepsList = stepsAsync.value ?? [];

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
        title: Text(
          (SafeCast.safeMap(widget.workflow['name'])['translations']
                  as Map?)?['fi'] ??
              (SafeCast.safeMap(widget.workflow['name'])['translations']
                  as Map?)?['en'] ??
              l10n.workflowEditTitle,
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

              const SizedBox(height: 24),

              // DAG Steps
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    l10n.workflowStepsTitle,
                    style: const TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  OutlinedButton.icon(
                    onPressed: _addStep,
                    icon: const Icon(Icons.add),
                    label: Text(l10n.workflowAddStepBtn),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              ...SafeCast.safeList(
                _editableWorkflow['steps'],
              ).asMap().entries.map((entry) {
                return _buildStepCard(
                  entry.key,
                  SafeCast.safeMap(entry.value),
                  l10n,
                  stepsList,
                );
              }),
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

  Widget _buildStepCard(
    int index,
    Map<String, dynamic> stepDef,
    AppLocalizations l10n,
    List<Map<String, dynamic>> stepsList,
  ) {
    final rawId = stepDef['id'];
    final rawStepId = stepDef['step_id'];
    final stepIdController = TextEditingController(
      text: SafeCast.safeString(rawId != null ? rawId : rawStepId),
    );
    final dependsOn =
        SafeCast.safeList(
          stepDef['depends_on'],
        ).map((e) => e.toString()).toList();
    final mappings = SafeCast.safeMap(stepDef['input_mappings']);

    final previousSteps =
        SafeCast.safeList(_editableWorkflow['steps'])
            .take(index)
            .map((s) {
              final sm = SafeCast.safeMap(s);
              final id = sm['id'];
              return SafeCast.safeString(id != null ? id : sm['step_id']);
            })
            .where((s) => s.isNotEmpty)
            .toList();

    final availableSources = <String>[
      '\$inputs',
      ...SafeCast.safeList(_editableWorkflow['expected_inputs'])
          .map((e) {
            final key = SafeCast.safeString(SafeCast.safeMap(e)['input_key']);
            return key.isNotEmpty ? '\$inputs.$key' : '';
          })
          .where((s) => s.isNotEmpty),
      ...previousSteps.map((s) => '\$steps.$s.outputs'),
    ];

    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Step ${index + 1}',
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.delete, color: Colors.red),
                  onPressed: () {
                    setState(() {
                      SafeCast.safeList(
                        _editableWorkflow['steps'],
                      ).removeAt(index);
                    });
                  },
                ),
              ],
            ),
            const Divider(),

            Row(
              children: [
                Expanded(
                  child: Focus(
                    onFocusChange: (f) {
                      if (!f) stepDef['id'] = stepIdController.text;
                    },
                    child: TextField(
                      controller: stepIdController,
                      decoration: InputDecoration(
                        labelText: l10n.workflowStepIdLabel,
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: DropdownButtonFormField<String>(
                    decoration: const InputDecoration(
                      labelText: 'Step (Logical Block)',
                    ),
                    initialValue:
                        stepsList.any(
                              (bp) => bp['slug'] == stepDef['task_blueprint'],
                            )
                            ? stepDef['task_blueprint'] as String?
                            : null,
                    items:
                        stepsList.map((bp) {
                          final slug = SafeCast.safeString(bp['slug']);
                          final nameMap = SafeCast.safeMap(bp['name']);
                          final enName = SafeCast.safeString(nameMap['en']);
                          final label = enName.isNotEmpty ? enName : slug;
                          return DropdownMenuItem(
                            value: slug,
                            child: Text(label),
                          );
                        }).toList(),
                    onChanged:
                        (val) =>
                            setState(() => stepDef['task_blueprint'] = val),
                  ),
                ),
              ],
            ),

            const SizedBox(height: 16),
            Text(
              l10n.workflowDependsOnLabel,
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
            Wrap(
              spacing: 8,
              children:
                  previousSteps.map((prevStepId) {
                    final isSelected = dependsOn.contains(prevStepId);
                    return FilterChip(
                      label: Text(prevStepId),
                      selected: isSelected,
                      onSelected: (selected) {
                        setState(() {
                          if (selected) {
                            dependsOn.add(prevStepId);
                          } else {
                            dependsOn.remove(prevStepId);
                          }
                          stepDef['depends_on'] = dependsOn;
                        });
                      },
                    );
                  }).toList(),
            ),
            if (previousSteps.isEmpty)
              Text(
                l10n.workflowNoPrevSteps,
                style: const TextStyle(
                  fontStyle: FontStyle.italic,
                  color: Colors.grey,
                ),
              ),

            const SizedBox(height: 16),
            Row(
              children: [
                Text(
                  l10n.workflowInputMappingsLabel,
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
                IconButton(
                  icon: const Icon(Icons.info_outline, size: 20),
                  onPressed: () {
                    showDialog(
                      context: context,
                      builder:
                          (ctx) => AlertDialog(
                            title: Text(
                              // Using hardcoded fallback just in case, but prefer generated l10n
                              (l10n as dynamic).workflowMappingHelperTitle ??
                                  'How does Semantic Routing work?',
                            ),
                            content: Text(
                              (l10n as dynamic).workflowMappingHelperDesc ??
                                  '1. Left side (Agent Input Key) is the XML tag name the AI will use to read the data. Just type "inputs" (snake_case).\n2. Right side is the Data Source. "\$inputs" gets user data, "\$steps.step_x.outputs" connects previous agents.\nTo pass hardcoded text, type without the \$ sign.',
                            ),
                            actions: [
                              TextButton(
                                onPressed: () => Navigator.of(ctx).pop(),
                                child: Text(l10n.close),
                              ),
                            ],
                          ),
                    );
                  },
                ),
              ],
            ),
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.surfaceContainerHighest,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Column(
                children: [
                  ...mappings.entries.map((m) {
                    final targetCtrl = TextEditingController(text: m.key);
                    final sourceCtrl = TextEditingController(
                      text: m.value.toString(),
                    );
                    return Padding(
                      padding: const EdgeInsets.only(bottom: 8.0),
                      child: Row(
                        children: [
                          Expanded(
                            child: Focus(
                              onFocusChange: (f) {
                                if (!f &&
                                    targetCtrl.text.isNotEmpty &&
                                    sourceCtrl.text.isNotEmpty) {
                                  mappings.remove(m.key);
                                  mappings[targetCtrl.text] = sourceCtrl.text;
                                  stepDef['input_mappings'] = mappings;
                                }
                              },
                              child: TextField(
                                controller: targetCtrl,
                                decoration: InputDecoration(
                                  labelText: l10n.workflowAgentInputKey,
                                  isDense: true,
                                ),
                                inputFormatters: [
                                  FilteringTextInputFormatter.allow(
                                    RegExp(r'[a-z0-9_]'),
                                  ),
                                ],
                              ),
                            ),
                          ),
                          const Padding(
                            padding: EdgeInsets.symmetric(horizontal: 8.0),
                            child: Icon(Icons.arrow_back),
                          ),
                          Expanded(
                            child: Autocomplete<String>(
                              initialValue: TextEditingValue(
                                text: sourceCtrl.text,
                              ),
                              optionsBuilder: (textEditingValue) {
                                if (textEditingValue.text.isEmpty) {
                                  return availableSources;
                                }
                                return availableSources.where(
                                  (opt) => opt.toLowerCase().contains(
                                    textEditingValue.text.toLowerCase(),
                                  ),
                                );
                              },
                              onSelected: (selection) {
                                setState(() {
                                  sourceCtrl.text = selection;
                                  mappings[targetCtrl.text] = selection;
                                  stepDef['input_mappings'] = mappings;

                                  // Dependency Guard Logic
                                  if (selection.startsWith('\$steps.')) {
                                    final parts = selection.split('.');
                                    if (parts.length > 1) {
                                      final stepId = parts[1];
                                      if (!dependsOn.contains(stepId) &&
                                          previousSteps.contains(stepId)) {
                                        dependsOn.add(stepId);
                                        stepDef['depends_on'] = dependsOn;
                                      }
                                    }
                                  }
                                });
                              },
                              fieldViewBuilder: (
                                context,
                                textEditingController,
                                focusNode,
                                onFieldSubmitted,
                              ) {
                                return Focus(
                                  onFocusChange: (f) {
                                    if (!f &&
                                        targetCtrl.text.isNotEmpty &&
                                        textEditingController.text.isNotEmpty) {
                                      mappings[targetCtrl.text] =
                                          textEditingController.text;
                                      stepDef['input_mappings'] = mappings;

                                      // Dependency Guard Logic
                                      final sel = textEditingController.text;
                                      if (sel.startsWith('\$steps.')) {
                                        final parts = sel.split('.');
                                        if (parts.length > 1) {
                                          final stepId = parts[1];
                                          if (!dependsOn.contains(stepId) &&
                                              previousSteps.contains(stepId)) {
                                            setState(() {
                                              dependsOn.add(stepId);
                                              stepDef['depends_on'] = dependsOn;
                                            });
                                          }
                                        }
                                      }
                                    }
                                  },
                                  child: TextField(
                                    controller: textEditingController,
                                    focusNode: focusNode,
                                    decoration: InputDecoration(
                                      labelText: l10n.workflowSourceVarLabel,
                                      isDense: true,
                                    ),
                                  ),
                                );
                              },
                            ),
                          ),
                          IconButton(
                            icon: const Icon(
                              Icons.remove_circle,
                              color: Colors.red,
                            ),
                            onPressed: () {
                              setState(() {
                                mappings.remove(m.key);
                                stepDef['input_mappings'] = mappings;
                              });
                            },
                          ),
                        ],
                      ),
                    );
                  }),
                  TextButton.icon(
                    onPressed: () {
                      setState(() {
                        mappings['new_input_key_${mappings.length}'] =
                            '\$inputs.';
                        stepDef['input_mappings'] = mappings;
                      });
                    },
                    icon: const Icon(Icons.add_link),
                    label: Text(l10n.workflowAddMappingBtn),
                  ),
                ],
              ),
            ),

            // MCP Tool — single toggle per StepRule
            const SizedBox(height: 16),
            SwitchListTile(
              title: Text(l10n.stepBuilderMCPToolsTitle),
              subtitle: Text(l10n.stepBuilderToolHint),
              secondary: Icon(Icons.travel_explore, color: Colors.teal.shade700),
              value: SafeCast.safeList(stepDef['allowed_mcp_tools']).isNotEmpty,
              onChanged: (enabled) {
                setState(() {
                  if (enabled) {
                    stepDef['allowed_mcp_tools'] = ['mcp_tavily_search'];
                  } else {
                    stepDef['allowed_mcp_tools'] = <String>[];
                  }
                });
              },
            ),
          ],
        ),
      ),
    );
  }
}
