import 'package:client_app/core/error/app_error.dart';
import 'package:client_app/features/studio/data/studio_repository.dart';
import 'package:client_app/features/studio/domain/models/component_def.dart';
import 'package:client_app/features/studio/domain/models/step_config.dart';
import 'package:client_app/features/studio/presentation/providers/steps_controller.dart';
import 'package:client_app/features/studio/presentation/providers/available_matrices_controller.dart';
import 'package:client_app/features/studio/presentation/providers/available_components_controller.dart';
import 'package:flutter/material.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:collection/collection.dart';
import 'package:client_app/core/logging/logger_service.dart';

class StepsManagerPanel extends HookConsumerWidget {
  const StepsManagerPanel({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // 1. State
    final stepsState = ref.watch(stepsControllerProvider);
    final selectedId = useState<String?>(null);
    final searchController = useTextEditingController();
    final logger = ref.watch(loggerServiceProvider);

final l10n = AppLocalizations.of(context)!;

    // Derived List (Filtered)
    final filteredSteps =
        useMemoized(() {
          final allSteps = stepsState.value ?? [];
          final query = searchController.text.toLowerCase();
          if (query.isEmpty) return allSteps;
          return allSteps
              .where(
                (s) =>
                    s.name.toLowerCase().contains(query) ||
                    s.id.toLowerCase().contains(query),
              )
              .toList();
        }, [stepsState.value, searchController.text]);

    // Force refresh filtering when text changes
    useListenable(searchController);

    // Removed monolithic controller preload: Riverpod 3.0 handles this natively on watch.

    // 2. Loading / Error States
    if (stepsState.isLoading && !stepsState.hasValue) {
      return const Center(child: CircularProgressIndicator());
    }

    if (stepsState.hasError) {
      return Center(child: Text('Error: ${stepsState.error}'));
    }

    final selectedStep =
        selectedId.value == 'new'
            ? const StepConfig(id: 'step_new', name: 'New Step')
            : (stepsState.value?.where((s) => s.id == selectedId.value).firstOrNull);

    // 3. Layout
    return Row(
      children: [
        // MASTER (List)
        Expanded(
          flex: 2,
          child: Card(
            margin: const EdgeInsets.all(8),
            elevation: 0,
            shape: RoundedRectangleBorder(
              side: BorderSide(
                color: Theme.of(context).colorScheme.outlineVariant,
              ),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Column(
              children: [
                // Toolbar
                Padding(
                  padding: const EdgeInsets.all(8.0),
                  child: Row(
                    children: [
                      Expanded(
                        child: TextField(
                          controller: searchController,
                          decoration: InputDecoration(
                            labelText: l10n.searchSteps,
                            prefixIcon: const Icon(Icons.search),
                            isDense: true,
                            border: const OutlineInputBorder(),
                          ),
                        ),
                      ),
                      const SizedBox(width: 8),
                      // Using standard IconButton for now to avoid analyzer issues if .filled unavailable in some versions
                      IconButton(
                        icon: const Icon(Icons.add),
                        style: IconButton.styleFrom(
                          backgroundColor:
                              Theme.of(context).colorScheme.primaryContainer,
                          foregroundColor:
                              Theme.of(context).colorScheme.onPrimaryContainer,
                        ),
                        tooltip: "Create New Step",
                        onPressed: () {
                          selectedId.value = 'new';
                        },
                      ),
                    ],
                  ),
                ),
                const Divider(height: 1),

                // List
                Expanded(
                  child: ListView.builder(
                    itemCount: filteredSteps.length,
                    itemBuilder: (context, index) {
                      final step = filteredSteps[index];
                      final isSelected = step.id == selectedId.value;
                      return ListTile(
                        title: Text(
                          step.name,
                          style: const TextStyle(fontWeight: FontWeight.w600),
                        ),
                        selected: isSelected,
                        selectedTileColor:
                            Theme.of(context).colorScheme.primaryContainer
                                .withOpacity(0.2),
                        onTap: () => selectedId.value = step.id,
                        trailing: const Icon(Icons.chevron_right, size: 16),
                      );
                    },
                  ),
                ),
              ],
            ),
          ),
        ),

        // DETAIL (Editor)
        Expanded(
          flex: 5,
          child: Card(
            margin: const EdgeInsets.all(8),
            elevation: 0,
            shape: RoundedRectangleBorder(
              side: BorderSide(
                color: Theme.of(context).colorScheme.outlineVariant,
              ),
              borderRadius: BorderRadius.circular(8),
            ),
            child:
                selectedId.value == null
                    ? Center(
                      child: Text(
                        l10n.stepSelectToEdit,
                        style: const TextStyle(color: Colors.grey),
                      ),
                    )
                    : _StepEditor(
                      // Key forces rebuild when selection changes
                      key: ValueKey(selectedId.value),
                      stepId: selectedId.value!,
                      initialStep: selectedStep,
                      onSave: () => selectedId.value = null, // Or stay?
                    ),
          ),
        ),
      ],
    );
  }
}

class _StepEditor extends HookConsumerWidget {
  final String stepId;
  final StepConfig? initialStep;
  final VoidCallback onSave;

  const _StepEditor({
    super.key,
    required this.stepId,
    required this.initialStep,
    required this.onSave,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final isMounted = useIsMounted();

    if (initialStep == null && stepId != 'new') {
      return Center(child: Text(AppLocalizations.of(context)!.errorNotFound));
    }

    final l10n = AppLocalizations.of(context)!;
    final isNew = stepId == 'new';
    final repo = ref.watch(studioRepositoryProvider);
    final logger = ref.watch(loggerServiceProvider);

    // Form Controls
    final idController = useTextEditingController(text: initialStep?.id ?? '');
    final nameController = useTextEditingController(
      text: initialStep?.name ?? '',
    );
    final descController = useTextEditingController(
      text: initialStep?.description ?? '',
    );
    
    // Component & Matrix
    final selectedAgent = useState<String>('AnalystAgent');

    // Fetch Data for Selectors
    final availableComponentsState = ref.watch(availableComponentsControllerProvider);
    final matricesState = ref.watch(availableMatricesControllerProvider);
    
    // Derived: Step Prompts
    final llmPrompts = useState<List<String>>([]);

    // Derived: Selected Matrix
    final selectedMatrixId = useState<String?>(null);

    // Initialize State from current step
    useEffect(() {
        if (initialStep != null) {
            idController.text = initialStep!.id;
            nameController.text = initialStep!.name;
            descController.text = initialStep!.description ?? "";
            
            // "One Key" Strategy: No Mapping.
            // The taskKey IS the identifier used in the Component Registry.
            // e.g. "analyst" -> "analyst"
            selectedAgent.value = initialStep!.taskKey;

            // Config
            final conf = initialStep!.config;
            if (conf.containsKey('llm_prompts')) {
                llmPrompts.value = List<String>.from(conf['llm_prompts']);
            }
            if (conf.containsKey('matrix_id')) {
                selectedMatrixId.value = conf['matrix_id'];
            }
        }
        return null; // Cleanup
    }, [initialStep]);

    // Handlers
    Future<void> save() async {
        if (idController.text.isEmpty || nameController.text.isEmpty) {
            ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text(l10n.stepIdNameRequired))
            );
            return;
        }

        // Direct Access: The selected agent ID IS the task key.
        final taskKey = selectedAgent.value;

        final Map<String, dynamic> newConfig = {
            "llm_prompts": llmPrompts.value,
        };
        
        // Specific config for Judge (keyed by 'judge', not 'JudgeAgent')
        if (selectedAgent.value == "judge" && selectedMatrixId.value != null) {
            newConfig["matrix_id"] = selectedMatrixId.value;
        }

        final newStep = StepConfig(
            id: idController.text,
            name: nameController.text,
            description: descController.text,
            taskKey: taskKey, 
            config: newConfig,
        );

        final controller = ref.read(stepsControllerProvider.notifier);
        
        try {
            if (isNew) {
                await controller.create(newStep);
            } else {
                await controller.updateStep(newStep);
            }
            
            if (isMounted()) {
                ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text(l10n.stepSaveSuccess))
                );
                onSave();
            }
        } catch (e) {
             if (isMounted()) {
                ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text("Error saving: $e"), backgroundColor: Colors.red)
                );
             }
        }
    }

    Future<void> deleteStep() async {
        final confirm = await showDialog<bool>(
            context: context,
            builder: (context) => AlertDialog(
                title: Text(l10n.stepDeleteConfirmTitle),
                content: Text(l10n.stepDeleteConfirmMessage(initialStep!.id)),
                actions: [
                    TextButton(onPressed: () => Navigator.pop(context, false), child: Text(l10n.cancel)),
                    FilledButton(
                        style: FilledButton.styleFrom(backgroundColor: Colors.red),
                        onPressed: () => Navigator.pop(context, true), 
                        child: Text(l10n.delete)
                    ),
                ]
            )
        );
        if (confirm == true) {
             await ref.read(stepsControllerProvider.notifier).delete(initialStep!.id);
             onSave(); // Close editor
        }
    }

    void showAddPromptDialog(List<StudioComponentDef> allComponents) {
        showDialog(
            context: context, 
            builder: (context) {
                // Filter valid types
                final validTypes = ['header', 'exclude', 'rule', 'mandate', 'protocol', 'instruction', 'context'];
                final validComponents = allComponents.where((c) => validTypes.contains(c.type)).toList();
                
                String search = "";
                return StatefulBuilder(
                    builder: (context, setState) {
                        final filtered = validComponents.where((c) => 
                            c.id.toLowerCase().contains(search.toLowerCase()) || 
                            (c.name ?? c.slug ?? '').toLowerCase().contains(search.toLowerCase()) ||
                            (c.slug?.toLowerCase().contains(search.toLowerCase()) ?? false)
                        ).toList();

                        return AlertDialog(
                            title: Text(l10n.stepAddPromptTitle),
                            content: SizedBox(
                                width: 500,
                                height: 500,
                                child: Column(
                                    children: [
                                        TextField(
                                            decoration: InputDecoration(
                                                labelText: l10n.stepSearchPrompts, 
                                                prefixIcon: const Icon(Icons.search),
                                                border: const OutlineInputBorder()
                                            ),
                                            onChanged: (v) => setState(() => search = v),
                                        ),
                                        const SizedBox(height: 8),
                                        Expanded(
                                            child: ListView.builder(
                                                itemCount: filtered.length,
                                                itemBuilder: (context, index) {
                                                    final c = filtered[index];
                                                    final isSelected = llmPrompts.value.contains(c.id);
                                                    return ListTile(
                                                        title: Text(c.slug ?? c.name ?? 'Unknown Component (${c.id})'),
                                                        subtitle: Text(c.type, style: const TextStyle(fontSize: 12)),
                                                        trailing: isSelected ? const Icon(Icons.check, color: Colors.green) : null,
                                                        onTap: () {
                                                            if (!isSelected) {
                                                                llmPrompts.value = [...llmPrompts.value, c.id];
                                                            }
                                                            Navigator.pop(context);
                                                        },
                                                    );
                                                }
                                            )
                                        )
                                    ],
                                ),
                            ),
                            actions: [
                                TextButton(onPressed: () => Navigator.pop(context), child: Text(l10n.close)),
                            ],
                        );
                    }
                );
            }
        );
    }

    // Common Agents
    final agentOptions = ['AnalystAgent', 'JudgeAgent', 'SearchAgent', 'OverseerAgent', 'StandardAgent', 'CriticAgent'];

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
            // Header
            Row(children: [
                Text(isNew ? l10n.studioCreateNew : l10n.stepEdit, style: Theme.of(context).textTheme.headlineSmall),
                const Spacer(),
                FilledButton.icon(
                    icon: const Icon(Icons.save),
                    label: Text(l10n.save),
                    onPressed: save,
                ),
                if (!isNew) ...[
                    const SizedBox(width: 8),
                    OutlinedButton.icon(
                         icon: const Icon(Icons.delete, color: Colors.red),
                         label: Text(l10n.delete, style: const TextStyle(color: Colors.red)),
                         onPressed: deleteStep,
                     )
                ]
            ]),
            const Divider(),
            const SizedBox(height: 16),
            
            // Basic Info
            Row(children: [
                Expanded(
                    child: TextField(
                        controller: idController,
                        enabled: isNew, // ID immutable after creation
                        decoration: InputDecoration(
                            labelText: l10n.stepIdLabel, 
                            border: const OutlineInputBorder(),
                            helperText: l10n.stepIdHelper
                        ),
                    ),
                ),
                const SizedBox(width: 16),
                Expanded(
                    child: TextField(
                        controller: nameController,
                        decoration: InputDecoration(
                            labelText: l10n.stepNameLabel, 
                            border: const OutlineInputBorder()
                        ),
                    ),
                ),
            ]),
            const SizedBox(height: 16),
            
            // Description
            TextField(
                controller: descController,
                decoration: InputDecoration(
                    labelText: l10n.stepDescriptionLabel, 
                    border: const OutlineInputBorder()
                ),
            ),
             const SizedBox(height: 16),

            // Agent Class
            DropdownButtonFormField<String>(
                value: agentOptions.contains(selectedAgent.value) ? selectedAgent.value : agentOptions.first,
                decoration: InputDecoration(
                    labelText: l10n.stepAgentLogicClass,
                    border: const OutlineInputBorder(),
                ),
                items: agentOptions.map((a) => DropdownMenuItem(value: a, child: Text(a))).toList(),
                onChanged: (v) {
                    if (v != null) selectedAgent.value = v;
                },
            ),

            // JudgeAgent Specifics (Matrix)
            if (selectedAgent.value == 'JudgeAgent') ...[
                const SizedBox(height: 16),
                Text(l10n.stepJudgeConfig, style: const TextStyle(fontWeight: FontWeight.bold)),
                if (matricesState.hasValue) ...[
                    Builder(builder: (context) {
                        final matrices = matricesState.value ?? [];
                        // Ensure selected ID exists in the list, otherwise null
                        final currentValue = matrices.any((m) => m.id == selectedMatrixId.value) 
                            ? selectedMatrixId.value 
                            : null;
                            
                        return DropdownButtonFormField<String>(
                             value: currentValue,
                             decoration: InputDecoration(
                                 labelText: l10n.stepEvaluationMatrix,
                                 border: const OutlineInputBorder(),
                                 helperText: l10n.stepEvaluationMatrixHelper
                             ),
                             items: matrices.map((m) => DropdownMenuItem<String>(
                                value: m.id, 
                                child: Text(m.name)
                             )).toList(),
                             onChanged: (v) => selectedMatrixId.value = v,
                        );
                    })
                ] else 
                    const LinearProgressIndicator(),
            ],

            const SizedBox(height: 24),
            const Divider(),
            const SizedBox(height: 8),

            // Prompt Assembly
            Row(children: [
                Text(l10n.stepPromptAssembly, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                const Spacer(),
                TextButton.icon(
                    icon: const Icon(Icons.add),
                    label: Text(l10n.stepAddPrompt),
                    onPressed: () {
                         if (availableComponentsState.hasValue) {
                             showAddPromptDialog(availableComponentsState.value ?? []);
                         }
                    },
                ),
            ]),
            Text(l10n.stepPromptAssemblyHelper, style: const TextStyle(color: Colors.grey)),
            const SizedBox(height: 8),

            // Prompt Chips
            availableComponentsState.when(
              loading: () => const Padding(padding: EdgeInsets.symmetric(vertical: 16), child: Center(child: CircularProgressIndicator())),
              error: (err, stack) => Text('Error loading components', style: TextStyle(color: Theme.of(context).colorScheme.error)),
              data: (components) => Wrap(
                spacing: 8,
                runSpacing: 8,
                children: llmPrompts.value.map((pid) {
                     final comp = components.firstWhereOrNull((c) => c.id == pid);
                     
                     if (comp == null) {
                         return InputChip(
                             label: Text('Unknown or Missing ID: ${pid}', style: const TextStyle(color: Colors.white)),
                             backgroundColor: Colors.red.shade900,
                             deleteIconColor: Colors.white,
                             tooltip: pid,
                             onDeleted: () {
                                 llmPrompts.value = llmPrompts.value.where((id) => id != pid).toList();
                             },
                         );
                     }
                     
                     return InputChip(
                         label: Text(comp.slug ?? comp.name ?? 'Unknown (${comp.id})'),
                         tooltip: comp.id,
                         onDeleted: () {
                             llmPrompts.value = llmPrompts.value.where((id) => id != pid).toList();
                         },
                     );
                }).toList(),
              ),
            ),

            const SizedBox(height: 40),
        ],
      ),
    );
  }
}

