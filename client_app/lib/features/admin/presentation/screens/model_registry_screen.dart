import 'package:flutter/material.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import '../../domain/models/model_registry.dart';
import '../providers/model_registry_controller.dart';
import '../widgets/provider_config_form.dart';
import '../widgets/adhoc_test_panel.dart';

class ModelRegistryScreen extends HookConsumerWidget {
  const ModelRegistryScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // ignore: unnecessary_non_null_assertion
    final l10n = AppLocalizations.of(context)!;
    final asyncState = ref.watch(modelRegistryControllerProvider);
    final controller = ref.read(modelRegistryControllerProvider.notifier);

    return Scaffold(
      body: asyncState.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (err, st) => Center(child: SelectableText('Error: $err')),
        data: (state) => Row(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Left Pane: List
          Expanded(
            flex: 1,
            child: Card(
              margin: const EdgeInsets.all(8.0),
              child: Column(
                children: [
                  ListTile(
                    title: Text(
                      l10n.modelRegistryTitle,
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                    trailing: IconButton(
                      icon: const Icon(Icons.refresh),
                      onPressed:
                          () => ref.refresh(
                            modelRegistryControllerProvider,
                          ), // Clean refresh
                    ),
                  ),
                  const Divider(),
                  Expanded(
                    child: ListView.builder(
                            itemCount: state.providers.length,
                            itemBuilder: (context, index) {
                              final p = state.providers[index];
                              final isSelected =
                                  p.id == state.selectedProviderId;
                              return ListTile(
                                title: Text(
                                  p.id,
                                  style: const TextStyle(fontWeight: FontWeight.bold),
                                ),
                                subtitle: Text('${p.provider} • ${p.modelName}'),
                                selected: isSelected,
                                onTap:
                                    () => controller.selectProvider(p.id),
                                trailing:
                                    isSelected
                                        ? const Icon(
                                          Icons.arrow_forward_ios,
                                          size: 16,
                                        )
                                        : null,
                              );
                            },
                          ),
                  ),
                ],
              ),
            ),
          ),

          // Right Pane: Detail
          Expanded(
            flex: 2,
            child:
                state.selectedProviderId == null
                    ? Center(
                      child: Text(
                        l10n.selectProviderPlaceholder,
                        style: Theme.of(context).textTheme.bodyLarge,
                      ),
                    )
                    : _DetailsPane(
                      key: ValueKey(
                        state.selectedProviderId,
                      ), // Force rebuild on switch
                      providerId: state.selectedProviderId!,
                      state: state,
                      controller: controller,
                    ),
          ),
        ],
      ),
    ));
  }
}

class _DetailsPane extends HookConsumerWidget {
  final String providerId;
  final ModelRegistryState state;
  final ModelRegistryController controller;

  const _DetailsPane({
    super.key,
    required this.providerId,
    required this.state,
    required this.controller,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // ignore: unnecessary_non_null_assertion
    final l10n = AppLocalizations.of(context)!;

    // Find the config object
    final configOrNull =
        state.providers
            .where((p) => p.id == providerId)
            .firstOrNull;

    if (configOrNull == null) return const SizedBox.shrink();

    return DefaultTabController(
      length: 2,
      child: Column(
        children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            decoration: BoxDecoration(
              border: Border(
                bottom: BorderSide(
                  color: Theme.of(context).dividerColor,
                ),
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(
                  configOrNull.modelName,
                  style: Theme.of(context).textTheme.headlineSmall,
                ),
                const SizedBox(height: 8),
                TabBar(
                  labelColor: Theme.of(context).colorScheme.primary,
                  unselectedLabelColor: Theme.of(context).disabledColor,
                  tabs: [
                    Tab(
                      text: l10n.providerSettings,
                      icon: const Icon(Icons.settings),
                    ),
                    Tab(text: l10n.testLab, icon: const Icon(Icons.science)),
                  ],
                ),
              ],
            ),
          ),
          Expanded(
            child: TabBarView(
              children: [
                // Tab 1: Config
                ProviderConfigForm(
                  config: configOrNull,
                  isSaving: state.isSaving,
                  onSave:
                      (newConfig) =>
                          controller.saveConfig(providerId, newConfig),
                ),

                // Tab 2: Test
                AdHocTestPanel(
                  testResult: state.testResult,
                  providerType: configOrNull.provider,
                  onRunTest: (req) {
                    // Merge UI inputs with Provider Type.
                    // Inject Strategy ID and Model Name to allow Backend to resolve "Standard Execution" from DB.
                    final extraParams = Map<String, dynamic>.from(req.modelParams);
                    if (configOrNull != null) {
                      extraParams['strategy_id'] = configOrNull.id;
                      extraParams['model_name'] = configOrNull.modelName;
                      // Also merge additionalParams (max_tokens)
                      extraParams.addAll(configOrNull.additionalParams);
                    }

                    final enrichedReq = req.copyWith(
                      modelParams: extraParams,
                    );
                    
                    controller.runTest(enrichedReq);
                  },
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
