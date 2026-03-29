import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/studio/controllers/output_profile_controller.dart';
import 'package:client_app/utils/safe_cast.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/router/router.dart';
import 'package:client_app/features/studio/views/components/clone_entity_button.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

class OutputProfileListView extends ConsumerWidget {
  const OutputProfileListView({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final profilesState = ref.watch(outputProfilesControllerProvider);

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                l10n.studioViewsOutputProfilesMasterTitle,
                style: Theme.of(context).textTheme.titleLarge,
              ),
              FilledButton.icon(
                onPressed: () {
                  const OutputProfileNewRoute().go(context);
                },
                icon: const Icon(Icons.add),
                label: Text(l10n.studioViewsNewProfileBtn),
              ),
            ],
          ),
          const SizedBox(height: 16),
          profilesState.when(
            data: (profiles) {
              if (profiles.isEmpty)
                return Text(l10n.studioViewsNoOutputProfiles);
              return ListView.builder(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                itemCount: profiles.length,
                itemBuilder: (context, index) {
                  final profile = profiles[index];
                  final layouts = SafeCast.safeList(profile['layouts']);

                  final nameObj = SafeCast.safeMap(profile['name']);
                  final title =
                      (nameObj['translations'] as Map?)?['fi'] ??
                      nameObj['fi'] ??
                      profile['id']?.toString() ??
                      l10n.studioViewsUnnamedProfile;

                  return Card(
                    child: ListTile(
                      leading: Icon(
                        Icons.print,
                        color: Theme.of(context).colorScheme.onSurfaceVariant,
                      ),
                      title: Text(
                        title,
                        style: const TextStyle(fontWeight: FontWeight.bold),
                      ),
                      subtitle: Text(
                        '${l10n.studioViewsSlugSubtitle(profile['slug']?.toString() ?? '')}\n${l10n.studioViewsProfileListSubtitle(
                          profile['id']?.toString() ?? '',
                          profile['workflow_id']?.toString() ??
                              l10n.studioViewsNone,
                          layouts.length,
                        )}',
                      ),
                      trailing: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          CloneEntityButton(
                            onClone: () async {
                              final id = profile['id']?.toString();
                              if (id == null) return;
                              await ref
                                  .read(
                                    outputProfilesControllerProvider.notifier,
                                  )
                                  .cloneProfile(id);
                            },
                          ),
                          const Icon(Icons.edit_document),
                        ],
                      ),
                      onTap: () {
                        OutputProfileEditRoute(
                          id: profile['id'] ?? '',
                          $extra: profile,
                        ).go(context);
                      },
                    ),
                  );
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
                              .read(outputProfilesControllerProvider.notifier)
                              .refresh(),
                ),
          ),
        ],
      ),
    );
  }
}
