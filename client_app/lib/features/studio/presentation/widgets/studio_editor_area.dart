import 'package:client_app/features/studio/data/studio_repository.dart';
import 'package:client_app/features/studio/presentation/widgets/matrix_editor_panel.dart';
import 'package:client_app/core/error/app_error.dart';
import 'package:client_app/features/studio/domain/models/json_schema.dart';
import 'package:client_app/features/studio/domain/models/component_def.dart';
import 'package:client_app/features/studio/domain/models/workflow_def.dart';
import 'package:client_app/features/orchestration/presentation/widgets/sdui/generic_table.dart';
import 'package:client_app/features/studio/presentation/widgets/sdui/reorderable_array_builder.dart';
import 'package:client_app/features/studio/presentation/providers/studio_controller.dart';
import 'package:client_app/features/studio/presentation/widgets/dynamic_config_form.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class StudioEditorArea extends ConsumerStatefulWidget {
  final String? selectedStepId;

  const StudioEditorArea({super.key, required this.selectedStepId});

  @override
  ConsumerState<StudioEditorArea> createState() => _StudioEditorAreaState();
}

class _StudioEditorAreaState extends ConsumerState<StudioEditorArea> {
  @override
  void initState() {
    super.initState();
    // Ensure components are loaded
    Future.microtask(() {
      ref.read(studioControllerProvider.notifier).loadComponents();
    });
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(studioControllerProvider);
    final l10n = AppLocalizations.of(context)!;

    // Check for Matrix Selection first
    if (state.selectedMatrixId != null) {
      return state.availableMatrices.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (err, st) => Center(child: Text('Error: $err')),
        data: (matrices) {
          // Using the MatrixController state now, so no need to pass matrix
          return const SingleChildScrollView(child: MatrixEditorPanel());
        },
      );
    }

    return state.activeWorkflow.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (err, st) => Center(child: Text('Error loading editor: $err')),
      data: (workflow) {
        if (workflow == null) {
          return const Center(child: Text('Select a workflow or matrix to edit.'));
        }

        // If no step selected, show Step Sequencer & Scoring Configuration with Tabs
        if (widget.selectedStepId == null) {
          return DefaultTabController(
            length: 3,
            child: Column(
              children: [
                const TabBar(
                  tabs: [
                    Tab(text: "Sequencer"),
                    Tab(text: "Scoring"),
                    Tab(text: "Model Mapping"),
                  ],
                ),
                Expanded(
                  child: TabBarView(
                    children: [
                      // Tab 1: Sequencer
                      SingleChildScrollView(
                        child: _buildStepSequencer(context, ref, workflow, l10n),
                      ),
                      // Tab 2: Scoring
                      ScoringConfigSection(workflow: workflow),
                      // Tab 3: Model Mapping
                       SingleChildScrollView(
                         child: Padding(
                           padding: const EdgeInsets.all(16.0),
                           child: ModelMappingGrid(
                             steps: workflow.steps,
                             currentMapping: (workflow.uiSchema['default_model_mapping'] as Map?)?.cast<String, String>() ?? {},
                             onChanged: (newMapping) => _updateModelMapping(ref, workflow, newMapping),
                           ),
                         ),
                       ),
                    ],
                  ),
                ),
              ],
            ),
          );
        }

        // Find the selected step safely
        final selectedStep = workflow.steps.cast<WorkflowStepDef?>().firstWhere(
          (step) => step?.id == widget.selectedStepId,
          orElse: () => null,
        );

        if (selectedStep == null) {
          return Center(child: Text(l10n.errorNotFound));
        }

        return Card(
          margin: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header
              Padding(
                padding: const EdgeInsets.all(16.0),
                child: Text(
                  'Configuration: ${selectedStep.name}',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
              ),
              const Divider(height: 1),

              // Dynamic Form
              Expanded(
                child: DynamicConfigForm(
                  config: selectedStep.config,
                  onFieldChanged: (key, value) {
                    final newConfig = Map<String, dynamic>.from(
                      selectedStep.config,
                    );
                    newConfig[key] = value;

                    ref
                        .read(studioControllerProvider.notifier)
                        .updateStep(selectedStep.id, newConfig);
                  },
                ),
              ),
            ],
          ),
        );
      },
    );
  }
  Widget _buildStepSequencer(
    BuildContext context,
    WidgetRef ref,
    WorkflowDef workflow,
    AppLocalizations l10n,
  ) {
    return Card(
      margin: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
           Padding(
            padding: const EdgeInsets.all(16.0),
            child: Text(
              l10n.studioStepsHeader,
              style: Theme.of(context).textTheme.titleLarge,
            ),
          ),
          const Divider(height: 1),
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: ReorderableArrayBuilder(
              schema: const JsonSchema(type: 'array'),
              initialData: workflow.steps,
              onChanged: (newItems) {
                // Handle additions (deletions are handled by custom builder, reorder by onReorder)
                // But specifically for 'Add', ReorderableArrayBuilder calls this.
                // We need to save the new list.
                final newSteps = newItems.cast<WorkflowStepDef>();
                _updateSteps(ref, workflow, newSteps);
              },
              onReorder: (oldIndex, newIndex) {
                 ref.read(studioControllerProvider.notifier).reorderSteps(oldIndex, newIndex);
              },
              itemFactory: () {
                 // Create a valid default step to prevent cast errors
                 final id = 'step_${DateTime.now().millisecondsSinceEpoch}';
                 return WorkflowStepDef(
                   id: id, 
                   name: 'New Step', 
                   taskKey: 'judge',
                 );
              },
              customItemBuilder: (context, index, item) {
                final step = item as WorkflowStepDef;
                return Card(
                  key: ValueKey(step.id),
                  margin: const EdgeInsets.symmetric(vertical: 4.0),
                  child: ListTile(
                    leading: const Icon(Icons.drag_handle),
                    title: Text(step.name.isNotEmpty ? step.name : step.id),
                    subtitle: Text('Task: ${step.taskKey}'),
                    trailing: IconButton(
                       icon: const Icon(Icons.delete, color: Colors.red),
                       onPressed: () => _deleteStep(ref, workflow, step.id),
                    ),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _updateSteps(WidgetRef ref, WorkflowDef workflow, List<WorkflowStepDef> newSteps) async {
    final newWf = workflow.copyWith(steps: newSteps);
    try {
      await ref.read(studioRepositoryProvider).saveWorkflow(newWf);
      await ref.read(studioControllerProvider.notifier).loadWorkflow(workflow.id);
    } catch (e) {
      _showError(context, e);
    }
  }

  Future<void> _deleteStep(WidgetRef ref, WorkflowDef workflow, String stepId) async {
    final newSteps = workflow.steps.where((s) => s.id != stepId).toList();
    final newWf = workflow.copyWith(steps: newSteps);

    try {
      await ref.read(studioRepositoryProvider).saveWorkflow(newWf);
      await ref.read(studioControllerProvider.notifier).loadWorkflow(workflow.id);
    } catch (e) {
       _showError(context, e);
    }
  }

  Future<void> _updateModelMapping(WidgetRef ref, WorkflowDef workflow, Map<String, String> mapping) async {
    final newUiSchema = Map<String, dynamic>.from(workflow.uiSchema);
    newUiSchema['default_model_mapping'] = mapping;
    
    final newWf = workflow.copyWith(uiSchema: newUiSchema);
    
    try {
       await ref.read(studioRepositoryProvider).saveWorkflow(newWf);
       await ref.read(studioControllerProvider.notifier).loadWorkflow(workflow.id);
    } catch (e) {
       _showError(context, e);
    }
  }


  void _showError(BuildContext context, Object error) {
    if (!context.mounted) return;
    
    String errorMessage = 'An error occurred';
    if (error is AppError) {
      errorMessage = error.when(
        unknown: (_, __) => 'Unknown error',
        network: (_) => 'Network error',
        server: (msg, _) => msg ?? 'Server error',
        unauthorized: () => 'Unauthorized',
        notFound: (msg) => msg,
        validation: (reason) => 'Validation error: $reason',
        validationMissing: (fields) => 'Missing fields: ${fields.join(", ")}',
        cancelled: () => 'Cancelled',
        api: (_, detail, __, ___) => detail,
      );
    } else {
      errorMessage = error.toString();
    }

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(errorMessage),
        backgroundColor: Theme.of(context).colorScheme.error,
        duration: const Duration(seconds: 4),
      ),
    );
  }
}

class ScoringConfigSection extends ConsumerWidget {
  final WorkflowDef workflow;

  const ScoringConfigSection({super.key, required this.workflow});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // We access components to populate dropdowns
    final componentsAsync = ref.watch(studioControllerProvider).components;

    return Card(
      margin: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Scoring Configuration',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                ElevatedButton.icon(
                  onPressed: () => _addScoringLogic(context, ref, workflow),
                  icon: const Icon(Icons.add),
                  label: const Text('Add Logic'),
                ),
              ],
            ),
          ),
          const Divider(height: 1),
          Expanded(
            child: ListView.separated(
              itemCount: workflow.scoringLogic.length,
              separatorBuilder: (_, __) => const Divider(),
              itemBuilder: (context, index) {
                final logic = workflow.scoringLogic[index];
                return ExpansionTile(
                  title: Text(logic.label),
                  subtitle: Text('${logic.rules.length} Rules'),
                  children: [
                    _RulesTable(
                      workflow: workflow,
                      logicIndex: index,
                      logic: logic,
                      availableComponents: componentsAsync.value ?? [],
                    ),
                  ],
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _addScoringLogic(
    BuildContext context,
    WidgetRef ref,
    WorkflowDef workflow,
  ) async {
    final newLogic = ScoringLogic(label: 'New Logic ${workflow.scoringLogic.length + 1}');
    final updatedList = [...workflow.scoringLogic, newLogic];
    final updatedWf = workflow.copyWith(scoringLogic: updatedList);
    await _saveAndReload(context, ref, updatedWf);
  }

  static Future<void> _saveAndReload(BuildContext context, WidgetRef ref, WorkflowDef updatedWf) async {
    try {
      await ref.read(studioRepositoryProvider).saveWorkflow(updatedWf);
      // Reload to refresh UI (Repo Save is single source of truth here)
      await ref.read(studioControllerProvider.notifier).loadWorkflow(updatedWf.id);
    } catch (e) {
      debugPrint("Failed to save: $e");
      if (context.mounted) {
        String errorMessage = 'Failed to save';
        if (e is AppError) {
          errorMessage = e.when(
            unknown: (_, __) => 'Unknown error',
            network: (_) => 'Network error',
            server: (msg, _) => msg ?? 'Server error',
            unauthorized: () => 'Unauthorized',
            notFound: (msg) => msg,
            validation: (reason) => 'Validation error: $reason',
            validationMissing: (fields) => 'Missing fields: ${fields.join(", ")}',
            cancelled: () => 'Cancelled',
            api: (_, detail, __, ___) => detail,
          );
        } else {
             errorMessage = e.toString();
        }

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(errorMessage),
            backgroundColor: Theme.of(context).colorScheme.error,
            duration: const Duration(seconds: 4),
          ),
        );
      }
    }
  }
}

class _RulesTable extends ConsumerWidget {
  final WorkflowDef workflow;
  final int logicIndex;
  final ScoringLogic logic;
  final List<StudioComponentDef> availableComponents;

  const _RulesTable({
    required this.workflow,
    required this.logicIndex,
    required this.logic,
    required this.availableComponents,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Column(
      children: [
        DataTable(
          columns: const [
            DataColumn(label: Text('Component')),
            DataColumn(label: Text('Metric')),
            DataColumn(label: Text('Weight')),
            DataColumn(label: Text('Actions')),
          ],
          rows: logic.rules.asMap().entries.map((entry) {
            final ruleIndex = entry.key;
            final rule = entry.value;
            return DataRow(cells: [
              DataCell(
                DropdownButton<String>(
                  value: availableComponents.any((c) => c.id == rule.componentId) ? rule.componentId : null,
                  hint: Text(rule.componentId),
                  items: availableComponents.map((c) {
                    return DropdownMenuItem(
                      value: c.id,
                      child: Text(c.name),
                    );
                  }).toList(),
                  onChanged: (val) {
                    if (val != null) _updateRule(context, ref, ruleIndex, rule.copyWith(componentId: val));
                  },
                ),
              ),
              DataCell(
                SizedBox(
                  width: 150,
                  child: TextFormField(
                    initialValue: rule.metricKey,
                    decoration: const InputDecoration(isDense: true),
                    onFieldSubmitted: (val) {
                      _updateRule(context, ref, ruleIndex, rule.copyWith(metricKey: val));
                    },
                  ),
                ),
              ),
              DataCell(
                SizedBox(
                  width: 150,
                  child: Row(
                    children: [
                      Expanded(
                        child: Slider(
                          value: rule.weight,
                          onChanged: (val) {
                            // Debounce logic would go here
                          },
                          onChangeEnd: (val) {
                             _updateRule(context, ref, ruleIndex, rule.copyWith(weight: val));
                          },
                        ),
                      ),
                      Text(rule.weight.toStringAsFixed(1)),
                    ],
                  ),
                ),
              ),
              DataCell(
                IconButton(
                  icon: const Icon(Icons.delete, size: 20),
                  onPressed: () => _removeRule(context, ref, ruleIndex),
                ),
              ),
            ]);
          }).toList(),
        ),
        Padding(
          padding: const EdgeInsets.all(8.0),
          child: OutlinedButton(
            onPressed: () => _addRule(context, ref),
            child: const Text('Add Rule'),
          ),
        ),
      ],
    );
  }

  Future<void> _updateRule(BuildContext context, WidgetRef ref, int ruleIndex, ComponentScoringRule newRule) async {
    final newRules = List<ComponentScoringRule>.from(logic.rules);
    newRules[ruleIndex] = newRule;
    await _updateLogic(context, ref, logic.copyWith(rules: newRules));
  }

  Future<void> _removeRule(BuildContext context, WidgetRef ref, int ruleIndex) async {
    final newRules = List<ComponentScoringRule>.from(logic.rules);
    newRules.removeAt(ruleIndex);
    await _updateLogic(context, ref, logic.copyWith(rules: newRules));
  }

  Future<void> _addRule(BuildContext context, WidgetRef ref) async {
    // Default to first component or empty
    final compId = availableComponents.isNotEmpty ? availableComponents.first.id : 'unknown';
    final newRule = ComponentScoringRule(componentId: compId, metricKey: 'score', weight: 1.0);
     final newRules = [...logic.rules, newRule];
    await _updateLogic(context, ref, logic.copyWith(rules: newRules));
  }

  Future<void> _updateLogic(BuildContext context, WidgetRef ref, ScoringLogic newLogic) async {
    final newLogics = List<ScoringLogic>.from(workflow.scoringLogic);
    newLogics[logicIndex] = newLogic;
    final updatedWf = workflow.copyWith(scoringLogic: newLogics);
    await ScoringConfigSection._saveAndReload(context, ref, updatedWf);
  }
}
