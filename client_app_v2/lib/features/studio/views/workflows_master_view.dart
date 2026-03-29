import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/studio/controllers/studio_controller.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/router/router.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/features/studio/views/components/clone_entity_button.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/utils/safe_cast.dart';

/// Flat MVC List view for Workflows (DAG definitions).
/// Adheres strictly to De-Generator constraints using List<Map<String, dynamic>>.
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
                    final labelMap = SafeCast.safeMap(workflow['name']);
                    final translations = SafeCast.safeMap(
                      labelMap['translations'],
                    );
                    final defaultLocale =
                        labelMap['default_locale']?.toString();
                    if (defaultLocale == null) {
                      throw AppException.validation(
                        'Workflow configuration corrupted: missing default_locale.',
                      );
                    }

                    // Support legacy direct strings or V2 I18n block
                    final nameVal = workflow['name'];
                    final String displayName;

                    if (nameVal is String) {
                      displayName = nameVal;
                    } else {
                      final localizedName =
                          translations[defaultLocale]?.toString();
                      if (localizedName == null) {
                        throw AppException.validation(
                          'Workflow name missing for locale: $defaultLocale.',
                        );
                      }
                      displayName = localizedName;
                    }

                    final stepsList = SafeCast.safeList(workflow['steps']);
                    final steps = stepsList.length;
                    final status = SafeCast.safeString(workflow['status']);

                    final slugStr = SafeCast.safeString(workflow['slug']);
                    final slug =
                        slugStr.isNotEmpty
                            ? slugStr
                            : (throw AppException.validation(
                              'Workflow slug is missing.',
                            ));

                    final workflowId = workflow['id']?.toString();
                    if (workflowId == null || workflowId.isEmpty) {
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
                          l10n.studioViewsWorkflowSubtitle(
                            workflow['id']?.toString() ?? '',
                            steps,
                            status,
                          ),
                        ),
                        trailing: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            CloneEntityButton(
                              onClone: () async {
                                final id = workflow['id']?.toString();
                                if (id == null) return;
                                await ref
                                    .read(workflowsControllerProvider.notifier)
                                    .cloneWorkflow(id);
                              },
                            ),
                            const Icon(Icons.settings_ethernet),
                          ],
                        ),
                        onTap: () {
                          WorkflowEditRoute(
                            id: workflowId,
                            slug: slug,
                            $extra: workflow,
                          ).go(context);
                        },
                      ),
                    );
                  } catch (e) {
                    return ErrorView(error: e, compact: true);
                  }
                },
              );
            },
            loading: () => const Center(child: CircularProgressIndicator()),
            error:
                (e, _) => ErrorView(
                  error: e,
                  compact: true,
                  onRetry:
                      () =>
                          ref
                              .read(workflowsControllerProvider.notifier)
                              .refresh(),
                ),
          ),
        ],
      ),
    );
  }
}
