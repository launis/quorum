import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/studio/controllers/output_profile_controller.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/router/router.dart';
import 'package:client_app/features/studio/views/components/clone_entity_button.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/core/logging/logger_service.dart';

class OutputProfileListView extends ConsumerWidget {
  const OutputProfileListView({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final profilesState = ref.watch(outputProfilesControllerProvider);

    return SingleChildScrollView(
      padding: AppSpacing.p16,
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
                onPressed: () async {
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
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          content: Text(
                            l10n.studioViewsFailedToCreate(e.toString()),
                          ),
                        ),
                      );
                    }
                  }
                },
                icon: const Icon(Icons.add),
                label: Text(l10n.studioViewsNewProfileBtn),
              ),
            ],
          ),
          AppSpacing.h16,
          switch (profilesState) {
            AsyncData(value: final profiles) => Builder(
              builder: (context) {
                if (profiles.isEmpty)
                  return Text(l10n.studioViewsNoOutputProfiles);
                return ListView.builder(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  itemCount: profiles.length,
                  itemBuilder: (context, index) {
                    final profile = profiles[index];
                    final layouts = profile.layouts;

                    final currentLocale = Localizations.localeOf(
                      context,
                    ).languageCode;
                    final title =
                        profile.name.translations[currentLocale] ??
                        profile.name.translations['en'] ??
                        profile.name.translations['fi'] ??
                        (profile.id.isNotEmpty
                            ? profile.id
                            : l10n.studioViewsUnnamedProfile);

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
                          '${l10n.studioViewsSlugSubtitle(profile.slug)}\n${l10n.studioViewsProfileListSubtitle(profile.id, profile.workflowId.isEmpty ? l10n.studioViewsNone : profile.workflowId, layouts.length)}',
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
                                      outputProfilesControllerProvider.notifier,
                                    )
                                    .cloneProfile(id);
                              },
                            ),
                            const Icon(Icons.edit_document),
                          ],
                        ),
                        onTap: () {
                          OutputProfileEditRoute(id: profile.id).go(context);
                        },
                      ),
                    );
                  },
                );
              },
            ),
            AsyncLoading() => const Center(child: CircularProgressIndicator()),
            AsyncError(:final error) => ErrorView(
              error: error,
              compact: true,
              onRetry: () =>
                  ref.read(outputProfilesControllerProvider.notifier).refresh(),
            ),
          },
        ],
      ),
    );
  }
}
