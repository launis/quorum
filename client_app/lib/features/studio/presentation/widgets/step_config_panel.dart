import 'package:client_app/features/studio/domain/models/workflow_def.dart';
import 'package:client_app/features/studio/presentation/providers/studio_controller.dart';
import 'package:client_app/features/studio/presentation/widgets/dynamic_step_form.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class StepConfigPanel extends ConsumerWidget {
  final WorkflowStepDef? step;

  const StepConfigPanel({super.key, required this.step});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;

    if (step == null) {
      return Center(
        child: Text(
          l10n.studioSelectStepPrompt,
          style: Theme.of(context).textTheme.bodyLarge?.copyWith(
            color: Theme.of(context).colorScheme.outline,
          ),
        ),
      );
    }

    // "Step Configuration" (Localized) - fallback if key missing, but we assume it's studioConfigurationTitle
    final title = l10n.studioConfigurationTitle;

    return Card(
      margin: const EdgeInsets.all(16.0),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '$title: ${step!.name}',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: 8),
            Text(
              'Task: ${step!.taskKey}',
              style: Theme.of(context).textTheme.labelMedium,
            ),
            const Divider(height: 32),
            Expanded(
              child: SingleChildScrollView(
                child: DynamicStepForm(
                  config: step!.config,
                  onChanged: (key, value) {
                    // clone config + update
                    final newConfig = Map<String, dynamic>.from(step!.config);
                    newConfig[key] = value;

                    ref
                        .read(studioControllerProvider.notifier)
                        .updateStep(step!.id, newConfig);
                  },
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
