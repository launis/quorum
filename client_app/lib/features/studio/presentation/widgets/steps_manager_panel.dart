import 'package:client_app/core/error/app_error.dart';
import 'package:client_app/features/studio/data/studio_repository.dart';
import 'package:client_app/features/studio/domain/models/component_def.dart';
import 'package:client_app/features/studio/domain/models/step_config.dart';
import 'package:client_app/features/studio/presentation/providers/steps_controller.dart';
import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';

class StepsManagerPanel extends HookConsumerWidget {
  const StepsManagerPanel({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // 1. State
    final stepsState = ref.watch(stepsControllerProvider);
    final selectedId = useState<String?>(null);
    final searchController = useTextEditingController();

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
                          decoration: const InputDecoration(
                            labelText: "Search Steps",
                            prefixIcon: Icon(Icons.search),
                            isDense: true,
                            border: OutlineInputBorder(),
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
                        subtitle: Text(
                          step.id,
                          style: TextStyle(
                            fontSize: 12,
                            color: Theme.of(context).colorScheme.secondary,
                          ),
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
                    ? const Center(
                      child: Text(
                        "Select a step to edit",
                        style: TextStyle(color: Colors.grey),
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
      return const Center(child: Text("Step not found"));
    }

    final isNew = stepId == 'new';
    final repo = ref.watch(studioRepositoryProvider);

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
    final componentsFuture = useMemoized(() => repo.getComponents());
    final componentsSnapshot = useFuture(componentsFuture);
    
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
                const SnackBar(content: Text("ID and Name are required."))
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
                    const SnackBar(content: Text("Step saved!"))
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
                title: const Text("Confirm Delete"),
                content: Text("Delete step '${initialStep!.id}'?"),
                actions: [
                    TextButton(onPressed: () => Navigator.pop(context, false), child: const Text("Cancel")),
                    FilledButton(
                        style: FilledButton.styleFrom(backgroundColor: Colors.red),
                        onPressed: () => Navigator.pop(context, true), 
                        child: const Text("Delete")
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
                            c.name.toLowerCase().contains(search.toLowerCase())
                        ).toList();

                        return AlertDialog(
                            title: const Text("Add Prompt Component"),
                            content: SizedBox(
                                width: 500,
                                height: 500,
                                child: Column(
                                    children: [
                                        TextField(
                                            decoration: const InputDecoration(
                                                labelText: "Search Prompts", 
                                                prefixIcon: Icon(Icons.search),
                                                border: OutlineInputBorder()
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
                                                        title: Text(c.name),
                                                        subtitle: Text("${c.type} • ${c.id}", style: const TextStyle(fontSize: 12)),
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
                                TextButton(onPressed: () => Navigator.pop(context), child: const Text("Close")),
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
                Text(isNew ? "Create New Step" : "Edit Step", style: Theme.of(context).textTheme.headlineSmall),
                const Spacer(),
                FilledButton.icon(
                    icon: const Icon(Icons.save),
                    label: const Text("Save"),
                    onPressed: save,
                ),
                if (!isNew) ...[
                    const SizedBox(width: 8),
                    OutlinedButton.icon(
                         icon: const Icon(Icons.delete, color: Colors.red),
                         label: const Text("Delete", style: TextStyle(color: Colors.red)),
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
                        decoration: const InputDecoration(
                            labelText: "Step ID", 
                            border: OutlineInputBorder(),
                            helperText: "Unique identifier (e.g. 'step_analyst')"
                        ),
                    ),
                ),
                const SizedBox(width: 16),
                Expanded(
                    child: TextField(
                        controller: nameController,
                        decoration: const InputDecoration(
                            labelText: "Name", 
                            border: OutlineInputBorder()
                        ),
                    ),
                ),
            ]),
            const SizedBox(height: 16),
            
            // Description
            TextField(
                controller: descController,
                decoration: const InputDecoration(
                    labelText: "Description", 
                    border: OutlineInputBorder()
                ),
            ),
             const SizedBox(height: 16),

            // Agent Class
            DropdownButtonFormField<String>(
                value: agentOptions.contains(selectedAgent.value) ? selectedAgent.value : agentOptions.first,
                decoration: const InputDecoration(
                    labelText: "Agent Logic Class",
                    border: OutlineInputBorder(),
                ),
                items: agentOptions.map((a) => DropdownMenuItem(value: a, child: Text(a))).toList(),
                onChanged: (v) {
                    if (v != null) selectedAgent.value = v;
                },
            ),

            // JudgeAgent Specifics (Matrix)
            if (selectedAgent.value == 'JudgeAgent') ...[
                const SizedBox(height: 16),
                const Text("Judge Configuration", style: TextStyle(fontWeight: FontWeight.bold)),
                if (componentsSnapshot.hasData) ...[
                    Builder(builder: (context) {
                        final matrices = componentsSnapshot.data!.where((c) => c.type == 'evaluation_matrix').toList();
                        // Ensure selected ID exists in the list, otherwise null
                        final currentValue = matrices.any((m) => m.id == selectedMatrixId.value) 
                            ? selectedMatrixId.value 
                            : null;
                            
                        return DropdownButtonFormField<String>(
                             value: currentValue,
                             decoration: const InputDecoration(
                                 labelText: "Evaluation Matrix",
                                 border: OutlineInputBorder(),
                                 helperText: "The criteria used for judging."
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
                const Text("Prompt Assembly", style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                const Spacer(),
                TextButton.icon(
                    icon: const Icon(Icons.add),
                    label: const Text("Add Prompt"),
                    onPressed: () {
                         if (componentsSnapshot.hasData) {
                             showAddPromptDialog(componentsSnapshot.data!);
                         }
                    },
                ),
            ]),
            const Text("Components that form the context and instruction for this agent.", style: TextStyle(color: Colors.grey)),
            const SizedBox(height: 8),

            // Prompt Chips
            componentsSnapshot.hasData 
            ? Wrap(
                spacing: 8,
                runSpacing: 8,
                children: llmPrompts.value.map((pid) {
                     final comp = componentsSnapshot.data!.firstWhere((c) => c.id == pid, orElse: () => StudioComponentDef(id: pid, name: pid, type: '?', content: const {}));
                     return InputChip(
                         label: Text(comp.name),
                         tooltip: comp.id,
                         onDeleted: () {
                             llmPrompts.value = llmPrompts.value.where((id) => id != pid).toList();
                         },
                     );
                }).toList(),
            ) : const LinearProgressIndicator(),

            const SizedBox(height: 40),
        ],
      ),
    );
  }
}

