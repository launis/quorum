import 'package:client_app/features/studio/data/schema_repository.dart';
import 'package:client_app/features/studio/data/studio_repository.dart';
import 'package:client_app/features/studio/domain/models/component_def.dart';
import 'package:client_app/features/studio/domain/models/json_schema.dart';
import 'package:client_app/features/studio/domain/models/workflow_def.dart';
import 'package:client_app/features/studio/presentation/providers/studio_controller.dart';
import 'package:client_app/features/studio/presentation/widgets/dynamic_step_form.dart';
import 'package:client_app/features/studio/presentation/widgets/strategy_selection_field.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Manual provider to avoid building .g.dart
final componentSchemaProvider = FutureProvider.family<JsonSchema, String>((ref, type) async {
  return ref.read(schemaRepositoryProvider).fetchSchema(type);
});

class StepConfigPanel extends ConsumerWidget {
  final WorkflowStepDef? step;

  const StepConfigPanel({super.key, required this.step});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;

    if (step == null) {
      return Center(
        child: Text(
          l10n.studioSelectStepPrompt,
          style: Theme.of(context).textTheme.bodyLarge?.copyWith(
            color: Theme.of(context).colorScheme.outline,
          ),
        ),
      );
    }

    // Components Logic
    final title = "Configuration";
    final availableComponents = ref.watch(studioControllerProvider).components.value ?? [];
    final linkedComponents = (step!.config['_linked_components'] as List?)?.cast<String>() ?? [];

    void updateConfig(String key, dynamic value) {
        final newConfig = Map<String, dynamic>.from(step!.config);
        newConfig[key] = value;
        ref.read(studioControllerProvider.notifier).updateStep(step!.id, newConfig);
    }

    return Card(
      margin: const EdgeInsets.all(16.0),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '$title: ${step!.name}',
                        style: Theme.of(context).textTheme.headlineSmall,
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Task: ${step!.taskKey}',
                        style: Theme.of(context).textTheme.labelMedium,
                      ),
                    ],
                  ),
                ),
                _ComponentPicker(
                   availableComponents: availableComponents,
                   onSelected: (compId) => _addComponent(ref, compId),
                ),
              ],
            ),
            const Divider(height: 32),
            Expanded(
              child: SingleChildScrollView(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // 1. Base Step Config
                     _buildSectionHeader(context, "Base Configuration"),
                     StrategySelectionField(
                       currentStrategy: step!.config['model_strategy'] as String?,
                       onChanged: (val) => updateConfig('model_strategy', val),
                     ),
                     const SizedBox(height: 16),
                     DynamicStepForm(
                       config: step!.config, // Filters out _internal inside widget
                       onChanged: updateConfig,
                     ),
                     const SizedBox(height: 24),
                    
                    // 1.5 Judge Configuration (Matrix Selection)
                    if (step!.taskKey.toLowerCase() == 'judge') ...[
                       _buildSectionHeader(context, "Judge Configuration"),
                       _MatrixSelectionField(
                         currentMatrixId: step!.config['matrix_id'],
                         onChanged: (val) => updateConfig('matrix_id', val),
                         availableMatrices: ref.watch(studioControllerProvider).availableMatrices.value ?? [],
                       ),
                       const SizedBox(height: 24),
                    ],

                    // 2. Linked Components
                    if (linkedComponents.isNotEmpty)
                      ...linkedComponents.map((compId) {
                        final compDef = availableComponents.firstWhere(
                          (c) => c.id == compId,
                          orElse: () => StudioComponentDef(id: compId, name: 'Unknown', type: 'unknown', content: {}),
                        );
                        
                        return _ComponentConfigSection(
                           stepId: step!.id,
                           component: compDef,
                           currentConfig: step!.config,
                           onUpdateConfig: updateConfig,
                           onRemove: () => _removeComponent(ref, compId),
                        );
                      }),

                    const SizedBox(height: 24),
                    
                    // 3. Output & Scoring
                    _buildSectionHeader(context, "Output & Scoring"),
                    _OutputAndScoringSection(step: step!, availableComponents: availableComponents),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _addComponent(WidgetRef ref, String compId) {
    final currentLinks = (step!.config['_linked_components'] as List?)?.cast<String>() ?? [];
    if (currentLinks.contains(compId)) return;
    
    final newLinks = [...currentLinks, compId];
    _updateConfigWithRef(ref, '_linked_components', newLinks);
  }

  void _removeComponent(WidgetRef ref, String compId) {
    final currentLinks = (step!.config['_linked_components'] as List?)?.cast<String>() ?? [];
    final newLinks = currentLinks.where((c) => c != compId).toList();
    _updateConfigWithRef(ref, '_linked_components', newLinks);
  }
  
  void _updateConfigWithRef(WidgetRef ref, String key, dynamic value) {
     final newConfig = Map<String, dynamic>.from(step!.config);
     newConfig[key] = value;
     ref.read(studioControllerProvider.notifier).updateStep(step!.id, newConfig);
  }

  Widget _buildSectionHeader(BuildContext context, String title) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16.0),
      child: Text(
        title,
        style: Theme.of(context).textTheme.titleMedium?.copyWith(
          color: Theme.of(context).colorScheme.primary,
        ),
      ),
    );
  }
}

class _MatrixSelectionField extends StatelessWidget {
  final String? currentMatrixId;
  final ValueChanged<String?> onChanged;
  final List<StudioComponentDef> availableMatrices;

  const _MatrixSelectionField({
    required this.currentMatrixId,
    required this.onChanged,
    required this.availableMatrices,
  });

  @override
  Widget build(BuildContext context) {
    // If current ID is not in list (e.g. deleted), we should still show it or handle null
    // But for now, we just match what we can.
    final l10n = AppLocalizations.of(context)!;
    
    return DropdownButtonFormField<String>(
      value: availableMatrices.any((m) => m.id == currentMatrixId) ? currentMatrixId : null,
      decoration: InputDecoration(
        labelText: l10n.studioSelectMatrix,
        border: const OutlineInputBorder(),
        isDense: true,
        helperText: currentMatrixId != null && !availableMatrices.any((m) => m.id == currentMatrixId)
            ? 'Selected matrix not found ($currentMatrixId)'
            : null,
      ),
      items: [
         const DropdownMenuItem(value: null, child: Text('None')),
         ...availableMatrices.map((m) {
           return DropdownMenuItem(
             value: m.id,
             child: Text(m.name, overflow: TextOverflow.ellipsis),
           );
         }),
      ],
      onChanged: onChanged,
    );
  }
}

class _ComponentPicker extends StatelessWidget {
  final List<StudioComponentDef> availableComponents;
  final ValueChanged<String> onSelected;

  const _ComponentPicker({required this.availableComponents, required this.onSelected});

  @override
  Widget build(BuildContext context) {
    return MenuAnchor(
       builder: (context, controller, child) {
         return FilledButton.icon(
           onPressed: () {
             if (controller.isOpen) {
               controller.close();
             } else {
               controller.open();
             }
           },
           icon: const Icon(Icons.add),
           label: const Text('Add Component'),
         );
       },
       menuChildren: availableComponents.map((c) {
         return MenuItemButton(
           onPressed: () => onSelected(c.id),
           child: Text('${c.name} (${c.type})'),
         );
       }).toList(),
    );
  }
}

class _ComponentConfigSection extends ConsumerWidget {
  final String stepId;
  final StudioComponentDef component;
  final Map<String, dynamic> currentConfig;
  final Function(String, dynamic) onUpdateConfig;
  final VoidCallback onRemove;

  const _ComponentConfigSection({
    required this.stepId,
    required this.component,
    required this.currentConfig,
    required this.onUpdateConfig,
    required this.onRemove,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final schemaAsync = ref.watch(componentSchemaProvider(component.type));

    return Card(
      color: Theme.of(context).colorScheme.surfaceContainerLow,
      margin: const EdgeInsets.only(bottom: 16.0),
      child: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(component.name, style: Theme.of(context).textTheme.titleSmall),
                IconButton(
                  icon: const Icon(Icons.delete_outline, size: 20),
                  onPressed: onRemove,
                  tooltip: 'Remove Component',
                )
              ],
            ),
            const Divider(),
            schemaAsync.when(
               loading: () => const LinearProgressIndicator(),
               error: (e, _) => Text('Error loading schema: $e'),
               data: (schema) => DynamicStepForm(
                  config: currentConfig,
                  schema: schema,
                  onChanged: onUpdateConfig,
               ),
            ),
          ],
        ),
      ),
    );
  }
}

class _OutputAndScoringSection extends ConsumerWidget {
  final WorkflowStepDef step;
  final List<StudioComponentDef> availableComponents;

  const _OutputAndScoringSection({required this.step, required this.availableComponents});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Access global workflow logic via controller
    final workflowDef = ref.watch(studioControllerProvider).activeWorkflow.value;
    if (workflowDef == null) return const SizedBox.shrink();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Text("Scoring Bars (Matrix)", style: TextStyle(fontWeight: FontWeight.bold)),
            IconButton(
              onPressed: () => _addLogic(ref, workflowDef),
              icon: const Icon(Icons.add_circle_outline),
              tooltip: "Add Bar",
            )
          ],
        ),
        const SizedBox(height: 8),
        if (workflowDef.scoringLogic.isEmpty)
           const Padding(
             padding: EdgeInsets.all(8.0),
             child: Text("No scoring bars defined. Add one to visualize metrics.", style: TextStyle(fontStyle: FontStyle.italic)),
           ),
        ...workflowDef.scoringLogic.asMap().entries.map((entry) {
          final index = entry.key;
          final logic = entry.value;
          return Card(
             margin: const EdgeInsets.only(bottom: 8.0),
             child: ExpansionTile(
               title: TextFormField(
                 initialValue: logic.label,
                 decoration: const InputDecoration(labelText: "Bar Label"),
                 onFieldSubmitted: (v) => _updateLogic(ref, workflowDef, index, logic.copyWith(label: v)),
               ),
               children: [
                 _RulesTable(
                    logic: logic,
                    availableComponents: availableComponents,
                    onUpdate: (newLogic) => _updateLogic(ref, workflowDef, index, newLogic),
                 ),
                 Align(
                   alignment: Alignment.centerRight,
                   child: TextButton.icon(
                     onPressed: () => _removeLogic(ref, workflowDef, index),
                     icon: const Icon(Icons.delete, color: Colors.red),
                     label: const Text("Remove Bar", style: TextStyle(color: Colors.red)),
                   ),
                 )
               ],
             ),
          );
        }),
      ],
    );
  }

  Future<void> _addLogic(WidgetRef ref, WorkflowDef workflow) async {
    final newLogic = ScoringLogic(label: "New Bar");
    final newWf = workflow.copyWith(scoringLogic: [...workflow.scoringLogic, newLogic]);
    await ref.read(studioRepositoryProvider).saveWorkflow(newWf);
    ref.read(studioControllerProvider.notifier).loadWorkflow(workflow.id);
  }

  Future<void> _updateLogic(WidgetRef ref, WorkflowDef workflow, int index, ScoringLogic updatedLogic) async {
    final newLogics = List<ScoringLogic>.from(workflow.scoringLogic);
    newLogics[index] = updatedLogic;
    final newWf = workflow.copyWith(scoringLogic: newLogics);
    await ref.read(studioRepositoryProvider).saveWorkflow(newWf);
    ref.read(studioControllerProvider.notifier).loadWorkflow(workflow.id);
  }

  Future<void> _removeLogic(WidgetRef ref, WorkflowDef workflow, int index) async {
    final newLogics = List<ScoringLogic>.from(workflow.scoringLogic);
    newLogics.removeAt(index);
    final newWf = workflow.copyWith(scoringLogic: newLogics);
    await ref.read(studioRepositoryProvider).saveWorkflow(newWf);
    ref.read(studioControllerProvider.notifier).loadWorkflow(workflow.id);
  }
}

class _RulesTable extends StatelessWidget {
  final ScoringLogic logic;
  final List<StudioComponentDef> availableComponents;
  final ValueChanged<ScoringLogic> onUpdate;

  const _RulesTable({
    required this.logic,
    required this.availableComponents,
    required this.onUpdate,
  });

  @override
  Widget build(BuildContext context) {
     return Column(
       children: [
         DataTable(
           headingRowHeight: 40,
           dataRowMinHeight: 30,
           columnSpacing: 16,
           columns: const [
             DataColumn(label: Text('Component')),
             DataColumn(label: Text('Metric')),
             DataColumn(label: Text('Weight')),
             DataColumn(label: Text('')),
           ],
           rows: logic.rules.asMap().entries.map((entry) {
             final idx = entry.key;
             final rule = entry.value;
             return DataRow(cells: [
               DataCell(
                 DropdownButton<String>(
                   value: availableComponents.any((c) => c.id == rule.componentId) ? rule.componentId : null,
                   hint: const Text("Select..."),
                   isDense: true,
                   underline: const SizedBox.shrink(),
                   items: availableComponents.map((c) => DropdownMenuItem(value: c.id, child: Text(c.name, overflow: TextOverflow.ellipsis))).toList(),
                   onChanged: (v) {
                     if (v != null) _updateRule(idx, rule.copyWith(componentId: v));
                   },
                 )
               ),
               DataCell(
                 TextFormField(
                   initialValue: rule.metricKey,
                   decoration: const InputDecoration(border: InputBorder.none, isDense: true),
                   onFieldSubmitted: (v) => _updateRule(idx, rule.copyWith(metricKey: v)),
                 )
               ),
               DataCell(
                 SizedBox(
                   width: 80,
                   child: TextFormField(
                     initialValue: rule.weight.toString(),
                     keyboardType: TextInputType.number,
                     decoration: const InputDecoration(border: InputBorder.none, isDense: true),
                     onFieldSubmitted: (v) {
                       final d = double.tryParse(v);
                       if (d != null) _updateRule(idx, rule.copyWith(weight: d));
                     },
                   ),
                 )
               ),
               DataCell(
                 IconButton(icon: const Icon(Icons.close, size: 16), onPressed: () => _removeRule(idx))
               )
             ]);
           }).toList(),
         ),
         TextButton.icon(
            onPressed: _addRule,
            icon: const Icon(Icons.add, size: 16),
            label: const Text("Add Rule"),
         )
       ],
     );
  }

  void _updateRule(int index, ComponentScoringRule newRule) {
    final newRules = List<ComponentScoringRule>.from(logic.rules);
    newRules[index] = newRule;
    onUpdate(logic.copyWith(rules: newRules));
  }

  void _removeRule(int index) {
      final newRules = List<ComponentScoringRule>.from(logic.rules);
      newRules.removeAt(index);
      onUpdate(logic.copyWith(rules: newRules));
  }

  void _addRule() {
     final firstComp = availableComponents.isNotEmpty ? availableComponents.first.id : 'unknown';
     final newRule = ComponentScoringRule(componentId: firstComp, metricKey: 'score', weight: 1.0);
     onUpdate(logic.copyWith(rules: [...logic.rules, newRule]));
  }
}



// remove generated provider definition if present

