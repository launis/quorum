import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/studio/controllers/output_profile_controller.dart';
import 'package:client_app/utils/safe_cast.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/router/router.dart';

class OutputProfileListView extends ConsumerWidget {
  const OutputProfileListView({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
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
                'Tulostusprofiilit (Output Profiles)',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              FilledButton.icon(
                onPressed: () {
                  const OutputProfileNewRoute().go(context);
                },
                icon: const Icon(Icons.add),
                label: const Text('New Profile'),
              ),
            ],
          ),
          const SizedBox(height: 16),
          profilesState.when(
            data: (profiles) {
              if (profiles.isEmpty)
                return const Text('No Output Profiles defined.');
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
                      'Unnamed Profile';

                  return Card(
                    child: ListTile(
                      leading: const Icon(Icons.print, color: Colors.blueGrey),
                      title: Text(
                        title,
                        style: const TextStyle(fontWeight: FontWeight.bold),
                      ),
                      subtitle: Text(
                        'ID: ${profile['id']} | Workflow: ${profile['workflow_id'] ?? 'None'} | ${layouts.length} Layout Blocks',
                      ),
                      trailing: const Icon(Icons.edit_document),
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
