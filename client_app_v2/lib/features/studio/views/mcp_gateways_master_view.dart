import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
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
      return id.contains(query);
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
                    if (context.mounted) {
                      McpGatewayEditRoute(id: draft.id).go(context);
                    }
                  } catch (e, st) {
                    if (context.mounted) {
                      ref
                          .read(loggerServiceProvider)
                          .error(
                            'McpGatewaysMasterView',
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
                child: switch (gatewaysState) {
                  AsyncData() =>
                    gateways!.isEmpty
                        ? Center(child: Text(l10n.noMcpGatewaysDefined))
                        : filtered!.isEmpty
                        ? Center(child: Text(l10n.studioMasterNoMatchingItems))
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
                                title: const Text(
                                  'Prototype Gateway ID',
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
                              final gateway = filtered[index];
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
                                    gateway.id.isNotEmpty
                                        ? gateway.id
                                        : l10n.unnamedGateway,
                                    overflow: TextOverflow.ellipsis,
                                    style: const TextStyle(
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
                                        onClone: () async {
                                          final id = gateway.id;
                                          if (id.isEmpty) return;
                                          await ref
                                              .read(
                                                mcpGatewaysControllerProvider
                                                    .notifier,
                                              )
                                              .cloneGateway(id);
                                        },
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
                  AsyncError(:final error) => ErrorView(
                    error: error,
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
    );
  }
}
