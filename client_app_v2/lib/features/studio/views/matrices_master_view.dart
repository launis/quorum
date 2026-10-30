import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/core/error/app_error_boundary.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/features/studio/controllers/prompt_blocks_controller.dart';
import 'package:client_app/features/studio/views/components/clone_entity_button.dart';
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

    return AppErrorBoundary(
      child: Align(
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
                    backgroundColor: Theme.of(
                      context,
                    ).colorScheme.errorContainer,
                    contentTextStyle: Theme.of(context).textTheme.bodyMedium
                        ?.copyWith(
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
                          .createPromptBlockDraft(categoryId: 'matrix');
                      if (!context.mounted) return;
                      PromptBlockEditRoute(
                        id: draft.id,
                        slug: draft.slug,
                      ).go(context);
                    } catch (e, st) {
                      ref
                          .read(loggerServiceProvider)
                          .error('MatricesMasterView', 'Failed to mint', e, st);
                      if (!context.mounted) return;
                      setState(() {
                        _bannerError = l10n.studioViewsFailedToCreate(
                          e.toString(),
                        );
                      });
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
                          ? Center(
                              child: Text(l10n.studioMasterNoMatchingItems),
                            )
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
                                  title: Text(
                                    l10n.studioDashboardMatricesTitle,
                                    overflow: TextOverflow.ellipsis,
                                    style: Theme.of(context).textTheme.bodyLarge
                                        ?.copyWith(fontWeight: FontWeight.bold),
                                  ),
                                  subtitle: Text(
                                    l10n.studioViewsMatricesDescription,
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
                                if (matrix.id.isEmpty) {
                                  throw AppException.validation(
                                    'Fail-Fast: Matrix ID is missing.',
                                  );
                                }
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
                                      displayName,
                                      overflow: TextOverflow.ellipsis,
                                      style: Theme.of(context)
                                          .textTheme
                                          .bodyLarge
                                          ?.copyWith(
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
                                        CloneEntityButton(
                                          onClone: () async {
                                            await ref
                                                .read(
                                                  promptBlocksControllerProvider
                                                      .notifier,
                                                )
                                                .clonePromptBlock(matrix.id);
                                          },
                                        ),
                                        const Icon(Icons.settings_ethernet),
                                      ],
                                    ),
                                    onTap: () {
                                      MatrixEditRoute(
                                        id: matrix.id,
                                      ).go(context);
                                    },
                                  ),
                                );
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
                          .read(promptBlocksControllerProvider.notifier)
                          .refresh(),
                    ),
                  },
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
