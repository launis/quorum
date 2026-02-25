// ignore_for_file: deprecated_member_use
import 'package:client_app/features/studio/presentation/providers/matrix_controller.dart';
import 'package:client_app/features/studio/presentation/providers/active_workflow_controller.dart';
import 'package:client_app/features/studio/presentation/widgets/matrix_editor_panel.dart';
import 'package:client_app/features/studio/presentation/widgets/ontology_manager_panel.dart';
import 'package:client_app/features/studio/presentation/widgets/studio_editor_area.dart';
import 'package:client_app/features/studio/presentation/widgets/steps_manager_panel.dart';
import 'package:client_app/features/studio/presentation/widgets/components_manager_panel.dart';
import 'package:client_app/features/studio/presentation/widgets/studio_sidebar.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:go_router/go_router.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';

class WorkflowStudioScreen extends HookConsumerWidget {
  final String? workflowId;
  final int initialTabIndex;

  const WorkflowStudioScreen({
    super.key,
    this.workflowId,
    this.initialTabIndex = 0,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // 1. Local State
    final selectedStepId = useState<String?>(null);
    final l10n = AppLocalizations.of(context)!;
    final activeWorkflowState = ref.watch(activeWorkflowControllerProvider);

    // 2. Initial Data Loading
    useEffect(() {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        // Deep link specific workflow if provided
        if (workflowId != null && initialTabIndex == 0) {
          ref.read(activeWorkflowControllerProvider.notifier).loadWorkflow(workflowId!);
        }
      });
      return null;
    }, [workflowId, initialTabIndex]);

    // 3. Feedback Listener
    ref.listen(activeWorkflowControllerProvider, (previous, next) {
      // Error Feedback
      if (next.hasError && !next.isLoading) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error: ${next.error}'),
            backgroundColor: Theme.of(context).colorScheme.error,
          ),
        );
      }
    });

    return Scaffold(
      appBar: AppBar(
        title: const Text("Cognitive Studio"),
        leading: BackButton(onPressed: () => context.go('/studio')),
        actions: [
          // Run Test Button
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 8.0),
            child: OutlinedButton.icon(
              icon: const Icon(Icons.play_arrow),
              label: Text(l10n.studioRunTest),
              onPressed: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Test run started (Mock)')),
                );
              },
            ),
          ),

          // Save Button
          Padding(
            padding: const EdgeInsets.only(right: 16.0, left: 8.0),
            child:
                activeWorkflowState.isLoading
                    ? const Row(
                      children: [
                        SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        ),
                        SizedBox(width: 8),
                        Text("Saving..."), // Fallback or use l10n.studioSaving
                      ],
                    )
                    : FilledButton.icon(
                      icon: const Icon(Icons.save),
                      label: Text(l10n.save),
                      onPressed: () async {
                        await ref.read(activeWorkflowControllerProvider.notifier).save();
                        if (context.mounted) {
                           ScaffoldMessenger.of(context).showSnackBar(
                             SnackBar(content: Text(l10n.studioChangesSaved), duration: const Duration(seconds: 2))
                           );
                        }
                      },
                    ),
          ),
        ],
      ),
      // 4. Split View Layout (Desktop First)
      // 4. Split View Layout (Desktop First)
      body: initialTabIndex == 2 
            ? const StepsManagerPanel()
            : initialTabIndex == 3
                ? const ComponentsManagerPanel()
                : Row(
        children: [
          StudioSidebar(
            selectedStepId: selectedStepId.value,
            onStepSelected: (id) {
              selectedStepId.value = id;
              // If in Matrix Mode, select the matrix in the controller
              if (initialTabIndex == 1 && id != null) {
                ref.read(matrixControllerProvider.notifier).selectMatrix(id);
              }
            },
            mode:
                initialTabIndex == 0
                    ? StudioSidebarMode.workflows
                    : StudioSidebarMode.matrices,
          ),
          const VerticalDivider(width: 1),
          // Content Area
          Expanded(
            child:
                initialTabIndex == 1
                    ? const Row(
                      children: [
                        Expanded(flex: 5, child: MatrixEditorPanel()),
                        VerticalDivider(width: 1),
                        Expanded(flex: 3, child: OntologyManagerPanel()),
                      ],
                    )
                    : StudioEditorArea(
                        selectedStepId: selectedStepId.value,
                        onStepSelected: (id) => selectedStepId.value = id,
                      ),
          ),
        ],
      ),
    );
  }
}
