import 'package:client_app/core/error/app_error.dart';
import 'package:file_picker/file_picker.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:client_app/features/orchestration/presentation/providers/wizard_provider.dart';
import 'package:client_app/features/orchestration/presentation/providers/execution_controller.dart';
import 'package:client_app/features/orchestration/presentation/widgets/wizard/workflow_selector.dart';
import 'package:client_app/features/orchestration/presentation/widgets/wizard/dynamic_input_form.dart';
import 'package:client_app/features/orchestration/presentation/providers/workflow_controller.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:collection/collection.dart';

class AnalysisWizardScreen extends ConsumerWidget {
  const AnalysisWizardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    // 1. Passive View Listener
    // Watch executionControllerProvider for side-effects (Success/Error)
    ref.listen(executionControllerProvider, (previous, next) {
      if (next is AsyncError) {
        final error = next.error;
        // Strictly localize
        String message = l10n.errorUnknown;

        if (error is AppError) {
          error.when(
            unknown: (_, _) => message = l10n.errorUnknown,
            network: (_) => message = l10n.errorNetwork,
            server:
                (msg, _) =>
                    message = msg ?? l10n.errorServer, // Fallback if msg null
            unauthorized: () => message = l10n.errorUnauthorized,
            notFound: (_) => message = l10n.errorNotFound,
            cancelled: () {}, // No-op
            validation: (reason) {
              switch (reason) {
                case ValidationErrorReason.emptyInput:
                  message = l10n.errorValidationEmpty;
                  break;
                default:
                  message = l10n.errorValidation;
              }
            },
            validationMissing:
                (fields) =>
                    message = l10n.errorValidationMissing(fields.join(', ')),
            api: (errorCode, detail, status, instance) {
              // RFC 7807 error - use detail as message
              message = detail;
            },
          );
        }

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(message),
            backgroundColor: Theme.of(context).colorScheme.error,
          ),
        );
      } else if (previous?.isLoading == true && next is AsyncData) {
        // Success Transition: Loading -> Data
        // Success handled in _submit via returned ID to prevent race condition.
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text(l10n.analysisStarted)));
      }
    });

    // Check loading state from controller, not wizardState (which mixes concerns)
    final executionState = ref.watch(executionControllerProvider);
    final isSubmitting = executionState.isLoading;

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
                    onPressed: isSubmitting ? null : () => _submit(context, ref),
                    icon:
                        isSubmitting
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
                      isSubmitting
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
    final logger = ref.read(loggerServiceProvider);
    
    try {
      logger.info('AnalysisWizard', 'Submit pressed');
      final wizardState = ref.read(wizardStateProvider);
      final workflowList = ref.read(workflowListProvider);

      // Find selected workflow to determine required inputs
      final workflow =
          workflowList.asData?.value
              .where((w) => w.id == wizardState.selectedWorkflowId)
              .firstOrNull;
      
      if (workflow == null) {
         logger.warning('AnalysisWizard', 'Workflow not found for ID: ${wizardState.selectedWorkflowId}');
         ScaffoldMessenger.of(ref.context).showSnackBar(
           const SnackBar(content: Text('Error: Invalid Workflow Selection. Please refresh.')),
         );
         return;
      }

      logger.info('AnalysisWizard', 'Selected workflow: ${workflow.id}');

      // Determine Required Keys based on Schema OR Fallback
      final List<String> requiredInputs;
      if (workflow.uiSchema?.isNotEmpty ?? false) {
        // Exclude system fields like 'default_model_mapping' which are configuration, not user inputs
        requiredInputs = workflow.uiSchema!.keys
            .where((k) => k != 'default_model_mapping')
            .toList();
      } else {
        requiredInputs = [];
      }
      
      logger.debug('AnalysisWizard', 'Required inputs: $requiredInputs');
      
      // Sanitize inputs for logging (avoid printing file bytes)
      final sanitizedInputs = wizardState.inputs.map((key, value) {
        if (value is PlatformFile) {
          return MapEntry(key, 'File: ${value.name} (${value.size} bytes)');
        }
        return MapEntry(key, value);
      });
      logger.debug('AnalysisWizard', 'Current inputs: $sanitizedInputs');

      // Delegate strictly to Controller.
      // Validation is handled inside startAnalysis (Fail-fast).
      // Navigation is now handled explicitly here using the returned ID.

      final executionId = await ref
          .read(executionControllerProvider.notifier)
          .startAnalysis(
            workflowId: wizardState.selectedWorkflowId,
            inputs: wizardState.inputs,
            requiredInputs: requiredInputs,
          );
      
      logger.info('AnalysisWizard', 'StartAnalysis returned ID: $executionId');
      
      if (executionId != null && context.mounted) {
        // Explicit navigation to the NEW execution
        context.go('/dashboard/executions/$executionId');
      }
    } catch (e, stack) {
      logger.error('AnalysisWizard', 'Error in _submit', e, stack);
      // Ensure specific errors are rethrown or handled if not by ref.listen
       if (context.mounted) {
         ScaffoldMessenger.of(context).showSnackBar(
             SnackBar(content: Text('Submission Error: $e')),
         );
       }
    }
  }
}
