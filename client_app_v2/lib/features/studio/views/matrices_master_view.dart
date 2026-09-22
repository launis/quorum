import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/studio/controllers/prompt_blocks_controller.dart';
import 'package:client_app/features/studio/views/widgets/studio_master_header.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/router/router.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/theme/app_spacing.dart';

/// Flat MVC List view for BARS Matrices.
/// Virtualized ListView.builder with prototypeItem and centered 1200px max-width containment.
class MatricesMasterView extends ConsumerStatefulWidget {
  const MatricesMasterView({super.key});

  @override
  ConsumerState<MatricesMasterView> createState() => _MatricesMasterViewState();
}

class _MatricesMasterViewState extends ConsumerState<MatricesMasterView> {
  String? _bannerError;
  String _searchQuery = '';

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final blocksState = ref.watch(promptBlocksControllerProvider);
    final currentLocale = Localizations.localeOf(context).languageCode;

    final matrices = switch (blocksState) {
      AsyncData(:final value) =>
        value
            .where(
              (b) => PromptBlockCategoryGroups.matrixCategories.contains(
                b.categoryId,
              ),
            )
            .toList(),
      _ => null,
    };

    final filtered = matrices?.where((m) {
      if (_searchQuery.isEmpty) return true;
      final query = _searchQuery.toLowerCase();
      final displayName = m.label.get(currentLocale).toLowerCase();
      final id = m.id.toLowerCase();
      final slug = m.slug.toLowerCase();
      return displayName.contains(query) ||
          id.contains(query) ||
          slug.contains(query);
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
                title: l10n.studioDashboardMatricesTitle,
                subtitle: l10n.studioViewsMatricesDescription,
                searchQuery: _searchQuery,
                onSearchChanged: (query) =>
                    setState(() => _searchQuery = query),
                itemCount: filtered?.length ?? 0,
                totalCount: matrices?.length ?? 0,
                actionLabel: l10n.studioViewsNewMatrix,
                actionIcon: Icons.grid_on,
                onAction: () async {
                  try {
                    final draft = await ref
                        .read(promptBlocksControllerProvider.notifier)
                        .createPromptBlockDraft();
                    if (context.mounted) {
                      PromptBlockEditRoute(
                        id: draft.id,
                        slug: draft.slug,
                      ).go(context);
                    }
                  } catch (e, st) {
                    if (context.mounted) {
                      ref
                          .read(loggerServiceProvider)
                          .error('MatricesMasterView', 'Failed to mint', e, st);
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
                child: switch (blocksState) {
                  AsyncData() =>
                    matrices!.isEmpty
                        ? Center(
                            child: Text(l10n.studioViewsNoMatricesAvailable),
                          )
                        : filtered!.isEmpty
                        ? Center(child: Text(l10n.studioMasterNoMatchingItems))
                        : ListView.builder(
                            itemCount: filtered.length,
                            prototypeItem: Card(
                              child: ListTile(
                                leading: Icon(
                                  Icons.table_chart,
                                  color: Theme.of(
                                    context,
                                  ).colorScheme.onSurfaceVariant,
                                ),
                                title: const Text(
                                  'Prototype Matrix Title',
                                  overflow: TextOverflow.ellipsis,
                                  style: TextStyle(fontWeight: FontWeight.bold),
                                ),
                                subtitle: const Text(
                                  'Prototype Subtitle',
                                  overflow: TextOverflow.ellipsis,
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
                              final matrix = filtered[index];
                              final displayName = matrix.label.get(
                                currentLocale,
                              );
                              final scalesCount = matrix.scales?.length ?? 0;

                              return Card(
                                child: ListTile(
                                  leading: Icon(
                                    Icons.table_chart,
                                    color: Theme.of(
                                      context,
                                    ).colorScheme.onSurfaceVariant,
                                  ),
                                  title: Text(
                                    displayName.isNotEmpty
                                        ? displayName
                                        : matrix.id,
                                    overflow: TextOverflow.ellipsis,
                                    style: const TextStyle(
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                  subtitle: Text(
                                    l10n.studioViewsMatrixSubtitle(
                                      matrix.id,
                                      scalesCount,
                                    ),
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                  trailing: Row(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      IconButton(
                                        icon: const Icon(Icons.copy),
                                        tooltip:
                                            l10n.studioMasterDuplicateTooltip,
                                        onPressed: () async {
                                          final id = matrix.id;
                                          if (id.isEmpty) return;

                                          try {
                                            await ref
                                                .read(
                                                  promptBlocksControllerProvider
                                                      .notifier,
                                                )
                                                .clonePromptBlock(id);
                                          } catch (e, st) {
                                            if (!context.mounted) return;
                                            ref
                                                .read(loggerServiceProvider)
                                                .error(
                                                  'Studio',
                                                  'Failed to clone matrix: $e',
                                                  e,
                                                  st,
                                                );
                                          }
                                        },
                                      ),
                                      const Icon(Icons.settings_ethernet),
                                    ],
                                  ),
                                  onTap: () {
                                    MatrixEditRoute(id: matrix.id).go(context);
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
                        .read(promptBlocksControllerProvider.notifier)
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
