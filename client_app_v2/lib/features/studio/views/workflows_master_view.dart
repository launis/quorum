import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/studio/controllers/studio_controller.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/router/router.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/features/studio/views/components/clone_entity_button.dart';
import 'package:client_app/features/studio/views/widgets/studio_master_header.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/theme/app_spacing.dart';

/// Flat MVC List view for Workflows (DAG definitions).
/// Virtualized ListView.builder with prototypeItem and centered 1200px max-width containment.
class WorkflowsMasterView extends ConsumerStatefulWidget {
  const WorkflowsMasterView({super.key});

  @override
  ConsumerState<WorkflowsMasterView> createState() =>
      _WorkflowsMasterViewState();
}

class _WorkflowsMasterViewState extends ConsumerState<WorkflowsMasterView> {
  String? _bannerError;
  String _searchQuery = '';

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final workflowsState = ref.watch(workflowsControllerProvider);
    final currentLocale = Localizations.localeOf(context).languageCode;

    final workflows = switch (workflowsState) {
      AsyncData(:final value) => value,
      _ => null,
    };

    final filtered = workflows?.where((w) {
      if (_searchQuery.isEmpty) return true;
      final query = _searchQuery.toLowerCase();
      final name = w.name.get(currentLocale).toLowerCase();
      final slug = w.slug.toLowerCase();
      final id = w.id.toLowerCase();
      return name.contains(query) || slug.contains(query) || id.contains(query);
    }).toList();

    return Align(
      alignment: Alignment.topCenter,
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 1200),
        child: Padding(
          padding: AppSpacing.p16,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              if (_bannerError != null) ...[
                MaterialBanner(
                  content: Text(_bannerError!),
                  backgroundColor: Theme.of(context).colorScheme.errorContainer,
                  contentTextStyle: TextStyle(
                    color: Theme.of(context).colorScheme.onErrorContainer,
                  ),
                  actions: [
                    TextButton(
                      onPressed: () => setState(() => _bannerError = null),
                      child: Text(l10n.cancelButton),
                    ),
                  ],
                ),
                AppSpacing.h16,
              ],
              StudioMasterHeader(
                title: l10n.studioViewsWorkflowBuilderTitle,
                subtitle: l10n.studioViewsWorkflowBuilderDesc,
                searchQuery: _searchQuery,
                onSearchChanged: (query) =>
                    setState(() => _searchQuery = query),
                itemCount: filtered?.length ?? 0,
                totalCount: workflows?.length ?? 0,
                actionLabel: l10n.studioViewsNewWorkflowBtn,
                actionIcon: Icons.account_tree,
                onAction: () async {
                  try {
                    final draft = await ref
                        .read(workflowsControllerProvider.notifier)
                        .createWorkflowDraft();
                    if (context.mounted) {
                      WorkflowEditRoute(
                        id: draft.id,
                        slug: draft.slug,
                      ).go(context);
                    }
                  } catch (e, st) {
                    if (context.mounted) {
                      ref
                          .read(loggerServiceProvider)
                          .error(
                            'Studio',
                            'Failed to mint workflow draft: $e',
                            e,
                            st,
                          );
                      setState(() {
                        _bannerError = l10n.studioViewsFailedToCreate(
                          e.toString(),
                        );
                      });
                    }
                  }
                },
              ),
              AppSpacing.h16,
              Expanded(
                child: switch (workflowsState) {
                  AsyncData() =>
                    workflows!.isEmpty
                        ? Center(
                            child: Text(l10n.studioViewsNoWorkflowsConfigured),
                          )
                        : filtered!.isEmpty
                        ? Center(child: Text(l10n.studioMasterNoMatchingItems))
                        : ListView.builder(
                            itemCount: filtered.length,
                            prototypeItem: Card(
                              child: ListTile(
                                leading: Icon(
                                  Icons.account_tree,
                                  color: Theme.of(
                                    context,
                                  ).colorScheme.onSurfaceVariant,
                                ),
                                title: const Text(
                                  'Prototype Title',
                                  overflow: TextOverflow.ellipsis,
                                  style: TextStyle(fontWeight: FontWeight.bold),
                                ),
                                subtitle: const Padding(
                                  padding: EdgeInsets.only(top: 8.0),
                                  child: Text(
                                    'Prototype Subtitle Content',
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                ),
                                trailing: const Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    Icon(Icons.copy),
                                    Icon(Icons.settings_ethernet),
                                  ],
                                ),
                              ),
                            ),
                            itemBuilder: (context, index) {
                              try {
                                final workflow = filtered[index];
                                final String displayName = workflow.name.get(
                                  currentLocale,
                                );
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
                                  throw AppException.validation(
                                    'Workflow ID is missing.',
                                  );
                                }

                                return Card(
                                  child: ListTile(
                                    leading: Icon(
                                      Icons.account_tree,
                                      color: Theme.of(
                                        context,
                                      ).colorScheme.onSurfaceVariant,
                                    ),
                                    title: Text(
                                      displayName,
                                      overflow: TextOverflow.ellipsis,
                                      style: const TextStyle(
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                                    subtitle: Padding(
                                      padding: const EdgeInsets.only(top: 8.0),
                                      child: Wrap(
                                        spacing: 12.0,
                                        runSpacing: 4.0,
                                        children: [
                                          Text(
                                            workflowId,
                                            style: Theme.of(context)
                                                .textTheme
                                                .bodySmall
                                                ?.copyWith(
                                                  color: Theme.of(context)
                                                      .colorScheme
                                                      .onSurfaceVariant,
                                                  fontFamily: 'monospace',
                                                ),
                                          ),
                                          Text(
                                            l10n.studioViewsSlugSubtitle(slug),
                                            style: Theme.of(context)
                                                .textTheme
                                                .bodySmall
                                                ?.copyWith(
                                                  color: Theme.of(context)
                                                      .colorScheme
                                                      .onSurfaceVariant,
                                                ),
                                          ),
                                          Text(
                                            l10n.studioViewsWorkflowSubtitle(
                                              '',
                                              steps,
                                              status,
                                            ),
                                            style: Theme.of(context)
                                                .textTheme
                                                .bodySmall
                                                ?.copyWith(
                                                  color: Theme.of(context)
                                                      .colorScheme
                                                      .onSurfaceVariant,
                                                ),
                                          ),
                                        ],
                                      ),
                                    ),
                                    trailing: Row(
                                      mainAxisSize: MainAxisSize.min,
                                      children: [
                                        CloneEntityButton(
                                          onClone: () async {
                                            await ref
                                                .read(
                                                  workflowsControllerProvider
                                                      .notifier,
                                                )
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
                                return ErrorView(
                                  error: e,
                                  stackTrace: st,
                                  compact: true,
                                );
                              }
                            },
                          ),
                  AsyncLoading() => const Center(
                    child: CircularProgressIndicator(),
                  ),
                  AsyncError(:final error, :final stackTrace) => ErrorView(
                    error: error,
                    stackTrace: stackTrace,
                    compact: true,
                    onRetry: () => ref
                        .read(workflowsControllerProvider.notifier)
                        .refresh(),
                  ),
                },
              ),
            ],
          ),
        ),
      ),
    );
  }
}
