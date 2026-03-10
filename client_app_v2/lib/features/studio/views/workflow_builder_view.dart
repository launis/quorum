import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/studio/controllers/studio_controller.dart';
import 'package:client_app/features/studio/views/widgets/i18n_text_field.dart';
import 'package:client_app/utils/safe_cast.dart';
import 'package:client_app/core/error/app_error.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

/// **Workflow DAG Builder**
///
/// CRUD interface for managing Semantic Routing & DAG structures.
/// Admin can define global inputs (`expected_inputs`) and sequence
/// processing steps (`steps`) including `depends_on` and `input_mappings`.
class WorkflowBuilderView extends ConsumerStatefulWidget {
  final Map<String, dynamic> workflow;

  const WorkflowBuilderView({super.key, required this.workflow});

  @override
  ConsumerState<WorkflowBuilderView> createState() =>
      _WorkflowBuilderViewState();
}

class _WorkflowBuilderViewState extends ConsumerState<WorkflowBuilderView> {
  late Map<String, dynamic> _editableWorkflow;
  late TextEditingController _idController;

  @override
  void initState() {
    super.initState();
    _editableWorkflow = Map<String, dynamic>.from(widget.workflow);
    _idController = TextEditingController(
      text: SafeCast.safeString(_editableWorkflow['id']),
    );

    if (!_editableWorkflow.containsKey('expected_inputs')) {
      _editableWorkflow['expected_inputs'] = [];
    }
    if (!_editableWorkflow.containsKey('steps')) {
      _editableWorkflow['steps'] = [];
    }
  }

  @override
  void dispose() {
    _idController.dispose();
    super.dispose();
  }

  void _saveWorkflow() {
    final id = _idController.text.trim();
    if (id.isEmpty) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('ID is required.')));
      return;
    }

    _editableWorkflow['id'] = id;

    ref
        .read(workflowsControllerProvider.notifier)
        .saveWorkflow(id, _editableWorkflow)
        .then((_) {
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('Workflow saved (Optimistic update applied).'),
              ),
            );
            Navigator.of(context).pop();
          }
        })
        .catchError((e) {
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text('Failed to save: $e'),
                backgroundColor: Colors.red,
              ),
            );
          }
        });
  }

  void _deleteWorkflow(BuildContext context) {
    final id = _editableWorkflow['id']?.toString();
    if (id == null || id.isEmpty) return;

    final l10n = AppLocalizations.of(context)!;

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Confirm Delete'),
        content: Text(l10n.deleteWorkflowConfirmation(id)),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: Text(l10n.cancel),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(ctx);
              ref
                  .read(workflowsControllerProvider.notifier)
                  .deleteWorkflow(id)
                  .then((_) {
                    if (mounted) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('Deleted successfully')),
                      );
                      Navigator.of(context).pop();
                    }
                  })
                  .catchError((e) {
                    if (mounted) {
                      String errorMsg = e.toString();
                      if (e is AppError && e is ApiAppError) {
                         if (e.errorCode == 'RESOURCE_IN_USE') {
                           errorMsg = l10n.errorResourceInUse;
                         }
                      } else if (errorMsg.contains('RESOURCE_IN_USE') || errorMsg.contains('400')) {
                         errorMsg = l10n.errorResourceInUse;
                      }
                      
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          content: Text(errorMsg),
                          backgroundColor: Colors.red,
                        ),
                      );
                    }
                  });
            },
            child: Text(l10n.delete, style: const TextStyle(color: Colors.red)),
          ),
        ],
      ),
    );
  }

  void _addExpectedInput() {
    setState(() {
      final inputs = SafeCast.safeList(_editableWorkflow['expected_inputs']);
      inputs.add({
        'role': 'new_input_role',
        'type': 'string',
        'description': 'Input description...',
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
        'input_mappings': <String, dynamic>{},
      });
      _editableWorkflow['steps'] = steps;
    });
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final stepsAsync = ref.watch(stepsControllerProvider);
    final stepsList = stepsAsync.value ?? [];

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.workflowEditTitle),
        actions: [
          if (widget.workflow['id']?.toString().isNotEmpty == true)
            IconButton(
              onPressed: () => _deleteWorkflow(context),
              icon: const Icon(Icons.delete, color: Colors.red),
              tooltip: 'Delete',
            ),
          FilledButton.icon(
            onPressed: _saveWorkflow,
            icon: const Icon(Icons.save),
            label: const Text('Save'),
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
    final roleController = TextEditingController(
      text: SafeCast.safeString(inputDef['role']),
    );
    final descController = TextEditingController(
      text: SafeCast.safeString(inputDef['description']),
    );

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Row(
          children: [
            Expanded(
              child: Focus(
                onFocusChange: (f) {
                  if (!f) inputDef['role'] = roleController.text;
                },
                child: TextField(
                  controller: roleController,
                  decoration: InputDecoration(
                    labelText: l10n.workflowRoleKeyLabel,
                  ),
                ),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Focus(
                onFocusChange: (f) {
                  if (!f) inputDef['description'] = descController.text;
                },
                child: TextField(
                  controller: descController,
                  decoration: InputDecoration(
                    labelText: l10n.workflowDescLabel,
                  ),
                ),
              ),
            ),
            const SizedBox(width: 12),
            DropdownButton<String>(
              value:
                  const ['string', 'file', 'json'].contains(inputDef['type'])
                      ? inputDef['type'] as String
                      : 'string',
              items: [
                DropdownMenuItem(
                  value: 'string',
                  child: Text(l10n.workflowTypeString),
                ),
                DropdownMenuItem(
                  value: 'file',
                  child: Text(l10n.workflowTypeFile),
                ),
                DropdownMenuItem(
                  value: 'json',
                  child: Text(l10n.workflowTypeJson),
                ),
              ],
              onChanged: (val) => setState(() => inputDef['type'] = val),
            ),
            IconButton(
              icon: const Icon(Icons.delete, color: Colors.red),
              onPressed: () {
                setState(() {
                  SafeCast.safeList(
                    _editableWorkflow['expected_inputs'],
                  ).removeAt(index);
                });
              },
            ),
          ],
        ),
      ),
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
            Text(
              l10n.workflowInputMappingsLabel,
              style: const TextStyle(fontWeight: FontWeight.bold),
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
                              ),
                            ),
                          ),
                          const Padding(
                            padding: EdgeInsets.symmetric(horizontal: 8.0),
                            child: Icon(Icons.arrow_back),
                          ),
                          Expanded(
                            child: Focus(
                              onFocusChange: (f) {
                                if (!f &&
                                    targetCtrl.text.isNotEmpty &&
                                    sourceCtrl.text.isNotEmpty) {
                                  mappings[targetCtrl.text] = sourceCtrl.text;
                                  stepDef['input_mappings'] = mappings;
                                }
                              },
                              child: TextField(
                                controller: sourceCtrl,
                                decoration: InputDecoration(
                                  labelText: l10n.workflowSourceVarLabel,
                                  isDense: true,
                                ),
                              ),
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
          ],
        ),
      ),
    );
  }
}
