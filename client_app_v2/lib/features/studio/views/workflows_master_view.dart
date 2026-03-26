import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/studio/controllers/studio_controller.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/router/router.dart';
import 'package:client_app/utils/safe_cast.dart';
import 'package:client_app/core/error/app_exception.dart';

/// Flat MVC List view for Workflows (DAG definitions).
/// Adheres strictly to De-Generator constraints using List<Map<String, dynamic>>.
class WorkflowsMasterView extends ConsumerWidget {
  const WorkflowsMasterView({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
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
                'Workflow Builder',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              FilledButton.icon(
                onPressed: () {
                  const WorkflowNewRoute().go(context);
                },
                icon: const Icon(Icons.account_tree),
                label: const Text('New Workflow'),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            'Manage master execution blueprints (DAGs) defining agentic workflows, inputs, and strategies.',
            style: Theme.of(context).textTheme.bodyMedium,
          ),
          const SizedBox(height: 16),
          workflowsState.when(
            data: (workflows) {
              if (workflows.isEmpty) {
                return const Text('No workflows configured.');
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
                    final defaultLocale = labelMap['default_locale']?.toString();
                    if (defaultLocale == null) {
                      throw AppException.validation('Workflow configuration corrupted: missing default_locale.');
                    }

                    // Support legacy direct strings or V2 I18n block
                    final nameVal = workflow['name'];
                    final String displayName;
                    
                    if (nameVal is String) {
                      displayName = nameVal;
                    } else {
                      final localizedName = translations[defaultLocale]?.toString();
                      if (localizedName == null) {
                        throw AppException.validation('Workflow name missing for locale: $defaultLocale.');
                      }
                      displayName = localizedName;
                    }

                    final stepsList = SafeCast.safeList(workflow['steps']);
                    final steps = stepsList.length;
                    final status = SafeCast.safeString(workflow['status']);
                    
                    final slugStr = SafeCast.safeString(workflow['slug']);
                    final slug = slugStr.isNotEmpty ? slugStr : (throw AppException.validation('Workflow slug is missing.'));
                    
                    final workflowId = workflow['id']?.toString();
                    if (workflowId == null || workflowId.isEmpty) {
                      throw AppException.validation('Workflow ID is missing.');
                    }

                    return Card(
                      child: ListTile(
                        leading: const Icon(
                          Icons.account_tree,
                          color: Colors.blueGrey,
                        ),
                        title: Text(
                          displayName,
                          style: const TextStyle(fontWeight: FontWeight.bold),
                        ),
                        subtitle: Text(
                          'ID: ${workflow['id']} | Nodes: $steps | Status: $status',
                        ),
                        trailing: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            IconButton(
                              icon: const Icon(Icons.copy),
                              tooltip: 'Duplicate (Shallow-Deep Copy)',
                              onPressed: () async {
                                final id = workflow['id']?.toString();
                                if (id == null) return;

                                try {
                                  await ref
                                      .read(workflowsControllerProvider.notifier)
                                      .cloneWorkflow(id);
                                  if (!context.mounted) return;
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    const SnackBar(
                                      content: Text('Workflow cloned securely.'),
                                    ),
                                  );
                                } catch (e) {
                                  if (!context.mounted) return;
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    SnackBar(
                                      content: Text('Failed to clone: $e'),
                                      backgroundColor: Colors.red,
                                    ),
                                  );
                                }
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
