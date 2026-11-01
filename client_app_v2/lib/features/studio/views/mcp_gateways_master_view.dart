import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/core/error/app_error_boundary.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/features/studio/controllers/mcp_gateways_controller.dart';
import 'package:client_app/features/studio/views/widgets/studio_master_header.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/router/router.dart';
import 'package:client_app/features/studio/views/components/clone_entity_button.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/core/logging/logger_service.dart';

/// Flat MVC List view for MCP Gateways.
/// Virtualized ListView.builder with prototypeItem and centered 1200px max-width containment.
class McpGatewaysMasterView extends ConsumerStatefulWidget {
  const McpGatewaysMasterView({super.key});

  @override
  ConsumerState<McpGatewaysMasterView> createState() =>
      _McpGatewaysMasterViewState();
}

class _McpGatewaysMasterViewState extends ConsumerState<McpGatewaysMasterView> {
  String? _bannerError;
  String _searchQuery = '';

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final gatewaysState = ref.watch(mcpGatewaysControllerProvider);

    final gateways = switch (gatewaysState) {
      AsyncData(:final value) => value,
      _ => null,
    };

    final filtered = gateways?.where((g) {
      if (_searchQuery.isEmpty) return true;
      final query = _searchQuery.toLowerCase();
      final id = g.id.toLowerCase();
      final slug = g.slug.toLowerCase();
      return id.contains(query) || slug.contains(query);
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
                  title: l10n.studioDashboardGatewaysTitle,
                  subtitle: l10n.studioDashboardGatewaysDesc,
                  searchQuery: _searchQuery,
                  onSearchChanged: (query) =>
                      setState(() => _searchQuery = query),
                  itemCount: filtered?.length ?? 0,
                  totalCount: gateways?.length ?? 0,
                  actionLabel: l10n.studioViewsNewBtn,
                  actionIcon: Icons.add,
                  onAction: () async {
                    try {
                      final draft = await ref
                          .read(mcpGatewaysControllerProvider.notifier)
                          .createMcpGatewayDraft();
                      if (!context.mounted) return;
                      McpGatewayEditRoute(id: draft.id).go(context);
                    } catch (e, st) {
                      ref
                          .read(loggerServiceProvider)
                          .error(
                            'McpGatewaysMasterView',
                            'Failed to mint',
                            e,
                            st,
                          );
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
                  child: switch (gatewaysState) {
                    AsyncData() =>
                      gateways!.isEmpty
                          ? Center(child: Text(l10n.noMcpGatewaysDefined))
                          : filtered!.isEmpty
                          ? Center(
                              child: Text(l10n.studioMasterNoMatchingItems),
                            )
                          : ListView.builder(
                              itemCount: filtered.length,
                              prototypeItem: Card(
                                child: ListTile(
                                  leading: Icon(
                                    Icons.hub,
                                    color: Theme.of(
                                      context,
                                    ).colorScheme.onSurfaceVariant,
                                  ),
                                  title: Text(
                                    l10n.studioDashboardGatewaysTitle,
                                    overflow: TextOverflow.ellipsis,
                                    style: Theme.of(context).textTheme.bodyLarge
                                        ?.copyWith(fontWeight: FontWeight.bold),
                                  ),
                                  subtitle: Text(
                                    l10n.studioDashboardGatewaysDesc,
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
                                final gateway = filtered[index];
                                if (gateway.id.isEmpty) {
                                  throw AppException.validation(
                                    'Fail-Fast: MCP Gateway ID is missing.',
                                  );
                                }
                                final tools = gateway.tools.length;

                                return Card(
                                  child: ListTile(
                                    leading: Icon(
                                      Icons.hub,
                                      color: Theme.of(
                                        context,
                                      ).colorScheme.onSurfaceVariant,
                                    ),
                                    title: Text(
                                      gateway.id,
                                      overflow: TextOverflow.ellipsis,
                                      style: Theme.of(context)
                                          .textTheme
                                          .bodyLarge
                                          ?.copyWith(
                                            fontWeight: FontWeight.bold,
                                          ),
                                    ),
                                    subtitle: Text(
                                      l10n.gatewaySubtitle(
                                        tools,
                                        l10n.activeStatus,
                                      ),
                                      overflow: TextOverflow.ellipsis,
                                    ),
                                    trailing: Row(
                                      mainAxisSize: MainAxisSize.min,
                                      children: [
                                        CloneEntityButton(
                                          onClone: () => ref
                                              .read(
                                                mcpGatewaysControllerProvider
                                                    .notifier,
                                              )
                                              .cloneGateway(gateway.id),
                                        ),
                                        const Icon(Icons.settings_ethernet),
                                      ],
                                    ),
                                    onTap: () {
                                      McpGatewayEditRoute(
                                        id: gateway.id,
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
                          .read(mcpGatewaysControllerProvider.notifier)
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
