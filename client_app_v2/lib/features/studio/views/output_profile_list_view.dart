import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/studio/controllers/output_profile_controller.dart';
import 'package:client_app/features/studio/views/widgets/studio_master_header.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/router/router.dart';
import 'package:client_app/features/studio/views/components/clone_entity_button.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/core/logging/logger_service.dart';

/// Flat MVC List view for Output Profiles.
/// Virtualized ListView.builder with prototypeItem and centered 1200px max-width containment.
class OutputProfileListView extends ConsumerStatefulWidget {
  const OutputProfileListView({super.key});

  @override
  ConsumerState<OutputProfileListView> createState() =>
      _OutputProfileListViewState();
}

class _OutputProfileListViewState extends ConsumerState<OutputProfileListView> {
  String? _bannerError;
  String _searchQuery = '';

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final profilesState = ref.watch(outputProfilesControllerProvider);
    final currentLocale = Localizations.localeOf(context).languageCode;

    final profiles = switch (profilesState) {
      AsyncData(:final value) => value,
      _ => null,
    };

    final filtered = profiles?.where((p) {
      if (_searchQuery.isEmpty) return true;
      final query = _searchQuery.toLowerCase();
      final name = p.name.get(currentLocale).toLowerCase();
      final slug = p.slug.toLowerCase();
      final id = p.id.toLowerCase();
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
                title: l10n.studioViewsOutputProfilesMasterTitle,
                subtitle: l10n.outputProfilesDictionary,
                searchQuery: _searchQuery,
                onSearchChanged: (query) =>
                    setState(() => _searchQuery = query),
                itemCount: filtered?.length ?? 0,
                totalCount: profiles?.length ?? 0,
                actionLabel: l10n.studioViewsNewProfileBtn,
                actionIcon: Icons.add,
                onAction: () async {
                  try {
                    final draft = await ref
                        .read(outputProfilesControllerProvider.notifier)
                        .createOutputProfileDraft();
                    if (context.mounted) {
                      OutputProfileEditRoute(id: draft.id).go(context);
                    }
                  } catch (e, st) {
                    if (context.mounted) {
                      ref
                          .read(loggerServiceProvider)
                          .error(
                            'OutputProfileListView',
                            'Failed to mint',
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
                child: switch (profilesState) {
                  AsyncData() =>
                    profiles!.isEmpty
                        ? Center(child: Text(l10n.studioViewsNoOutputProfiles))
                        : filtered!.isEmpty
                        ? Center(child: Text(l10n.studioMasterNoMatchingItems))
                        : ListView.builder(
                            itemCount: filtered.length,
                            prototypeItem: Card(
                              child: ListTile(
                                leading: Icon(
                                  Icons.print,
                                  color: Theme.of(
                                    context,
                                  ).colorScheme.onSurfaceVariant,
                                ),
                                title: const Text(
                                  'Prototype Output Profile Title',
                                  overflow: TextOverflow.ellipsis,
                                  style: TextStyle(fontWeight: FontWeight.bold),
                                ),
                                subtitle: const Text(
                                  'Prototype Subtitle\nSecondary Info',
                                  overflow: TextOverflow.ellipsis,
                                ),
                                trailing: const Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    Icon(Icons.copy),
                                    Icon(Icons.edit_document),
                                  ],
                                ),
                              ),
                            ),
                            itemBuilder: (context, index) {
                              final profile = filtered[index];
                              final groups = profile.matrixSynthesisGroups;
                              final title = profile.name.get(currentLocale);

                              return Card(
                                child: ListTile(
                                  leading: Icon(
                                    Icons.print,
                                    color: Theme.of(
                                      context,
                                    ).colorScheme.onSurfaceVariant,
                                  ),
                                  title: Text(
                                    title,
                                    overflow: TextOverflow.ellipsis,
                                    style: const TextStyle(
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                  subtitle: Text(
                                    '${l10n.studioViewsSlugSubtitle(profile.slug)}\n${l10n.studioViewsProfileListSubtitle(profile.id, profile.workflowId.isEmpty ? l10n.studioViewsNone : profile.workflowId, groups.length)}',
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                  trailing: Row(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      CloneEntityButton(
                                        onClone: () async {
                                          final id = profile.id;
                                          if (id.isEmpty) return;
                                          await ref
                                              .read(
                                                outputProfilesControllerProvider
                                                    .notifier,
                                              )
                                              .cloneProfile(id);
                                        },
                                      ),
                                      const Icon(Icons.edit_document),
                                    ],
                                  ),
                                  onTap: () {
                                    OutputProfileEditRoute(
                                      id: profile.id,
                                    ).go(context);
                                  },
                                ),
                              );
                            },
                          ),
                  AsyncLoading() => const Center(
                    child: CircularProgressIndicator(),
                  ),
                  AsyncError(:final error) => ErrorView(
                    error: error,
                    compact: true,
                    onRetry: () => ref
                        .read(outputProfilesControllerProvider.notifier)
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
