import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/studio/controllers/prompt_blocks_controller.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/router/router.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

/// Flat MVC List view for BARS Matrices.
/// Adheres strictly to De-Generator constraints using List<Map<String, dynamic>>.
class MatricesMasterView extends ConsumerWidget {
  const MatricesMasterView({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
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
                l10n.studioDashboardMatricesTitle,
                style: Theme.of(context).textTheme.titleLarge,
              ),
              FilledButton.icon(
                onPressed: () async {
                  try {
                    final draft = await ref
                        .read(promptBlocksControllerProvider.notifier)
                        .createPromptBlockDraft();
                    if (context.mounted) {
                      PromptBlockEditRoute(id: draft.id, slug: draft.slug)
                          .go(context);
                    }
                  } catch (e) {
                    if (context.mounted) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(content: Text('Failed to mint: $e')),
                      );
                    }
                  }
                },
                icon: const Icon(Icons.grid_on),
                label: Text(l10n.studioViewsNewMatrix),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            l10n.studioViewsMatricesDescription,
            style: Theme.of(context).textTheme.bodyMedium,
          ),
          const SizedBox(height: 16),
          blocksState.when(
            data: (blocks) {
              // The BARS matrices are a subtype of Prompt Blocks
              final matrices = blocks
                  .where((b) => b.categoryId == 'matrix')
                  .toList();

              if (matrices.isEmpty) {
                return Text(l10n.studioViewsNoMatricesAvailable);
              }

              return ListView.builder(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                itemCount: matrices.length,
                itemBuilder: (context, index) {
                  final matrix = matrices[index];
                  final displayName = matrix.label.get(
                    matrix.label.defaultLocale,
                  );
                  if (displayName.isEmpty == true && matrix.id.isNotEmpty) {
                    // Fallback
                  }

                  final scalesCount = matrix.scales?.length ?? 0;

                  return Card(
                    child: ListTile(
                      leading: Icon(
                        Icons.table_chart,
                        color: Theme.of(context).colorScheme.onSurfaceVariant,
                      ),
                      title: Text(
                        displayName.isNotEmpty ? displayName : matrix.id,
                        style: const TextStyle(fontWeight: FontWeight.bold),
                      ),
                      subtitle: Text(
                        'ID: ${matrix.id} | Scales (Grades): $scalesCount',
                      ),
                      trailing: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          IconButton(
                            icon: const Icon(Icons.copy),
                            tooltip: 'Duplicate (Deep Copy)',
                            onPressed: () async {
                              final id = matrix.id;
                              if (id.isEmpty) return;

                              try {
                                await ref
                                    .read(
                                      promptBlocksControllerProvider.notifier,
                                    )
                                    .clonePromptBlock(id);
                                if (!context.mounted) return;
                                ScaffoldMessenger.of(context).showSnackBar(
                                  SnackBar(
                                    content: Text(l10n.studioViewsMatrixCloned),
                                  ),
                                );
                              } catch (e) {
                                if (!context.mounted) return;
                                ref
                                    .read(loggerServiceProvider)
                                    .error(
                                      'Studio',
                                      'Failed to clone matrix: $e',
                                      e,
                                    );
                                ScaffoldMessenger.of(context).showSnackBar(
                                  SnackBar(
                                    content: Text(
                                      l10n.studioViewsFailedToClone(
                                        e.toString(),
                                      ),
                                    ),
                                    backgroundColor: Theme.of(
                                      context,
                                    ).colorScheme.error,
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
                          id: matrix.id,
                          $extra: matrix.toJson(),
                        ).go(context);
                      },
                    ),
                  );
                },
              );
            },
            loading: () => const Center(child: CircularProgressIndicator()),
            error: (e, _) => ErrorView(
              error: e,
              compact: true,
              onRetry: () =>
                  ref.read(promptBlocksControllerProvider.notifier).refresh(),
            ),
          ),
        ],
      ),
    );
  }
}
