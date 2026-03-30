import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/studio/controllers/studio_controller.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/router/router.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/features/studio/views/components/clone_entity_button.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/logging/logger_service.dart';

/// Flat MVC List view for Workflows (DAG definitions).
/// Adheres strictly to De-Generator constraints using List<Workflow>.
class WorkflowsMasterView extends ConsumerWidget {
  const WorkflowsMasterView({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final workflowsState = ref.watch(workflowsControllerProvider);

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                l10n.studioViewsWorkflowBuilderTitle,
                style: Theme.of(context).textTheme.titleLarge,
              ),
              FilledButton.icon(
                onPressed: () {
                  const WorkflowNewRoute().go(context);
                },
                icon: const Icon(Icons.account_tree),
                label: Text(l10n.studioViewsNewWorkflowBtn),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            l10n.studioViewsWorkflowBuilderDesc,
            style: Theme.of(context).textTheme.bodyMedium,
          ),
          const SizedBox(height: 16),
          workflowsState.when(
            data: (workflows) {
              if (workflows.isEmpty) {
                return Text(l10n.studioViewsNoWorkflowsConfigured);
              }
              return ListView.builder(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                itemCount: workflows.length,
                itemBuilder: (context, index) {
                  try {
                    final workflow = workflows[index];

                    final String displayName =
                        (workflow.name.translations['fi']?.isNotEmpty ?? false)
                        ? workflow.name.translations['fi']!
                        : (workflow.name.translations['en'] ??
                              'Unnamed Workflow');

                    final steps = workflow.steps.length;
                    final status = workflow.status;

                    final slug = workflow.slug;
                    if (slug.isEmpty) {
                      throw AppException.validation(
                        'Workflow slug is missing.',
                      );
                    }

                    final workflowId = workflow.id;
                    if (workflowId.isEmpty) {
                      throw AppException.validation('Workflow ID is missing.');
                    }

                    return Card(
                      child: ListTile(
                        leading: Icon(
                          Icons.account_tree,
                          color: Theme.of(context).colorScheme.onSurfaceVariant,
                        ),
                        title: Text(
                          displayName,
                          style: const TextStyle(fontWeight: FontWeight.bold),
                        ),
                        subtitle: Text(
                          '$workflowId\n${l10n.studioViewsSlugSubtitle(slug)}\n${l10n.studioViewsWorkflowSubtitle('', steps, status)}',
                        ),
                        trailing: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            CloneEntityButton(
                              onClone: () async {
                                await ref
                                    .read(workflowsControllerProvider.notifier)
                                    .cloneWorkflow(workflowId);
                              },
                            ),
                            const Icon(Icons.settings_ethernet),
                          ],
                        ),
                        onTap: () {
                          WorkflowEditRoute(
                            id: workflowId,
                            slug: slug,
                          ).go(context);
                        },
                      ),
                    );
                  } catch (e, st) {
                    ref
                        .read(loggerServiceProvider)
                        .error(
                          'Studio',
                          'Error rendering workflow list item: $e',
                          e,
                          st,
                        );
                    return ErrorView(error: e, stackTrace: st, compact: true);
                  }
                },
              );
            },
            loading: () => const Center(child: CircularProgressIndicator()),
            error: (e, _) => ErrorView(
              error: e,
              compact: true,
              onRetry: () =>
                  ref.read(workflowsControllerProvider.notifier).refresh(),
            ),
          ),
        ],
      ),
    );
  }
}
