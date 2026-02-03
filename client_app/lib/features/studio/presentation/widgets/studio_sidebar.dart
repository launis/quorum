import 'package:client_app/features/studio/domain/models/component_def.dart';
import 'package:client_app/features/studio/domain/models/workflow_def.dart';
import 'package:client_app/features/studio/presentation/providers/studio_controller.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

enum StudioSidebarMode { workflows, matrices, components }

class StudioSidebar extends ConsumerStatefulWidget {
  final String? selectedStepId;
  final ValueChanged<String?> onStepSelected;
  final StudioSidebarMode mode;

  const StudioSidebar({
    super.key,
    required this.selectedStepId,
    required this.onStepSelected,
    this.mode = StudioSidebarMode.workflows,
  });

  @override
  ConsumerState<StudioSidebar> createState() => _StudioSidebarState();
}

class _StudioSidebarState extends ConsumerState<StudioSidebar> {
  // Optimistic items to display while saving
  final List<WorkflowDef> _optimisticWorkflows = [];
  final List<StudioComponentDef> _optimisticMatrices = [];

  @override
  void initState() {
    super.initState();
    // Data fetching is handled by the parent screen (WorkflowStudioScreen).
    // This widget should be purely presentation.
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(studioControllerProvider);
    final l10n = AppLocalizations.of(context)!;
    final colorScheme = Theme.of(context).colorScheme;

    return Container(
      width: 300,
      color: colorScheme.surfaceContainer,
      child: Column(
        children: [
          // Header
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
            child: Row(
               mainAxisAlignment: MainAxisAlignment.spaceBetween,
               children: [
                 Text(
                   widget.mode == StudioSidebarMode.workflows ? l10n.studioTabWorkflows : l10n.studioTabMatrices,
                   style: Theme.of(context).textTheme.titleMedium?.copyWith(
                     fontWeight: FontWeight.bold,
                   ),
                 ),
                 IconButton.filledTonal(
                   onPressed: _handleCreateNew,
                   icon: const Icon(Icons.add, size: 20),
                   tooltip: l10n.studioCreateNew,
                   visualDensity: VisualDensity.compact,
                 ),
               ]
            ),
          ),
          const Divider(height: 1),

          // Content Areas
          Expanded(
            child: widget.mode == StudioSidebarMode.workflows 
                ? _buildWorkflowsList(context, state, l10n)
                : _buildMatricesList(context, state, l10n),
          ),
        ],
      ),
    );
  }

  Widget _buildWorkflowsList(BuildContext context, StudioState state, AppLocalizations l10n) {
    return state.workflows.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (err, st) => _ErrorView(error: err),
      data: (workflows) {
        final allWorkflows = [...workflows, ..._optimisticWorkflows];
        if (allWorkflows.isEmpty) {
          return Center(child: Text(l10n.noWorkflowsAvailable));
        }

        return ListView.builder(
          itemCount: allWorkflows.length,
          itemBuilder: (context, index) {
            final wf = allWorkflows[index];
            final isSelected = wf.id == state.activeWorkflow.value?.id;
            final colorScheme = Theme.of(context).colorScheme;

            return ListTile(
              title: Text(wf.name),
              subtitle: Text(wf.id, style: const TextStyle(fontSize: 10)),
              selected: isSelected,
              selectedTileColor: colorScheme.primaryContainer,
              selectedColor: colorScheme.onPrimaryContainer,
              onTap: () {
                 ref.read(studioControllerProvider.notifier).loadWorkflow(wf.id);
                 widget.onStepSelected(null);
              },
              trailing: PopupMenuButton<String>(
                icon: const Icon(Icons.more_vert, size: 20),
                onSelected: (value) {
                  if (value == 'copy') _showCopyDialog(context, wf);
                  if (value == 'delete') _confirmDeleteWorkflow(context, wf);
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
    );
  }

  Widget _buildMatricesList(BuildContext context, StudioState state, AppLocalizations l10n) {
     return state.availableMatrices.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (err, st) => _ErrorView(error: err),
        data: (matrices) {
           final allMatrices = [...matrices, ..._optimisticMatrices];
           if (allMatrices.isEmpty) {
             return Center(child: Text("No matrices found. Create one!"));
           }

           return ListView.builder(
              itemCount: allMatrices.length,
              itemBuilder: (context, index) {
                final matrix = allMatrices[index];
                // Selection logic for matrices? For now just viewing.
                return ListTile(
                   leading: const Icon(Icons.grid_on, size: 20),
                   title: Text(matrix.name),
                   subtitle: Text(matrix.description ?? ''),
                   onTap: () { 
                       // Trigger selection in parent (which calls MatrixController)
                       widget.onStepSelected(matrix.id);
                   },
                );
              },
           );
        },
     );
  }

  void _handleCreateNew() {
    if (widget.mode == StudioSidebarMode.workflows) {
      _createNewWorkflow();
    } else {
      _createNewMatrix();
    }
  }

  Future<void> _createNewWorkflow() async {
    final tempId = 'new_${DateTime.now().millisecondsSinceEpoch}';
    final tempWf = WorkflowDef(id: tempId, name: 'New Workflow', description: '', steps: []);
    
    setState(() => _optimisticWorkflows.add(tempWf));

    try {
      await ref.read(studioControllerProvider.notifier).createWorkflow(tempWf);
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Failed: $e')));
    } finally {
      if (mounted) setState(() => _optimisticWorkflows.remove(tempWf));
    }
  }

  Future<void> _createNewMatrix() async {
     final l10n = AppLocalizations.of(context)!;
     final nameController = TextEditingController();
     final descController = TextEditingController();

     final result = await showDialog<Map<String, String>>(
        context: context,
        builder: (context) => AlertDialog(
           title: Text(l10n.studioCreateMatrix),
           content: Column(
             mainAxisSize: MainAxisSize.min,
             children: [
               TextField(
                 controller: nameController,
                 decoration: InputDecoration(labelText: l10n.studioMatrixName),
                 autofocus: true,
               ),
               const SizedBox(height: 8),
               TextField(
                 controller: descController,
                 decoration: InputDecoration(labelText: l10n.studioMatrixDesc),
               ),
             ],
           ),
           actions: [
             TextButton(onPressed: () => Navigator.pop(context), child: Text(l10n.cancel)),
             FilledButton(
               onPressed: () => Navigator.pop(context, {'name': nameController.text, 'desc': descController.text}),
               child: Text(l10n.save),
             ),
           ],
        ),
     );

     if (result != null && result['name']!.isNotEmpty) {
       final name = result['name']!;
       final desc = result['desc'] ?? '';
       
       final tempId = 'new_${DateTime.now().millisecondsSinceEpoch}';
       final tempMatrix = StudioComponentDef(id: tempId, name: name, type: 'evaluation_matrix', description: desc, content: {});
       
       setState(() => _optimisticMatrices.add(tempMatrix));

       try {
          await ref.read(studioControllerProvider.notifier).createMatrix(name, desc);
       } catch (e) {
         if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Failed: $e')));
       } finally {
         if (mounted) setState(() => _optimisticMatrices.remove(tempMatrix));
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
          TextButton(onPressed: () => Navigator.pop(context), child: Text(l10n.cancel)),
          FilledButton(onPressed: () => Navigator.pop(context, nameController.text), child: Text(l10n.save)),
        ],
      ),
    );

    if (newName != null && newName.isNotEmpty && mounted) {
      final tempWf = original.copyWith(id: 'copying...', name: newName);
      setState(() => _optimisticWorkflows.add(tempWf));

      try {
        await ref.read(studioControllerProvider.notifier).copyWorkflow(original.id, newName);
      } catch (e) {
        if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Failed: $e')));
      } finally {
        if (mounted) setState(() => _optimisticWorkflows.remove(tempWf));
      }
    }
  }

  Future<void> _confirmDeleteWorkflow(BuildContext context, WorkflowDef wf) async {
    final l10n = AppLocalizations.of(context)!;
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(l10n.delete),
        content: Text('Are you sure you want to delete "${wf.name}"?'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context, false), child: Text(l10n.cancel)),
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
        if (mounted) {
           ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Deleted ${wf.name}')));
           if (widget.selectedStepId == wf.id) {
               // widget.onStepSelected(null); // Optional
           }
        }
      } catch (e) {
        if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Failed to delete: $e')));
      }
    }
  }
}

class _ErrorView extends StatelessWidget {
  final Object error;
  const _ErrorView({required this.error});
  @override
  Widget build(BuildContext context) {
    return Container(
      color: Colors.red.shade100,
      padding: const EdgeInsets.all(8.0),
      child: Text('Error: $error', style: const TextStyle(color: Colors.red)),
    );
  }
}

