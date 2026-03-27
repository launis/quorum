import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/studio/controllers/mcp_gateways_controller.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/router/router.dart';
import 'package:client_app/features/studio/views/components/clone_entity_button.dart';

class McpGatewaysMasterView extends ConsumerWidget {
  const McpGatewaysMasterView({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final gatewaysState = ref.watch(mcpGatewaysControllerProvider);

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
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
                onPressed: () {
                  const McpGatewayNewRoute().go(context);
                },
                icon: const Icon(Icons.add),
                label: const Text('New Gateway'),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            l10n.studioDashboardGatewaysDesc,
            style: Theme.of(context).textTheme.bodyMedium,
          ),
          const SizedBox(height: 16),
          gatewaysState.when(
            data: (gateways) {
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
                      leading: const Icon(Icons.hub, color: Colors.blueGrey),
                      title: Text(
                        gateway['id']?.toString() ?? 'Unnamed Gateway',
                        style: const TextStyle(fontWeight: FontWeight.bold),
                      ),
                      subtitle: Text(
                        'Allowed Tools: $tools | Status: ${gateway['is_active'] == true ? "Active" : "Inactive"}',
                      ),
                      trailing: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          CloneEntityButton(
                            onClone: () async {
                              final id = gateway['id']?.toString();
                              if (id == null) return;
                              await ref
                                  .read(mcpGatewaysControllerProvider.notifier)
                                  .cloneGateway(id);
                            },
                          ),
                          const Icon(Icons.settings_ethernet),
                        ],
                      ),
                      onTap: () {
                        McpGatewayEditRoute(
                          id: gateway['id'] ?? '',
                          $extra: gateway,
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
                              .read(mcpGatewaysControllerProvider.notifier)
                              .refresh(),
                ),
          ),
        ],
      ),
    );
  }
}
