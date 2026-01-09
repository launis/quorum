import 'package:client_app/features/orchestration/presentation/providers/workflow_controller.dart';
import 'package:client_app/features/orchestration/presentation/providers/wizard_provider.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class WorkflowSelector extends ConsumerWidget {
  const WorkflowSelector({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final selectedId = ref.watch(
      wizardStateProvider.select((s) => s.selectedWorkflowId),
    );
    final workflowsAsync = ref.watch(workflowListProvider);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const Text(
          'Choose Analysis Type',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 16),

        // Dynamic List
        workflowsAsync.when(
          data: (workflows) {
            if (workflows.isEmpty) {
              return const Text('No workflows available for your account.');
            }
            return Column(
              children:
                  workflows.map((wf) {
                    return Padding(
                      padding: const EdgeInsets.only(bottom: 12),
                      child: _buildOption(
                        context,
                        ref,
                        id: wf.id,
                        title: wf.name,
                        description:
                            wf.description.isNotEmpty
                                ? wf.description
                                : 'Custom workflow.',
                        // Mapping standard icons based on known IDs or fallback
                        icon: _getIconForWorkflow(wf.id),
                        isSelected: selectedId == wf.id,
                      ),
                    );
                  }).toList(),
            );
          },
          loading: () => const Center(child: CircularProgressIndicator()),
          error:
              (err, stack) => Text(
                'Error loading workflows: $err',
                style: const TextStyle(color: Colors.red),
              ),
        ),

        const SizedBox(height: 24),

        // Custom ID input fallback (Always available)
        TextFormField(
          initialValue:
              // Only show text if it's NOT one of the list options
              // This is tricky if lists are async.
              // Simplification: If selectedId starts with 'wf_' or standard IDs, hide it.
              // Or just always show empty unless user types here.
              '',
          decoration: const InputDecoration(
            labelText: 'Or enter Custom Workflow ID',
            border: OutlineInputBorder(),
            prefixIcon: Icon(Icons.code),
          ),
          onChanged: (value) {
            if (value.isNotEmpty) {
              ref.read(wizardStateProvider.notifier).selectWorkflow(value);
            }
          },
        ),
      ],
    );
  }

  IconData _getIconForWorkflow(String id) {
    if (id.contains('fused')) return Icons.gavel;
    if (id.contains('sequential')) return Icons.psychology;
    return Icons.settings_applications;
  }

  Widget _buildOption(
    BuildContext context,
    WidgetRef ref, {
    required String id,
    required String title,
    required String description,
    required IconData icon,
    required bool isSelected,
  }) {
    final theme = Theme.of(context);
    final color =
        isSelected
            ? theme.colorScheme.primary
            : theme.colorScheme.surfaceContainer;
    final textColor =
        isSelected ? theme.colorScheme.onPrimary : theme.colorScheme.onSurface;
    final subTextColor =
        isSelected
            ? theme.colorScheme.onPrimary.withValues(alpha: 0.8)
            : theme.colorScheme.onSurfaceVariant;

    return Card(
      color: color,
      elevation: isSelected ? 4 : 1,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side:
            isSelected
                ? BorderSide.none
                : BorderSide(color: theme.colorScheme.outlineVariant),
      ),
      child: InkWell(
        onTap: () => ref.read(wizardStateProvider.notifier).selectWorkflow(id),
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Row(
            children: [
              Icon(
                icon,
                color:
                    isSelected
                        ? theme.colorScheme.onPrimary
                        : theme.colorScheme.primary,
                size: 32,
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: theme.textTheme.titleMedium?.copyWith(
                        color: textColor,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      description,
                      style: theme.textTheme.bodyMedium?.copyWith(
                        color: subTextColor,
                      ),
                    ),
                  ],
                ),
              ),
              if (isSelected)
                Icon(Icons.check_circle, color: theme.colorScheme.onPrimary),
            ],
          ),
        ),
      ),
    );
  }
}
