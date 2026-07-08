import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/features/studio/controllers/model_registry_controller.dart';
import 'package:client_app/features/studio/models/model_config.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/core/logging/logger_service.dart';

/// Admin Studio View for managing the Model Registry.
/// Uses the 2026 Gold Standard Flat MVC Architecture (Dumb UI).
class ModelRegistryView extends HookConsumerWidget {
  final String id;
  const ModelRegistryView({super.key, required this.id});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final formKey = useMemoized(() => GlobalKey<FormState>());
    final availableModelsAsync = ref.watch(availableModelsProvider);
    final availableModels = availableModelsAsync.value ?? [];

    // 1. Data and loading states are read from Riverpod!
    final formState = ref.watch(modelRegistryFormProvider(id));

    return formState.when(
      loading: () => Scaffold(
        appBar: AppBar(title: Text(l10n.modelRegistryTitle)),
        body: const Center(child: CircularProgressIndicator()),
      ),
      error: (e, st) => Scaffold(
        appBar: AppBar(title: Text(l10n.modelRegistryTitle)),
        body: ErrorView(
          error: e,
          stackTrace: st,
          compact: false,
          onRetry: () => ref.invalidate(modelRegistryFormProvider(id)),
        ),
      ),
      data: (payload) {
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
    AsyncValue<ModelConfig> formState,
    ModelConfig payload,
    List<String> availableModels,
  ) {
    Future<void> deleteRegistry() async {
      final String idToDelete = payload.id;
      if (idToDelete.isEmpty) return;

      final type = payload.type;
      final nameToDisplay = type.isNotEmpty ? type : idToDelete;

      final confirm = await showDialog<bool>(
        context: context,
        builder: (ctx) => AlertDialog(
          title: Text(l10n.deleteConfigTitle),
          content: Text(l10n.deleteConfigConfirmation(nameToDisplay)),
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
          final latestPayload =
              ref.read(modelRegistryFormProvider(id)).value ?? payload;
          await notifier.submit(latestPayload);
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
            onPressed: formState.isLoading ? null : saveRegistry,
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

  Widget _buildSystemAttributes(AppLocalizations l10n, ModelConfig data) {
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
              initialValue: data.id,
              decoration: InputDecoration(labelText: l10n.configIdLabel),
              readOnly: true, // Server-side Minting: ID is immutable
            ),
            const SizedBox(height: 8),
            TextFormField(
              initialValue: data.type,
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
    ModelConfig payload,
    List<String> availableModels,
  ) {
    final Map<String, Map<String, LlmModelConfig>> providerGroups = {};
    for (final entry in payload.models.entries) {
      final provider = entry.value.provider.isNotEmpty
          ? entry.value.provider
          : 'unknown';
      providerGroups.putIfAbsent(provider, () => {})[entry.key] = entry.value;
    }

    void updateModel(String modelId, LlmModelConfig newConfig) {
      final newModels = Map<String, LlmModelConfig>.from(payload.models);
      newModels[modelId] = newConfig;
      ref
          .read(modelRegistryFormProvider(id).notifier)
          .forceRebuild(payload.copyWith(models: newModels));
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              l10n.providerSettings,
              style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w600),
            ),
            FilledButton.icon(
              onPressed: () {
                final newModels = Map<String, LlmModelConfig>.from(
                  payload.models,
                );
                final tempId = 'new_strategy_${newModels.length + 1}';
                newModels[tempId] = const LlmModelConfig();
                ref
                    .read(modelRegistryFormProvider(id).notifier)
                    .forceRebuild(payload.copyWith(models: newModels));
              },
              icon: const Icon(Icons.add),
              label: const Text('Add Strategy'),
            ),
          ],
        ),
        const SizedBox(height: 16),
        if (payload.models.isEmpty) Text(l10n.noModelsDefined),
        ...providerGroups.entries.map((providerEntry) {
          final providerName = providerEntry.key;
          final providerModels = providerEntry.value;

          return Card(
            margin: const EdgeInsets.only(bottom: 16.0),
            child: ExpansionTile(
              initiallyExpanded: true,
              title: Text('${l10n.providerLabel}: $providerName'),
              children: providerModels.entries.map((modelEntry) {
                final modelId = modelEntry.key;
                final cfg = modelEntry.value;

                return Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            '${l10n.strategyLabel}: $modelId',
                            style: const TextStyle(
                              fontWeight: FontWeight.bold,
                              color: Colors.blue,
                            ),
                          ),
                          IconButton(
                            icon: Icon(
                              Icons.delete,
                              color: Theme.of(ref.context).colorScheme.error,
                            ),
                            onPressed: () {
                              final newModels =
                                  Map<String, LlmModelConfig>.from(
                                    payload.models,
                                  );
                              newModels.remove(modelId);
                              ref
                                  .read(modelRegistryFormProvider(id).notifier)
                                  .forceRebuild(
                                    payload.copyWith(models: newModels),
                                  );
                            },
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      // Strategy Config fields
                      Padding(
                        padding: const EdgeInsets.only(bottom: 12.0),
                        child: TextFormField(
                          initialValue: cfg.provider,
                          decoration: InputDecoration(
                            labelText: 'Provider (e.g. google, openai)',
                            border: const OutlineInputBorder(),
                          ),
                          onChanged: (val) {
                            updateModel(modelId, cfg.copyWith(provider: val));
                          },
                        ),
                      ),

                      Padding(
                        padding: const EdgeInsets.only(bottom: 12.0),
                        child: DropdownButtonFormField<String>(
                          initialValue:
                              (cfg.modelName.isNotEmpty &&
                                  (availableModels.contains(cfg.modelName) ||
                                      availableModels.isEmpty))
                              ? cfg.modelName
                              : (availableModels.isNotEmpty
                                    ? availableModels.first
                                    : null),
                          decoration: InputDecoration(
                            labelText: l10n.modelNameLabel,
                            border: const OutlineInputBorder(),
                          ),
                          items:
                              {
                                    if (cfg.modelName.isNotEmpty &&
                                        !availableModels.contains(
                                          cfg.modelName,
                                        ))
                                      cfg.modelName,
                                    ...availableModels,
                                  }
                                  .map(
                                    (m) => DropdownMenuItem(
                                      value: m,
                                      child: Text(m),
                                    ),
                                  )
                                  .toList(),
                          onChanged: (val) {
                            if (val != null) {
                              updateModel(
                                modelId,
                                cfg.copyWith(modelName: val),
                              );
                            }
                          },
                        ),
                      ),

                      _buildDoubleField(
                        cfg.temperature,
                        l10n.temperatureLabel,
                        (val) => updateModel(
                          modelId,
                          cfg.copyWith(temperature: val),
                        ),
                      ),
                      _buildDoubleField(
                        cfg.frequencyPenalty,
                        l10n.frequencyPenaltyLabel,
                        (val) => updateModel(
                          modelId,
                          cfg.copyWith(frequencyPenalty: val),
                        ),
                      ),
                      _buildDoubleField(
                        cfg.presencePenalty,
                        l10n.presencePenaltyLabel,
                        (val) => updateModel(
                          modelId,
                          cfg.copyWith(presencePenalty: val),
                        ),
                      ),
                      _buildIntField(
                        cfg.maxTokens,
                        l10n.maxTokensLabel,
                        (val) =>
                            updateModel(modelId, cfg.copyWith(maxTokens: val)),
                      ),
                      _buildStringField(
                        cfg.parsingMode,
                        l10n.parsingModeLabel,
                        (val) => updateModel(
                          modelId,
                          cfg.copyWith(parsingMode: val),
                        ),
                      ),
                      _buildDoubleField(
                        cfg.topP,
                        l10n.topPLabel,
                        (val) => updateModel(modelId, cfg.copyWith(topP: val)),
                      ),
                      _buildIntField(
                        cfg.topK,
                        l10n.topKLabel,
                        (val) => updateModel(modelId, cfg.copyWith(topK: val)),
                      ),
                      _buildIntField(
                        cfg.tpmLimit,
                        l10n.tpmLimitLabel,
                        (val) =>
                            updateModel(modelId, cfg.copyWith(tpmLimit: val)),
                      ),
                      _buildIntField(
                        cfg.rpmLimit,
                        l10n.rpmLimitLabel,
                        (val) =>
                            updateModel(modelId, cfg.copyWith(rpmLimit: val)),
                      ),

                      _buildStringField(
                        cfg.cachingStrategy,
                        l10n.cachingStrategyLabel,
                        (val) => updateModel(
                          modelId,
                          cfg.copyWith(
                            cachingStrategy: val.trim().isEmpty ? null : val,
                          ),
                        ),
                      ),
                      _buildJsonField(
                        cfg.additionalParams,
                        l10n.additionalParamsLabel,
                        (val) => updateModel(
                          modelId,
                          cfg.copyWith(additionalParams: val),
                        ),
                      ),

                      _buildBoolField(
                        cfg.supportsGrounding,
                        l10n.supportsGroundingLabel,
                        (val) => updateModel(
                          modelId,
                          cfg.copyWith(supportsGrounding: val),
                        ),
                      ),
                      _buildBoolField(
                        cfg.isActive,
                        l10n.isActiveLabel,
                        (val) =>
                            updateModel(modelId, cfg.copyWith(isActive: val)),
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

  Widget _buildJsonField(
    Map<String, dynamic>? initialValue,
    String label,
    Function(Map<String, dynamic>) onSaved,
  ) {
    final initialText = initialValue != null && initialValue.isNotEmpty
        ? const JsonEncoder.withIndent('  ').convert(initialValue)
        : '{}';
    return Padding(
      padding: const EdgeInsets.only(bottom: 12.0),
      child: TextFormField(
        initialValue: initialText,
        maxLines: 4,
        decoration: InputDecoration(
          labelText: label,
          border: const OutlineInputBorder(),
        ),
        validator: (val) {
          if (val == null || val.trim().isEmpty) return null;
          try {
            final decoded = jsonDecode(val);
            if (decoded is! Map<String, dynamic>) {
              return 'Must be a valid JSON object (e.g. {"key": "val"})';
            }
          } catch (e) {
            return 'Invalid JSON';
          }
          return null;
        },
        onSaved: (val) {
          if (val != null && val.trim().isNotEmpty) {
            try {
              final decoded = jsonDecode(val);
              if (decoded is Map<String, dynamic>) {
                onSaved(decoded);
              }
            } catch (_) {}
          } else {
            onSaved({});
          }
        },
      ),
    );
  }

  Widget _buildStringField(
    String? initialValue,
    String label,
    Function(String) onChanged,
  ) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12.0),
      child: TextFormField(
        initialValue: initialValue ?? '',
        decoration: InputDecoration(
          labelText: label,
          border: const OutlineInputBorder(),
        ),
        onChanged: onChanged,
      ),
    );
  }

  Widget _buildDoubleField(
    double? initialValue,
    String label,
    Function(double) onChanged,
  ) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12.0),
      child: TextFormField(
        initialValue: initialValue?.toString() ?? '',
        keyboardType: const TextInputType.numberWithOptions(decimal: true),
        decoration: InputDecoration(
          labelText: label,
          border: const OutlineInputBorder(),
        ),
        validator: (val) {
          if (val == null || val.isEmpty) return null;
          if (double.tryParse(val) == null) return 'Must be a number';
          return null;
        },
        onChanged: (val) {
          if (val.isNotEmpty && double.tryParse(val) != null) {
            onChanged(double.parse(val));
          }
        },
      ),
    );
  }

  Widget _buildIntField(
    int? initialValue,
    String label,
    Function(int) onChanged,
  ) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12.0),
      child: TextFormField(
        initialValue: initialValue?.toString() ?? '',
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
        onChanged: (val) {
          if (val.isNotEmpty && int.tryParse(val) != null) {
            onChanged(int.parse(val));
          }
        },
      ),
    );
  }

  Widget _buildBoolField(
    bool initialValue,
    String label,
    Function(bool) onChanged,
  ) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8.0),
      child: SwitchListTile(
        title: Text(label),
        value: initialValue,
        onChanged: onChanged,
      ),
    );
  }
}
