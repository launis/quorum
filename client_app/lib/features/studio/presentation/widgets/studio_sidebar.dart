import 'package:client_app/features/studio/domain/models/workflow_def.dart';
import 'package:client_app/features/studio/presentation/providers/studio_controller.dart';
import 'package:client_app/features/auth/presentation/providers/auth_provider.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class StudioSidebar extends ConsumerStatefulWidget {
  final String? selectedStepId; // Note: In this context, this might be misinterpreted as WorkflowId by parent? 
  // We keep the signature but internally we treat the selection as active workflow linkage.
  final ValueChanged<String?> onStepSelected;

  const StudioSidebar({
    super.key,
    required this.selectedStepId,
    required this.onStepSelected,
  });

  @override
  ConsumerState<StudioSidebar> createState() => _StudioSidebarState();
}

class _StudioSidebarState extends ConsumerState<StudioSidebar> {
  // Optimistic items to display while saving
  final List<WorkflowDef> _optimisticWorkflows = [];

  @override
  void initState() {
    super.initState();
    // Removed: Parent WorkflowStudioScreen handles the initial load of workflows.
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(studioControllerProvider);
    final l10n = AppLocalizations.of(context)!;
    final colorScheme = Theme.of(context).colorScheme;

    // Listen to Auth changes (e.g. Login)
    // Relaxed check: Load whenever we have a user, to catch all race conditions
    // Listen to Auth changes (e.g. Login)
    // Relaxed check: Load whenever we have a user, to catch all race conditions
    // DISABLED: WorkflowStudioScreen handles the loading now to prevent double-triggering or race conditions.
    // ref.listen(authStateProvider, (previous, next) {
    //   if (next.value != null) {
    //      ref.read(studioControllerProvider.notifier).loadWorkflows();
    //   }
    // });

    return Container(
      width: 300,
      color: colorScheme.surfaceContainer,
      child: Column(
        children: [
          // Header Row
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 12.0),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      'Workflows',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    IconButton(
                      icon: const Icon(Icons.refresh, size: 18),
                      tooltip: l10n.refresh,
                      onPressed: () => ref.read(studioControllerProvider.notifier).loadWorkflows(),
                    ),
                  ],
                ),
                IconButton.filledTonal(
                  onPressed: _createNewWorkflow,
                  icon: const Icon(Icons.add, size: 20),
                  tooltip: l10n.studioCreateNew,
                  visualDensity: VisualDensity.compact,
                ),
              ],
            ),
          ),
          const Divider(height: 1),

          // Workflow List
          Expanded(
            child: state.workflows.when(
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (err, st) => Container(
                color: Colors.red.shade100,
                padding: const EdgeInsets.all(8.0),
                child: Text('Error: $err', style: const TextStyle(color: Colors.red)),
              ),
              data: (workflows) {
                // Merge real + optimistic
                final allWorkflows = [...workflows, ..._optimisticWorkflows];

                if (allWorkflows.isEmpty) {
                  return Center(child: Text(l10n.noWorkflowsAvailable));
                }

                return ListView.builder(
                  itemCount: allWorkflows.length,
                  itemBuilder: (context, index) {
                    final wf = allWorkflows[index];
                    final isSelected = wf.id == state.activeWorkflow.value?.id;

                    return ListTile(
                      title: Text(wf.name),
                      subtitle: Text(wf.id, style: const TextStyle(fontSize: 10)),
                      selected: isSelected,
                      selectedTileColor: colorScheme.primaryContainer,
                      selectedColor: colorScheme.onPrimaryContainer,
                      onTap: () {
                         ref.read(studioControllerProvider.notifier).loadWorkflow(wf.id);
                         // Clear step selection to show workflow config
                         widget.onStepSelected(null);
                      },
                      trailing: PopupMenuButton<String>(
                        icon: const Icon(Icons.more_vert, size: 20),
                        onSelected: (value) {
                          if (value == 'copy') _showCopyDialog(context, wf);
                          if (value == 'delete') _confirmDelete(context, wf);
                        },
                        itemBuilder: (context) => [
                          PopupMenuItem(
                            value: 'copy',
                            child: Row(
                              children: [
                                const Icon(Icons.copy, size: 18),
                                const SizedBox(width: 8),
                                Text(l10n.studioCopyWorkflow),
                              ],
                            ),
                          ),
                          PopupMenuItem(
                            value: 'delete',
                            child: Row(
                              children: [
                                const Icon(Icons.delete, size: 18, color: Colors.red),
                                const SizedBox(width: 8),
                                Text(l10n.delete, style: const TextStyle(color: Colors.red)),
                              ],
                            ),
                          ),
                        ],
                      ),
                    );
                  },
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _createNewWorkflow() async {
    // Optimistic UI
    final tempId = 'new_${DateTime.now().millisecondsSinceEpoch}';
    final tempWf = WorkflowDef(id: tempId, name: 'New Workflow', description: '', steps: []);
    
    setState(() {
      _optimisticWorkflows.add(tempWf);
    });

    try {
      // Use controller
      await ref.read(studioControllerProvider.notifier).createWorkflow(tempWf);
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Failed to create: $e')));
    } finally {
      if (mounted) {
        setState(() {
          _optimisticWorkflows.remove(tempWf);
        });
      }
    }
  }

  Future<void> _showCopyDialog(BuildContext context, WorkflowDef original) async {
    final l10n = AppLocalizations.of(context)!;
    final nameController = TextEditingController(text: '${original.name} (Copy)');

    final newName = await showDialog<String>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(l10n.studioCopyWorkflow),
        content: TextField(
          controller: nameController,
          decoration: InputDecoration(labelText: l10n.studioNewNameLabel),
          autofocus: true,
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(l10n.cancel),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, nameController.text),
            child: Text(l10n.save),
          ),
        ],
      ),
    );

    if (newName != null && newName.isNotEmpty && mounted) {
      // Optimistic UI handled by controller reloading? 
      // User requested optimistic UI in sidebar.
      // We can add a fake item "Copying..."
      final tempWf = original.copyWith(
        id: 'copying_${DateTime.now().millisecondsSinceEpoch}',
        name: newName,
      );
      
      setState(() {
        _optimisticWorkflows.add(tempWf);
      });

      try {
        await ref.read(studioControllerProvider.notifier).copyWorkflow(original.id, newName);
      } catch (e) {
        if (mounted) {
           ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Failed: $e')));
        }
      } finally {
        if (mounted) {
          setState(() {
            _optimisticWorkflows.remove(tempWf);
          });
        }
      }
    }
  }

  Future<void> _confirmDelete(BuildContext context, WorkflowDef wf) async {
    final l10n = AppLocalizations.of(context)!;
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(l10n.delete),
        content: Text('Are you sure you want to delete "${wf.name}"?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: Text(l10n.cancel),
          ),
          FilledButton(
            style: FilledButton.styleFrom(backgroundColor: Theme.of(context).colorScheme.error),
            onPressed: () => Navigator.pop(context, true),
            child: Text(l10n.delete),
          ),
        ],
      ),
    );

    if (confirmed == true && mounted) {
      try {
        await ref.read(studioControllerProvider.notifier).deleteWorkflow(wf.id);
        await ref.read(studioControllerProvider.notifier).loadWorkflows();
        
        if (mounted) {
           ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Deleted ${wf.name}')));
           // If deleted was selected, we should clear selection?
           if (widget.selectedStepId == wf.id) {
               // widget.onStepSelected(''); // Or handle upstream
           }
        }
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Failed to delete: $e')));
        }
      }
    }
  }
}

