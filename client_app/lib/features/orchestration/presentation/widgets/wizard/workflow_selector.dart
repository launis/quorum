import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/orchestration/presentation/providers/wizard_provider.dart';

class WorkflowSelector extends ConsumerWidget {
  const WorkflowSelector({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final selectedId = ref.watch(
      wizardStateProvider.select((s) => s.selectedWorkflowId),
    );

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const Text(
          'Choose Analysis Type',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 16),
        _buildOption(
          context,
          ref,
          id: 'fused_audit_chain',
          title: 'Courtroom 3.0 (Fused)',
          description:
              'Optimized "Fused Critics" workflow for standard auditing.',
          icon: Icons.gavel,
          isSelected: selectedId == 'fused_audit_chain',
        ),
        const SizedBox(height: 12),
        _buildOption(
          context,
          ref,
          id: 'sequential_audit_chain',
          title: 'Courtroom 2.0 (Sequential)',
          description: 'Full sequential audit chain (legacy/deep mode).',
          icon: Icons.psychology,
          isSelected: selectedId == 'sequential_audit_chain',
        ),
        const SizedBox(height: 24),
        // Custom ID input fallback
        TextFormField(
          initialValue:
              [
                    'fused_audit_chain',
                    'sequential_audit_chain',
                  ].contains(selectedId)
                  ? ''
                  : selectedId,
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
