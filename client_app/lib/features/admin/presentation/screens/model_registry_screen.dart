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

    ref.listen<AsyncValue<ModelRegistryState>>(
      modelRegistryControllerProvider,
      (_, next) {
        if (next.hasError && !next.isLoading) {
          final errStub = next.error.toString();
          String? title;
          String? content;

          if (errStub.contains('403') || errStub.contains('default strategy')) {
            title = 'Cannot Delete Default';
            content = 'The System Default strategy cannot be deleted. Change the default in Global Settings first.';
          } else if (errStub.contains('409') || errStub.contains('in use')) {
            title = 'Strategy In Use';
            content = 'This strategy is currently used by one or more Workflow Steps. Remove the assignment before deleting.';
          } else {
             // Optional: Show generic error for other issues? 
             // For now let the body error handler show it if it's not a specific actionable safety error
             // OR show a snackbar for generic API errors
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text('Error: ${next.error}')),
              );
              return;
          }

          if (title != null) {
             showDialog(
              context: context,
              builder: (ctx) => AlertDialog(
                title: Text(title!),
                content: Text(content!),
                actions: [
                  TextButton(
                    onPressed: () {
                       Navigator.pop(ctx);
                       // Optional: Clear error?
                       // ref.refresh(modelRegistryControllerProvider);
                    },
                    child: const Text('OK'),
                  ),
                ],
              ),
            );
          }
        }
      },
    );

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
                    trailing: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        IconButton(
                          icon: const Icon(Icons.add),
                          tooltip: l10n.addStrategyTooltip ?? 'Add Strategy',
                          onPressed: () => _showAddStrategyDialog(context, ref, controller),
                        ),
                        IconButton(
                          icon: const Icon(Icons.refresh),
                          onPressed:
                              () => ref.refresh(
                                modelRegistryControllerProvider,
                              ),
                        ),
                      ],
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
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      configOrNull.modelName,
                      style: Theme.of(context).textTheme.headlineSmall,
                    ),
                    IconButton(
                      icon: const Icon(Icons.delete, color: Colors.red),
                      tooltip: 'Delete Strategy',
                      onPressed: () async {
                        final confirm = await showDialog<bool>(
                          context: context,
                          builder: (context) => AlertDialog(
                            title: const Text('Delete Strategy?'),
                            content: Text(
                                'Are you sure you want to delete "${configOrNull.id}"? This cannot be undone.'),
                            actions: [
                              TextButton(
                                onPressed: () => Navigator.pop(context, false),
                                child: const Text('Cancel'),
                              ),
                              FilledButton(
                                style: FilledButton.styleFrom(
                                  backgroundColor: Colors.red,
                                ),
                                onPressed: () => Navigator.pop(context, true),
                                child: const Text('Delete'),
                              ),
                            ],
                          ),
                        );

                        if (confirm == true) {
                          controller.deleteConfig(providerId);
                        }
                      },
                    ),
                  ],
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

Future<void> _showAddStrategyDialog(BuildContext context, WidgetRef ref, ModelRegistryController controller) async {
  // Step 1: Select Provider
  final selectedProvider = await showDialog<String>(
    context: context,
    builder: (context) => SimpleDialog(
      title: const Text('Select Provider'),
      children: [
        SimpleDialogOption(
          onPressed: () => Navigator.pop(context, 'google'),
          child: const ListTile(
            leading: Icon(Icons.cloud_circle, color: Colors.blue),
            title: Text('Google (Vertex AI)'),
            subtitle: Text('Gemini Models'),
          ),
        ),
        SimpleDialogOption(
          onPressed: () => Navigator.pop(context, 'openai'),
          child: const ListTile(
            leading: Icon(Icons.auto_awesome, color: Colors.green),
            title: Text('OpenAI'),
            subtitle: Text('GPT Models'),
          ),
        ),
      ],
    ),
  );

  if (selectedProvider == null) return;

  // Step 2: Name Strategy
  if (!context.mounted) return;

  final formKey = GlobalKey<FormState>();
  String strategyName = '';
  
  await showDialog(
    context: context,
    builder: (context) => AlertDialog(
      title: Text('New ${selectedProvider == 'google' ? 'Google' : 'OpenAI'} Strategy'),
      content: Form(
        key: formKey,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextFormField(
              decoration: InputDecoration(
                labelText: 'Strategy Name',
                hintText: 'e.g. creative, fast, analisys_v1',
                prefixText: '$selectedProvider/',
              ),
              validator: (value) {
                if (value == null || value.isEmpty) return 'Required';
                if (!RegExp(r'^[a-z0-9_]+$').hasMatch(value)) return 'Lowercase, numbers, underscores only.';
                return null;
              },
              onSaved: (value) => strategyName = value!,
            ),
            const SizedBox(height: 8),
            Text(
              'Final ID will be: $selectedProvider/<name>',
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ],
        ),
      ),
      actions: [
        TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
        FilledButton(
          onPressed: () {
            if (formKey.currentState!.validate()) {
              formKey.currentState!.save();
              
              // Construct ID: provider/strategy
              final fullId = '$selectedProvider/$strategyName';
              
              // Create with default values based on provider
              final newConfig = LLMProviderConfig(
                id: fullId,
                provider: selectedProvider, 
                modelName: selectedProvider == 'google' ? 'gemini-1.5-pro' : 'gpt-4o', // Smart defaults
              );
              
              controller.saveConfig(fullId, newConfig);
              controller.selectProvider(fullId); // Auto-select
              Navigator.pop(context);
            }
          },
          child: const Text('Create'),
        ),
      ],
    ),
  );
}
