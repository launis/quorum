import 'package:client_app/features/orchestration/domain/models/workflow.dart';
import 'package:client_app/features/orchestration/presentation/providers/workflow_controller.dart';
import 'package:client_app/features/orchestration/presentation/providers/wizard_provider.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/core/ui/error_view.dart';

class WorkflowSelector extends ConsumerWidget {
  const WorkflowSelector({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final selectedId = ref.watch(
      wizardStateProvider.select((s) => s.selectedWorkflowId),
    );
    final workflowsAsync = ref.watch(workflowListProvider);
    final l10n = AppLocalizations.of(context)!;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        workflowsAsync.when(
          data: (workflows) {
            final items =
                workflows.map((wf) {
                  return DropdownMenuItem<String>(
                    value: wf.id,
                    child: Text(wf.name),
                  );
                }).toList();

            return InputDecorator(
              decoration: InputDecoration(
                labelText: l10n.chooseAnalysisType,
                border: const OutlineInputBorder(),
                prefixIcon: const Icon(Icons.settings_applications),
                contentPadding: const EdgeInsets.symmetric(
                  horizontal: 12.0,
                  vertical: 4.0,
                ),
              ),
              child: DropdownButtonHideUnderline(
                child: DropdownButton<String>(
                  value:
                      _isValidSelection(selectedId, workflows)
                          ? selectedId
                          : null,
                  items: items,
                  onChanged: (value) {
                    if (value != null) {
                      ref
                          .read(wizardStateProvider.notifier)
                          .selectWorkflow(value);
                    }
                  },
                  isExpanded: true,
                ),
              ),
            );
          },
          loading: () => const LinearProgressIndicator(),
          error:

              (err, stack) => ErrorView(
                error: err,
                compact: true,
                onRetry: () => ref.invalidate(workflowListProvider),
                retryLabel: l10n.retry,
              ),
        ),

        // Optional: Custom ID entry (hidden if regular selection is made, or always visible as advanced?)
        // Let's keep it simple for now as requested.
      ],
    );
  }

  bool _isValidSelection(String? id, List<Workflow> workflows) {
    if (id == null) return false;
    return workflows.any((w) => w.id == id);
  }
}
