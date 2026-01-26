import 'package:client_app/features/studio/presentation/providers/studio_controller.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/studio/domain/models/workflow_def.dart';

class StudioSidebarList extends ConsumerWidget {
  final String? selectedStepId;
  final ValueChanged<String> onStepSelected;

  const StudioSidebarList({
    super.key,
    required this.selectedStepId,
    required this.onStepSelected,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(studioControllerProvider);
    final l10n = AppLocalizations.of(context)!;

    return state.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (err, st) => Center(child: Text('Error: $err')),
      data: (workflow) {
        if (workflow == null) return const SizedBox.shrink();

        final steps = workflow.steps;

        return Column(
          children: [
            Padding(
              padding: const EdgeInsets.symmetric(
                horizontal: 16.0,
                vertical: 8.0,
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    l10n.studioStepsTitle,
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  IconButton(
                    icon: const Icon(Icons.add),
                    onPressed: () {
                      // Add a new step logic
                      // For now, we can create a default step
                      final newStep = WorkflowStepDef(
                        id: 'step_${DateTime.now().millisecondsSinceEpoch}',
                        name: 'New Step',
                        taskKey: 'unknown',
                      );
                      ref
                          .read(studioControllerProvider.notifier)
                          .addStep(newStep);
                    },
                    tooltip: l10n.studioAddStepButton,
                  ),
                ],
              ),
            ),
            Expanded(
              child: ReorderableListView.builder(
                buildDefaultDragHandles: true,
                itemCount: steps.length,
                onReorder: (oldIndex, newIndex) {
                  ref
                      .read(studioControllerProvider.notifier)
                      .reorderSteps(oldIndex, newIndex);
                },
                itemBuilder: (context, index) {
                  final step = steps[index];
                  final isSelected = step.id == selectedStepId;

                  return ListTile(
                    key: ValueKey(step.id),
                    title: Text(step.name),
                    selected: isSelected,
                    selectedTileColor:
                        Theme.of(context).colorScheme.primaryContainer,
                    selectedColor:
                        Theme.of(context).colorScheme.onPrimaryContainer,
                    onTap: () => onStepSelected(step.id),
                    trailing: const Icon(Icons.drag_handle),
                  );
                },
              ),
            ),
          ],
        );
      },
    );
  }
}
