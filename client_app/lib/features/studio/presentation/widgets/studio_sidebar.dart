import 'package:client_app/features/studio/domain/models/workflow_def.dart';
import 'package:client_app/features/studio/presentation/providers/studio_controller.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class StudioSidebar extends ConsumerWidget {
  final String? selectedStepId;
  final ValueChanged<String> onStepSelected;

  const StudioSidebar({
    super.key,
    required this.selectedStepId,
    required this.onStepSelected,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(studioControllerProvider);
    final l10n = AppLocalizations.of(context)!;
    final colorScheme = Theme.of(context).colorScheme;

    return Container(
      width: 300,
      color: colorScheme.surfaceContainer,
      child: Column(
        children: [
          // Header Row
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  l10n.studioStepsHeader,
                  style: Theme.of(context).textTheme.titleMedium,
                ),
                IconButton.filledTonal(
                  icon: const Icon(Icons.add),
                  tooltip: l10n.studioAddStep,
                  onPressed: () {
                    final newStep = WorkflowStepDef(
                      id: 'step_${DateTime.now().millisecondsSinceEpoch}',
                      name: 'New Step',
                      taskKey: 'unknown',
                    );
                    ref
                        .read(studioControllerProvider.notifier)
                        .addStep(newStep);
                  },
                ),
              ],
            ),
          ),
          const Divider(height: 1),

          // Reorderable List
          Expanded(
            child: state.when(
              // Loading State (Shimmer or Spinner)
              loading: () => const Center(child: CircularProgressIndicator()),

              // Error State
              error:
                  (err, st) => Center(
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Text(
                        err.toString(),
                        style: TextStyle(color: colorScheme.error),
                      ),
                    ),
                  ),

              // Data State
              data: (workflow) {
                if (workflow == null) return const SizedBox.shrink();
                final steps = workflow.steps;

                if (steps.isEmpty) {
                  return Center(
                    child: Text(
                      l10n.studioNoSteps,
                      style: TextStyle(color: colorScheme.outline),
                    ),
                  );
                }

                return ReorderableListView.builder(
                  buildDefaultDragHandles: false, // Custom handle
                  itemCount: steps.length,
                  onReorder: (oldIndex, newIndex) {
                    ref
                        .read(studioControllerProvider.notifier)
                        .reorderSteps(oldIndex, newIndex);
                  },
                  itemBuilder: (context, index) {
                    final step = steps[index];
                    final isSelected = step.id == selectedStepId;

                    return _SidebarStepItem(
                      key: ValueKey(step.id),
                      step: step,
                      isSelected: isSelected,
                      index: index,
                      onTap: () => onStepSelected(step.id),
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
}

class _SidebarStepItem extends StatelessWidget {
  final WorkflowStepDef step;
  final bool isSelected;
  final int index;
  final VoidCallback onTap;

  const _SidebarStepItem({
    super.key,
    required this.step,
    required this.isSelected,
    required this.index,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Material(
      color:
          isSelected
              ? colorScheme.primaryContainer
              : Colors.transparent, // Default bg handled by parent container
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 12.0),
          child: Row(
            children: [
              // Reorder Handle
              ReorderableDragStartListener(
                index: index,
                child: MouseRegion(
                  cursor: SystemMouseCursors.grab,
                  child: Icon(Icons.drag_handle, color: colorScheme.outline),
                ),
              ),
              const SizedBox(width: 12),
              // Step Name
              Expanded(
                child: Text(
                  step.name.isNotEmpty ? step.name : step.id,
                  style: TextStyle(
                    fontWeight:
                        isSelected ? FontWeight.bold : FontWeight.normal,
                    color:
                        isSelected
                            ? colorScheme.onPrimaryContainer
                            : colorScheme.onSurface,
                  ),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
