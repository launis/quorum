import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/studio/controllers/prompt_blocks_controller.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/router/router.dart';
import 'package:client_app/utils/safe_cast.dart';

/// Flat MVC List view for BARS Matrices.
/// Adheres strictly to De-Generator constraints using List<Map<String, dynamic>>.
class MatricesMasterView extends ConsumerWidget {
  const MatricesMasterView({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final blocksState = ref.watch(promptBlocksControllerProvider);

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Assessment Matrices',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              FilledButton.icon(
                onPressed: () {
                  const MatrixNewRoute().go(context);
                },
                icon: const Icon(Icons.add),
                label: const Text('New Matrix'),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            'Manage Behavioral Anchored Rating Scales (BARS) and standardized evaluation matrices.',
            style: Theme.of(context).textTheme.bodyMedium,
          ),
          const SizedBox(height: 16),
          blocksState.when(
            data: (blocks) {
              // The BARS matrices are a subtype of Prompt Blocks
              final matrices =
                  blocks.where((b) => b['category_id'] == 'matrix').toList();

              if (matrices.isEmpty) {
                return const Text('No assessment matrices globally available.');
              }

              return ListView.builder(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                itemCount: matrices.length,
                itemBuilder: (context, index) {
                  final matrix = matrices[index];
                  final labelMap = SafeCast.safeMap(matrix['label']);
                  final translations = SafeCast.safeMap(
                    labelMap['translations'],
                  );
                  final defaultLocale =
                      labelMap['default_locale']?.toString() ?? 'en';

                  final displayName =
                      translations[defaultLocale]?.toString() ??
                      matrix['id']?.toString() ??
                      'Unnamed Matrix';

                  final scales = SafeCast.safeList(matrix['scales']).length;

                  return Card(
                    child: ListTile(
                      leading: const Icon(
                        Icons.table_chart,
                        color: Colors.blueGrey,
                      ),
                      title: Text(
                        displayName,
                        style: const TextStyle(fontWeight: FontWeight.bold),
                      ),
                      subtitle: Text(
                        'ID: ${matrix['id']} | Scales (Grades): $scales',
                      ),
                      trailing: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          IconButton(
                            icon: const Icon(Icons.copy),
                            tooltip: 'Duplicate (Deep Copy)',
                            onPressed: () async {
                              final id = matrix['id']?.toString();
                              if (id == null) return;

                              try {
                                await ref
                                    .read(
                                      promptBlocksControllerProvider.notifier,
                                    )
                                    .clonePromptBlock(id);
                                if (!context.mounted) return;
                                ScaffoldMessenger.of(context).showSnackBar(
                                  const SnackBar(
                                    content: Text('Matrix cloned securely.'),
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
                        MatrixEditRoute(
                          id: matrix['id']?.toString() ?? '',
                          $extra: matrix,
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
                              .read(promptBlocksControllerProvider.notifier)
                              .refresh(),
                ),
          ),
        ],
      ),
    );
  }
}
