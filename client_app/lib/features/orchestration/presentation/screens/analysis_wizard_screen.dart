import 'package:client_app/l10n/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:client_app/features/orchestration/presentation/providers/wizard_provider.dart';
import 'package:client_app/features/orchestration/presentation/providers/execution_controller.dart';
import 'package:client_app/features/orchestration/presentation/widgets/wizard/workflow_selector.dart';
import 'package:client_app/features/orchestration/presentation/widgets/wizard/dynamic_input_form.dart';

class AnalysisWizardScreen extends ConsumerWidget {
  const AnalysisWizardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final wizardState = ref.watch(wizardStateProvider);
    final l10n = AppLocalizations.of(context)!;
    // Keep controller alive during async operations
    ref.watch(executionControllerProvider);
    // final theme = Theme.of(context); // Unused for now

    // Listen for global execution errors or success if needed,
    // but typically we await the future in the button callback.

    return Scaffold(
      appBar: AppBar(title: Text(l10n.newAnalysis)),
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 1000),
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // 1. Selector
                const WorkflowSelector(),

                const SizedBox(height: 32),

                // 2. Inputs (Dynamically rendered based on selection)
                const DynamicInputForm(),

                const SizedBox(height: 48),

                // 3. Submit Action
                SizedBox(
                  height: 50,
                  child: FilledButton.icon(
                    onPressed:
                        wizardState.isSubmitting
                            ? null
                            : () => _submit(context, ref),
                    icon:
                        wizardState.isSubmitting
                            ? const SizedBox(
                              width: 24,
                              height: 24,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                color: Colors.white,
                              ),
                            )
                            : const Icon(Icons.rocket_launch),
                    label: Text(
                      wizardState.isSubmitting
                          ? l10n.analysisInProgress
                          : l10n.startAnalysis,
                      style: const TextStyle(fontSize: 16),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Future<void> _submit(BuildContext context, WidgetRef ref) async {
    final notifier = ref.read(wizardStateProvider.notifier);
    // Use read, not watch/of for async context usage is safer with mounted check
    // But we need l10n to show messages.
    // It's safe to grab it before await, or if context is mounted after await.

    // Call provider method (handles state validation and API call)
    final executionId = await notifier.submitAnalysis();

    if (context.mounted) {
      final l10n = AppLocalizations.of(context)!;
      if (executionId != null && executionId.isNotEmpty) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text(l10n.analysisStarted)));
        context.go('/dashboard/executions/$executionId/monitor');
      } else {
        // Handle Failure
        // Check if it was validation error (inputs empty) or API error
        final state = ref.read(wizardStateProvider);
        if (state.inputs.isEmpty) {
          ScaffoldMessenger.of(
            context,
          ).showSnackBar(SnackBar(content: Text(l10n.fillRequiredInputs)));
        } else {
          final errorMsg = state.error ?? 'Error';
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(l10n.submissionFailed(errorMsg)),
              backgroundColor: Colors.red,
              duration: const Duration(seconds: 5),
            ),
          );
        }
      }
    }
  }
}
