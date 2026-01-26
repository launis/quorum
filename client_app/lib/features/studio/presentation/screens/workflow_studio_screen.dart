import 'package:client_app/features/studio/data/studio_repository.dart';
import 'package:client_app/features/studio/domain/models/workflow_summary.dart';
import 'package:client_app/features/studio/presentation/providers/studio_workflow_controller.dart';
import 'package:client_app/features/studio/presentation/widgets/sdui/schema_form_builder.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'workflow_studio_screen.g.dart';

// Local provider for fetching the list
@riverpod
Future<List<WorkflowSummary>> studioWorkflowList(Ref ref) {
  return ref.watch(studioRepositoryProvider).fetchWorkflows();
}

class WorkflowStudioScreen extends ConsumerStatefulWidget {
  final String? workflowId; // from route params if any

  const WorkflowStudioScreen({super.key, this.workflowId});

  @override
  ConsumerState<WorkflowStudioScreen> createState() =>
      _WorkflowStudioScreenState();
}

class _WorkflowStudioScreenState extends ConsumerState<WorkflowStudioScreen> {
  String? _selectedId;

  @override
  void initState() {
    super.initState();
    _selectedId = widget.workflowId;
  }

  @override
  void didUpdateWidget(covariant WorkflowStudioScreen oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.workflowId != oldWidget.workflowId) {
      _selectedId = widget.workflowId;
    }
  }

  void _onSelect(String id) {
    setState(() => _selectedId = id);
    // On narrow screens (or generally if we want URL sync), we should navigate.
    // For now, internal state update is fine for Split View logic.
    // If we want deep linking, we'd use context.go('/studio/workflow/$id')
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Workflow Studio')),
      body: LayoutBuilder(
        builder: (context, constraints) {
          final isWide = constraints.maxWidth > 800;

          if (isWide) {
            return Row(
              children: [
                Expanded(
                  flex: 1,
                  child: WorkflowList(
                    selectedId: _selectedId,
                    onTap: _onSelect,
                  ),
                ),
                const VerticalDivider(width: 1),
                Expanded(
                  flex: 2,
                  child:
                      _selectedId == null
                          ? const Center(child: Text('Select a workflow'))
                          : KeyedSubtree(
                            key: ValueKey(_selectedId),
                            child: WorkflowEditor(workflowId: _selectedId!),
                          ),
                ),
              ],
            );
          } else {
            // Narrow screen: Show List. If ID selected, ideally push route.
            // For MVP within this screen, we can toggle view.
            if (_selectedId != null) {
              return PopScope(
                canPop: false,
                onPopInvokedWithResult: (didPop, _) {
                  if (didPop) return;
                  setState(() => _selectedId = null);
                },
                child: WorkflowEditor(workflowId: _selectedId!),
              );
            }
            return WorkflowList(selectedId: _selectedId, onTap: _onSelect);
          }
        },
      ),
    );
  }
}

class WorkflowList extends ConsumerWidget {
  final String? selectedId;
  final ValueChanged<String> onTap;

  const WorkflowList({
    super.key,
    required this.selectedId,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final listAsync = ref.watch(studioWorkflowListProvider);

    return listAsync.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (err, st) => Center(child: Text('Error: $err')),
      data: (workflows) {
        if (workflows.isEmpty) {
          return const Center(child: Text('No workflows found.'));
        }
        return ListView.separated(
          itemCount: workflows.length,
          separatorBuilder: (_, __) => const Divider(),
          itemBuilder: (context, index) {
            final wf = workflows[index];
            final isSelected = wf.id == selectedId;
            return ListTile(
              title: Text(wf.name),
              subtitle: Text(wf.description ?? ''),
              selected: isSelected,
              onTap: () => onTap(wf.id),
              trailing: const Icon(Icons.chevron_right),
            );
          },
        );
      },
    );
  }
}

class WorkflowEditor extends ConsumerWidget {
  final String workflowId;

  const WorkflowEditor({super.key, required this.workflowId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final stateAsync = ref.watch(studioWorkflowControllerProvider(workflowId));
    final controller = ref.read(
      studioWorkflowControllerProvider(workflowId).notifier,
    );

    return stateAsync.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (err, st) => Center(child: SelectableText('Error: $err\n$st')),
      data: (state) {
        if (state.schema == null || state.data == null) {
          return const Center(child: Text('Missing schema or data.'));
        }

        return Scaffold(
          appBar: AppBar(
            automaticallyImplyLeading: false, // Handled by parent
            title: Text(state.data!['name'] ?? 'Editor'),
            actions: [
              if (state.isSaving)
                const Padding(
                  padding: EdgeInsets.all(16.0),
                  child: SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  ),
                ),
              if (!state.isSaving && state.lastError == null)
                const Padding(
                  padding: EdgeInsets.all(16.0),
                  child: Icon(Icons.check_circle, color: Colors.green),
                ),
              if (state.lastError != null)
                const Padding(
                  padding: EdgeInsets.all(16.0),
                  child: Icon(Icons.error, color: Colors.red),
                ),
            ],
          ),
          body: Column(
            children: [
              if (state.lastError != null)
                Container(
                  color: Colors.red.shade100,
                  padding: const EdgeInsets.all(8),
                  width: double.infinity,
                  child: Text(
                    state.lastError!,
                    style: const TextStyle(color: Colors.red),
                  ),
                ),
              Expanded(
                child: SingleChildScrollView(
                  padding: const EdgeInsets.all(16.0),
                  child: SchemaFormBuilder(
                    schema: state.schema!,
                    initialData: state.data!,
                    onChanged: (newData) {
                      controller.save(newData);
                    },
                  ),
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}
