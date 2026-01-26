import 'package:client_app/features/studio/domain/models/workflow_def.dart';
import 'package:client_app/features/studio/presentation/providers/studio_controller.dart';
import 'package:client_app/features/studio/presentation/widgets/dynamic_config_form.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class StudioEditorArea extends ConsumerWidget {
  final String? selectedStepId;

  const StudioEditorArea({super.key, required this.selectedStepId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(studioControllerProvider);
    final l10n = AppLocalizations.of(context)!;

    return state.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (err, st) => Center(child: Text('Error loading editor: $err')),
      data: (workflow) {
        if (workflow == null) {
          return const Center(child: Text('No workflow loaded.'));
        }

        if (selectedStepId == null) {
          return Center(
            child: Text(
              l10n.studioSelectStepPrompt,
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                color: Theme.of(context).colorScheme.onSurfaceVariant,
              ),
            ),
          );
        }

        // Find the selected step safely
        final selectedStep = workflow.steps.cast<WorkflowStepDef?>().firstWhere(
          (step) => step?.id == selectedStepId,
          orElse: () => null,
        );

        if (selectedStep == null) {
          return Center(child: Text(l10n.errorNotFound));
        }

        return Card(
          margin: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header
              Padding(
                padding: const EdgeInsets.all(16.0),
                child: Text(
                  'Configuration: ${selectedStep.name}',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
              ),
              const Divider(height: 1),

              // Dynamic Form
              Expanded(
                child: DynamicConfigForm(
                  config: selectedStep.config,
                  onFieldChanged: (key, value) {
                    final newConfig = Map<String, dynamic>.from(
                      selectedStep.config,
                    );
                    newConfig[key] = value;

                    ref
                        .read(studioControllerProvider.notifier)
                        .updateStep(selectedStep.id, newConfig);
                  },
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}
