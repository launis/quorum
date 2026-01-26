import 'package:client_app/features/studio/presentation/providers/studio_controller.dart';
import 'package:client_app/features/studio/presentation/widgets/step_config_panel.dart';
import 'package:client_app/features/studio/presentation/widgets/studio_sidebar_list.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';

class WorkflowEditorScreen extends HookConsumerWidget {
  final String workflowId;

  const WorkflowEditorScreen({super.key, required this.workflowId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Local state for selected step
    final selectedStepId = useState<String?>(null);
    final l10n = AppLocalizations.of(context)!;

    // Load workflow on mount
    useEffect(() {
      // Defer to next frame to allow build to finish? Or safe to call?
      // Riverpod Notifier calls are safe in build? generally NO.
      // Use microtask.
      Future.microtask(() {
        ref.read(studioControllerProvider.notifier).loadWorkflow(workflowId);
      });
      return null;
    }, [workflowId]);

    final state = ref.watch(studioControllerProvider);

    return Scaffold(
      appBar: AppBar(
        title: Text(state.value?.name ?? 'Workflow Studio'),
        actions: [
          IconButton(
            icon: const Icon(Icons.save),
            tooltip: l10n.studioSaveButton,
            onPressed: () {
              ref.read(studioControllerProvider.notifier).save();
            },
          ),
        ],
      ),
      body: state.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (err, st) => Center(child: Text('Error: $err')),
        data: (workflow) {
          if (workflow == null) return const Center(child: Text('Loading...'));

          // Master-Detail Layout
          return Row(
            children: [
              // Sidebar
              SizedBox(
                width: 300,
                child: StudioSidebarList(
                  selectedStepId: selectedStepId.value,
                  onStepSelected: (id) => selectedStepId.value = id,
                ),
              ),
              const VerticalDivider(width: 1),
              // Detail Panel
              Expanded(
                child: StepConfigPanel(
                  step: workflow.steps.cast().firstWhere(
                    (s) => s.id == selectedStepId.value,
                    orElse: () => null,
                  ),
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}
