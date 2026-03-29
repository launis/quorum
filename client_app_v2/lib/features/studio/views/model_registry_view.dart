import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/features/studio/controllers/model_registry_controller.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/utils/safe_cast.dart';

/// Admin Studio View for managing the Model Registry (SystemConfig).
/// Uses the 2026 Gold Standard Flat MVC Architecture (Dumb UI).
class ModelRegistryView extends HookConsumerWidget {
  final String id;
  // initialData drops to null here since Gold Standard requires native ID resolution
  const ModelRegistryView({super.key, required this.id});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final formKey = useMemoized(() => GlobalKey<FormState>());
    final availableModelsAsync = ref.watch(availableModelsProvider);
    final availableModels = availableModelsAsync.value ?? [];

    // 1. Data and loading states are read from Riverpod! No useEffect for fetching!
    final formState = ref.watch(modelRegistryFormProvider(id));

    return formState.when(
      loading:
          () => Scaffold(
            appBar: AppBar(title: Text(l10n.modelRegistryTitle)),
            body: const Center(child: CircularProgressIndicator()),
          ),
      error:
          (e, st) => Scaffold(
            appBar: AppBar(title: Text(l10n.modelRegistryTitle)),
            body: ErrorView(
              error: e,
              stackTrace: st,
              compact: false,
              onRetry: () => ref.invalidate(modelRegistryFormProvider(id)),
            ),
          ),
      data: (payload) {
        // The UI is a pure renderer of the business payload
        return _buildScaffold(
          context,
          ref,
          l10n,
          formKey,
          formState,
          payload,
          availableModels,
        );
      },
    );
  }

  Widget _buildScaffold(
    BuildContext context,
    WidgetRef ref,
    AppLocalizations l10n,
    GlobalKey<FormState> formKey,
    AsyncValue<Map<String, dynamic>> formState,
    Map<String, dynamic> payload,
    List<String> availableModels,
  ) {
    Future<void> deleteRegistry() async {
      final String idToDelete = payload['id']?.toString() ?? '';
      if (idToDelete.isEmpty || id == 'new') return;

      final confirm = await showDialog<bool>(
        context: context,
        builder:
            (ctx) => AlertDialog(
              title: Text(l10n.deleteConfigTitle),
              content: Text(l10n.deleteConfigConfirmation(idToDelete)),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(ctx, false),
                  child: Text(l10n.cancelButton),
                ),
                FilledButton(
                  style: FilledButton.styleFrom(
                    backgroundColor: Theme.of(context).colorScheme.error,
                  ),
                  onPressed: () => Navigator.pop(ctx, true),
                  child: Text(l10n.deleteButton),
                ),
              ],
            ),
      );

      if (confirm == true) {
        try {
          await ref
              .read(modelRegistryControllerProvider.notifier)
              .deleteConfig(idToDelete);
          if (!context.mounted) return;
          context.pop();
        } catch (e) {
          if (!context.mounted) return;
          ref
              .read(loggerServiceProvider)
              .error('Studio', 'Failed to delete registry config: $e', e);
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(l10n.deleteFailedError(e.toString())),
              backgroundColor: Theme.of(context).colorScheme.error,
            ),
          );
        }
      }
    }

    Future<void> saveRegistry() async {
      if (formKey.currentState!.validate()) {
        formKey.currentState!.save();
        try {
          final notifier = ref.read(modelRegistryFormProvider(id).notifier);
          await notifier.submit(payload);
          if (!context.mounted) return;
          ScaffoldMessenger.of(
            context,
          ).showSnackBar(SnackBar(content: Text(l10n.configSavedSuccess)));
        } catch (e) {
          if (!context.mounted) return;
          ref
              .read(loggerServiceProvider)
              .error('Studio', 'Failed to save registry config: $e', e);
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(l10n.saveFailedError(e.toString())),
              backgroundColor: Theme.of(context).colorScheme.error,
            ),
          );
        }
      }
    }

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.modelRegistryTitle),
        actions: [
          if (formState.isLoading)
            const Center(
              child: Padding(
                padding: EdgeInsets.only(right: 16.0),
                child: SizedBox(
                  width: 16,
                  height: 16,
                  child: CircularProgressIndicator(strokeWidth: 2),
                ),
              ),
            ),
          if (id != 'new')
            IconButton(
              icon: Icon(
                Icons.delete,
                color: Theme.of(context).colorScheme.error,
              ),
              onPressed: formState.isLoading ? null : deleteRegistry,
              tooltip: l10n.deleteConfigTitle,
            ),
          FilledButton.icon(
            icon: const Icon(Icons.save),
            label: Text(l10n.studioSaveButton),
            onPressed:
                formState.isLoading
                    ? null
                    : saveRegistry, // Read isLoading directly from Riverpod!
          ),
          const SizedBox(width: 16),
        ],
      ),
      body: Form(
        key: formKey,
        child: ListView(
          padding: const EdgeInsets.all(16.0),
          children: [
            _buildSystemAttributes(l10n, payload),
            const SizedBox(height: 24),
            _buildModelsSection(ref, l10n, payload, availableModels),
          ],
        ),
      ),
    );
  }

  Widget _buildSystemAttributes(
    AppLocalizations l10n,
    Map<String, dynamic> data,
  ) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              l10n.systemMetaTitle,
              style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 16),
            TextFormField(
              initialValue: data['id']?.toString(),
              decoration: InputDecoration(labelText: l10n.configIdLabel),
              readOnly: true, // Opaque ID Mandate: NEVER editable manually
            ),
            const SizedBox(height: 8),
            TextFormField(
              initialValue: data['type']?.toString(),
              decoration: InputDecoration(labelText: l10n.configTypeLabel),
              readOnly: true,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildModelsSection(
    WidgetRef ref,
    AppLocalizations l10n,
    Map<String, dynamic> data,
    List<String> availableModels,
  ) {
    final models = data['models'] as Map<String, dynamic>? ?? {};

    // Group by provider for UI display
    final Map<String, Map<String, dynamic>> providerGroups = {};
    for (final entry in models.entries) {
      final modelId = entry.key;
      final attrs = entry.value;
      if (attrs is Map<String, dynamic>) {
        final provider = SafeCast.safeString(attrs['provider'], 'unknown');
        providerGroups.putIfAbsent(provider, () => {})[modelId] = attrs;
      }
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text(
          l10n.providerSettings,
          style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w600),
        ),
        const SizedBox(height: 16),
        if (models.isEmpty) Text(l10n.noModelsDefined),
        ...providerGroups.entries.map((providerEntry) {
          final providerName = providerEntry.key;
          final providerModels = providerEntry.value;

          return Card(
            margin: const EdgeInsets.only(bottom: 16.0),
            child: ExpansionTile(
              initiallyExpanded: true,
              title: Text('${l10n.providerLabel}: $providerName'),
              children:
                  providerModels.entries.map((modelEntry) {
                    final modelId = modelEntry.key;
                    final fields = modelEntry.value as Map<String, dynamic>;

                    return Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            '${l10n.strategyLabel}: $modelId',
                            style: const TextStyle(
                              fontWeight: FontWeight.bold,
                              color: Colors.blue,
                            ),
                          ),
                          const SizedBox(height: 8),
                          _buildModelNameDropdown(
                            ref,
                            fields,
                            'model_name',
                            l10n.modelNameLabel,
                            availableModels,
                          ),
                          _buildDoubleField(
                            fields,
                            'temperature',
                            l10n.temperatureLabel,
                          ),
                          _buildIntField(
                            fields,
                            'max_tokens',
                            l10n.maxTokensLabel,
                          ),
                          _buildStringField(
                            fields,
                            'parsing_mode',
                            l10n.parsingModeLabel,
                          ),
                          _buildDoubleField(fields, 'top_p', l10n.topPLabel),
                          _buildIntField(
                            fields,
                            'tpm_limit',
                            l10n.tpmLimitLabel,
                          ),
                          _buildIntField(
                            fields,
                            'rpm_limit',
                            l10n.rpmLimitLabel,
                          ),
                          _buildBoolField(
                            ref,
                            fields,
                            'supports_grounding',
                            l10n.supportsGroundingLabel,
                          ),
                          _buildBoolField(
                            ref,
                            fields,
                            'is_active',
                            l10n.isActiveLabel,
                          ),
                          const Divider(height: 32),
                        ],
                      ),
                    );
                  }).toList(),
            ),
          );
        }),
      ],
    );
  }

  Widget _buildStringField(Map<String, dynamic> map, String key, String label) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12.0),
      child: TextFormField(
        initialValue: map[key]?.toString() ?? '',
        decoration: InputDecoration(
          labelText: label,
          border: const OutlineInputBorder(),
        ),
        onSaved: (val) => map[key] = val,
      ),
    );
  }

  Widget _buildModelNameDropdown(
    WidgetRef ref,
    Map<String, dynamic> map,
    String key,
    String label,
    List<String> availableModels,
  ) {
    final currentValue = map[key]?.toString();
    final items = availableModels.toList();
    if (currentValue != null &&
        currentValue.isNotEmpty &&
        !items.contains(currentValue)) {
      items.add(currentValue);
    }

    return Padding(
      padding: const EdgeInsets.only(bottom: 12.0),
      child: DropdownButtonFormField<String>(
        key: ValueKey(items.length),
        decoration: InputDecoration(
          labelText: label,
          border: const OutlineInputBorder(),
        ),
        initialValue: items.contains(currentValue) ? currentValue : null,
        items:
            items.map((modelId) {
              return DropdownMenuItem(value: modelId, child: Text(modelId));
            }).toList(),
        onChanged: (val) {
          if (val != null) {
            map[key] = val; // Synchronous pure map edit
            ref.read(modelRegistryFormProvider(id).notifier).forceRebuild();
          }
        },
      ),
    );
  }

  Widget _buildDoubleField(Map<String, dynamic> map, String key, String label) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12.0),
      child: TextFormField(
        initialValue: map[key]?.toString() ?? '0.0',
        keyboardType: const TextInputType.numberWithOptions(decimal: true),
        decoration: InputDecoration(
          labelText: label,
          border: const OutlineInputBorder(),
        ),
        validator: (val) {
          if (val == null || val.isEmpty) return null; // Optional
          if (double.tryParse(val) == null) return 'Must be a number';
          return null;
        },
        onSaved: (val) {
          if (val != null && val.isNotEmpty) {
            map[key] = double.tryParse(val);
          }
        },
      ),
    );
  }

  Widget _buildIntField(Map<String, dynamic> map, String key, String label) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12.0),
      child: TextFormField(
        initialValue: map[key]?.toString() ?? '0',
        keyboardType: TextInputType.number,
        decoration: InputDecoration(
          labelText: label,
          border: const OutlineInputBorder(),
        ),
        validator: (val) {
          if (val == null || val.isEmpty) return null;
          if (int.tryParse(val) == null) return 'Must be an integer';
          return null;
        },
        onSaved: (val) {
          if (val != null && val.isNotEmpty) {
            map[key] = int.tryParse(val);
          }
        },
      ),
    );
  }

  Widget _buildBoolField(
    WidgetRef ref,
    Map<String, dynamic> map,
    String key,
    String label,
  ) {
    // Value could be null initially.
    final currentValue = map[key] as bool? ?? false;

    return Padding(
      padding: const EdgeInsets.only(bottom: 8.0),
      child: SwitchListTile(
        title: Text(label),
        value: currentValue,
        onChanged: (val) {
          map[key] = val; // Synchronous pure map edit
          ref.read(modelRegistryFormProvider(id).notifier).forceRebuild();
        },
      ),
    );
  }
}
