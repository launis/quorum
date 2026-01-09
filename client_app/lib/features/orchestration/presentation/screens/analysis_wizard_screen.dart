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
    // Keep controller alive during async operations
    ref.watch(executionControllerProvider);
    // final theme = Theme.of(context); // Unused for now

    // Listen for global execution errors or success if needed,
    // but typically we await the future in the button callback.

    return Scaffold(
      appBar: AppBar(title: const Text('New Analysis')),
      body: Stepper(
        type: StepperType.horizontal,
        currentStep: wizardState.currentStep,
        onStepCancel: () {
          if (wizardState.currentStep > 0) {
            ref
                .read(wizardStateProvider.notifier)
                .setStep(wizardState.currentStep - 1);
          } else {
            if (context.canPop()) {
              context.pop();
            } else {
              context.go('/dashboard');
            }
          }
        },
        onStepContinue: () {
          // Validate current step
          final current = wizardState.currentStep;
          if (current == 0) {
            // Step 1: Workflow Selection
            ref.read(wizardStateProvider.notifier).setStep(1);
          } else if (current == 1) {
            // Step 2: Inputs -> SUbmit directly
            final inputs = wizardState.inputs;
            if (inputs.isEmpty) {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Please fill in required inputs.'),
                ),
              );
              return;
            }
            _submit(context, ref);
          }
        },
        controlsBuilder: (context, details) {
          final isLast = wizardState.currentStep == 1;
          return Padding(
            padding: const EdgeInsets.only(top: 24.0),
            child: Row(
              children: [
                FilledButton(
                  onPressed:
                      wizardState.isSubmitting ? null : details.onStepContinue,
                  child:
                      wizardState.isSubmitting
                          ? const SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              color: Colors.white,
                            ),
                          )
                          : Text(isLast ? 'Start Analysis' : 'Next'),
                ),
                const SizedBox(width: 12),
                TextButton(
                  onPressed:
                      wizardState.isSubmitting ? null : details.onStepCancel,
                  child: Text(wizardState.currentStep == 0 ? 'Cancel' : 'Back'),
                ),
              ],
            ),
          );
        },
        steps: [
          Step(
            title: const Text('Type'),
            isActive: wizardState.currentStep >= 0,
            state:
                wizardState.currentStep > 0
                    ? StepState.complete
                    : StepState.editing,
            content: const WorkflowSelector(),
          ),
          Step(
            title: const Text('Inputs'),
            isActive: wizardState.currentStep >= 1,
            state: StepState.editing,
            content: const DynamicInputForm(),
          ),
        ],
      ),
    );
  }

  Future<void> _submit(BuildContext context, WidgetRef ref) async {
    final state = ref.read(wizardStateProvider);
    final notifier = ref.read(wizardStateProvider.notifier);

    notifier.setSubmitting(true);
    notifier.setError(null);

    try {
      final executionId = await ref
          .read(executionControllerProvider.notifier)
          .startAnalysis(
            workflowId: state.selectedWorkflowId,
            inputs: state.inputs,
          );

      if (context.mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(const SnackBar(content: Text('Analysis Started!')));

        if (executionId != null && executionId.isNotEmpty) {
          context.go('/dashboard/executions/$executionId/monitor');
        } else {
          // FIX: Do not silently fail. Show error from controller.
          final errorState = ref.read(executionControllerProvider);
          final errorMsg =
              errorState.error?.toString() ??
              'Unknown Error: Execution ID was null';

          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Submission Failed: $errorMsg'),
              backgroundColor: Colors.red,
              duration: const Duration(seconds: 5),
            ),
          );
        }
      }
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e'), backgroundColor: Colors.red),
        );
        notifier.setError(e.toString());
      }
    } finally {
      notifier.setSubmitting(false);
    }
  }
}
