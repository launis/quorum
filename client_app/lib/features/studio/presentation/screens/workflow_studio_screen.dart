import 'package:client_app/features/studio/presentation/providers/studio_controller.dart';
import 'package:client_app/features/studio/presentation/widgets/studio_editor_area.dart';
import 'package:client_app/features/studio/presentation/widgets/studio_sidebar.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';

class WorkflowStudioScreen extends HookConsumerWidget {
  final String? workflowId;

  const WorkflowStudioScreen({super.key, this.workflowId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // 1. Local State
    final selectedStepId = useState<String?>(null);
    final l10n = AppLocalizations.of(context)!;
    final studioState = ref.watch(studioControllerProvider);

    // 2. Initial Data Loading (useEffect similar to initState)
    useEffect(() {
      if (workflowId != null) {
        // Run after build
        Future.microtask(() {
          ref.read(studioControllerProvider.notifier).loadWorkflow(workflowId!);
        });
      }
      return null;
    }, [workflowId]);

    // 3. Feedback Listener
    ref.listen(studioControllerProvider, (previous, next) {
      // Error Feedback
      if (next.hasError && !next.isLoading) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error: ${next.error}'),
            backgroundColor: Theme.of(context).colorScheme.error,
          ),
        );
      }

      // Success Feedback (Saved)
      // Check transition from loading to data, but we need to know if it was a SAVE operation?
      // Simple heuristic: If it was loading and now isn't, and no error.
      // Ideally controller would expose specific statuse (isSaving), but AsyncValue is generic.
      // For now, simple transition check is accepted for "Optimistic UI" feedback.
      if (previous?.isLoading == true && !next.isLoading && !next.hasError) {
        // Optional: Only show if we know data changed?
        // Logic: Controller.save() sets loading.
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(l10n.studioChangesSaved),
            duration: const Duration(seconds: 2),
          ),
        );
      }
    });

    return Scaffold(
      appBar: AppBar(
        title: const Text("Cognitive Studio"),
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
            child: studioState.isLoading
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
                    onPressed: () {
                      ref.read(studioControllerProvider.notifier).save();
                    },
                  ),
          ),
        ],
      ),
      // 4. Split View Layout (Desktop First)
      body: Row(
        children: [
          StudioSidebar(
            selectedStepId: selectedStepId.value,
            onStepSelected: (id) => selectedStepId.value = id,
          ),
          const VerticalDivider(width: 1),
          Expanded(
            child: StudioEditorArea(selectedStepId: selectedStepId.value),
          ),
        ],
      ),
    );
  }
}
