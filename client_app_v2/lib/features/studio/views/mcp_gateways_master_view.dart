import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/studio/controllers/mcp_gateways_controller.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/router/router.dart';
import 'package:client_app/features/studio/views/components/clone_entity_button.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/core/logging/logger_service.dart';

class McpGatewaysMasterView extends ConsumerWidget {
  const McpGatewaysMasterView({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final gatewaysState = ref.watch(mcpGatewaysControllerProvider);

    return SingleChildScrollView(
      padding: AppSpacing.p16,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                l10n.studioDashboardGatewaysTitle,
                style: Theme.of(context).textTheme.titleLarge,
              ),
              FilledButton.icon(
                onPressed: () async {
                  try {
                    final draft = await ref
                        .read(mcpGatewaysControllerProvider.notifier)
                        .createMcpGatewayDraft();
                    if (context.mounted) {
                      McpGatewayEditRoute(id: draft['id'] ?? '').go(context);
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
                label: Text(l10n.studioViewsNewBtn),
              ),
            ],
          ),
          AppSpacing.h8,
          Text(
            l10n.studioDashboardGatewaysDesc,
            style: Theme.of(context).textTheme.bodyMedium,
          ),
          AppSpacing.h16,
          switch (gatewaysState) {
            AsyncData(value: final gateways) => Builder(
              builder: (context) {
                if (gateways.isEmpty) {
                  return Text(l10n.noMcpGatewaysDefined);
                }
                return ListView.builder(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  itemCount: gateways.length,
                  itemBuilder: (context, index) {
                    final gateway = gateways[index];
                    final tools =
                        (gateway['allowed_tools'] as List?)?.length ?? 0;

                    return Card(
                      child: ListTile(
                        leading: Icon(
                          Icons.hub,
                          color: Theme.of(context).colorScheme.onSurfaceVariant,
                        ),
                        title: Text(
                          gateway['id']?.toString() ?? l10n.unnamedGateway,
                          style: const TextStyle(fontWeight: FontWeight.bold),
                        ),
                        subtitle: Text(
                          l10n.gatewaySubtitle(
                            tools,
                            gateway['is_active'] == true
                                ? l10n.activeStatus
                                : l10n.inactiveStatus,
                          ),
                        ),
                        trailing: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            CloneEntityButton(
                              onClone: () async {
                                final id = gateway['id']?.toString();
                                if (id == null) return;
                                await ref
                                    .read(
                                      mcpGatewaysControllerProvider.notifier,
                                    )
                                    .cloneGateway(id);
                              },
                            ),
                            const Icon(Icons.settings_ethernet),
                          ],
                        ),
                        onTap: () {
                          McpGatewayEditRoute(
                            id: gateway['id'] ?? '',
                          ).go(context);
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
                  ref.read(mcpGatewaysControllerProvider.notifier).refresh(),
            ),
          },
        ],
      ),
    );
  }
}
