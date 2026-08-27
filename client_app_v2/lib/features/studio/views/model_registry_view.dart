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
import 'package:client_app/core/theme/app_spacing.dart';

/// Admin Studio View for managing the Model Registry.
/// Uses the 2026 Gold Standard Flat MVC Architecture (Dumb UI).
class ModelRegistryView extends HookConsumerWidget {
  final String id;
  const ModelRegistryView({super.key, required this.id});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final formKey = useMemoized(() => GlobalKey<FormState>());

    // 1. Data and loading states are read from Riverpod!
    final formState = ref.watch(modelRegistryFormProvider(id));

    return switch (formState) {
      AsyncLoading() => Scaffold(
        appBar: AppBar(title: Text(l10n.modelRegistryTitle)),
        body: const Center(child: CircularProgressIndicator()),
      ),
      AsyncError(:final error, :final stackTrace) => Scaffold(
        appBar: AppBar(title: Text(l10n.modelRegistryTitle)),
        body: ErrorView(
          error: error,
          stackTrace: stackTrace,
          compact: false,
          onRetry: () => ref.invalidate(modelRegistryFormProvider(id)),
        ),
      ),
      AsyncData(value: final payload) => _buildScaffold(
        context,
        ref,
        l10n,
        formKey,
        formState,
        payload,
      ),
    };
  }

  Widget _buildScaffold(
    BuildContext context,
    WidgetRef ref,
    AppLocalizations l10n,
    GlobalKey<FormState> formKey,
    AsyncValue<ModelConfig> formState,
    ModelConfig payload,
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
                padding: EdgeInsets.only(right: AppSpacing.s16),
                child: SizedBox(
                  width: AppSpacing.s16,
                  height: AppSpacing.s16,
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
          AppSpacing.w16,
        ],
      ),
      body: Form(
        key: formKey,
        child: ListView(
          padding: AppSpacing.p16,
          children: [
            _buildSystemAttributes(l10n, payload),
            AppSpacing.h24,
            _buildModelsSection(ref, l10n, payload),
          ],
        ),
      ),
    );
  }

  Widget _buildSystemAttributes(AppLocalizations l10n, ModelConfig data) {
    return Card(
      child: Padding(
        padding: AppSpacing.p16,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              l10n.systemMetaTitle,
              style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w600),
            ),
            AppSpacing.h16,
            TextFormField(
              initialValue: data.id,
              decoration: InputDecoration(labelText: l10n.configIdLabel),
              readOnly: true, // Server-side Minting: ID is immutable
            ),
            AppSpacing.h8,
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
  ) {
    final locationsAsync = ref.watch(supportedLocationsProvider);
    final supportedLocations = locationsAsync.value ?? [];

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
                final newKey =
                    'custom_${DateTime.now().millisecondsSinceEpoch}';
                newModels[newKey] = const LlmModelConfig(
                  provider: 'google',
                  modelName: 'vertex_ai/gemini-2.5-pro',
                  additionalParams: {
                    'platform': 'vertex_ai',
                    'vertex_location': 'europe-north1',
                  },
                );
                ref
                    .read(modelRegistryFormProvider(id).notifier)
                    .forceRebuild(payload.copyWith(models: newModels));
              },
              icon: const Icon(Icons.add),
              label: Text(l10n.addStrategyButton),
            ),
          ],
        ),
        AppSpacing.h16,
        if (payload.models.isEmpty) Text(l10n.noModelsDefined),
        ...providerGroups.entries.map((providerEntry) {
          final providerName = providerEntry.key;
          final providerModels = providerEntry.value;

          return Card(
            margin: const EdgeInsets.only(bottom: AppSpacing.s16),
            child: ExpansionTile(
              initiallyExpanded: true,
              title: Text('${l10n.providerLabel}: $providerName'),
              children: providerModels.entries.map((modelEntry) {
                final modelId = modelEntry.key;
                final cfg = modelEntry.value;

                // Determine active platform
                String currentPlatform = 'vertex_ai';
                if (cfg.provider == 'google') {
                  if (cfg.modelName.startsWith('gemini/') ||
                      (cfg.additionalParams['platform'] == 'ai_studio')) {
                    currentPlatform = 'ai_studio';
                  } else {
                    currentPlatform = 'vertex_ai';
                  }
                } else if (cfg.provider == 'ai_studio') {
                  currentPlatform = 'ai_studio';
                } else if (cfg.provider == 'openai') {
                  currentPlatform = 'openai';
                } else if (cfg.provider == 'anthropic') {
                  currentPlatform = 'anthropic';
                }

                // Determine active location
                final String currentLocation =
                    cfg.additionalParams['vertex_location'] as String? ??
                    'europe-north1';

                // Query models dynamically for this strategy's platform & location
                final strategyModelsAsync = ref.watch(
                  availableModelsProvider(
                    platform: currentPlatform,
                    location: currentPlatform == 'vertex_ai'
                        ? currentLocation
                        : null,
                  ),
                );
                final dynamicModels = strategyModelsAsync.value ?? [];

                return Padding(
                  padding: AppSpacing.p16,
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
                      AppSpacing.h8,

                      // 1. Platform Selector Dropdown
                      Padding(
                        padding: const EdgeInsets.only(bottom: AppSpacing.s12),
                        child: DropdownButtonFormField<String>(
                          initialValue: currentPlatform,
                          isExpanded: true,
                          decoration: InputDecoration(
                            labelText: l10n.platformLabel,
                            border: const OutlineInputBorder(),
                          ),
                          items: [
                            DropdownMenuItem(
                              value: 'vertex_ai',
                              child: Text(l10n.platformVertexAi),
                            ),
                            DropdownMenuItem(
                              value: 'ai_studio',
                              child: Text(l10n.platformAiStudio),
                            ),
                            DropdownMenuItem(
                              value: 'openai',
                              child: Text(l10n.platformOpenAi),
                            ),
                            DropdownMenuItem(
                              value: 'anthropic',
                              child: Text(l10n.platformAnthropic),
                            ),
                          ],
                          onChanged: (val) {
                            if (val == null) return;
                            String newProvider = val;
                            if (val == 'vertex_ai') {
                              newProvider = 'google';
                            } else if (val == 'ai_studio') {
                              newProvider = 'google';
                            }
                            final updatedParams = Map<String, dynamic>.from(
                              cfg.additionalParams,
                            );
                            updatedParams['platform'] = val;
                            updateModel(
                              modelId,
                              cfg.copyWith(
                                provider: newProvider,
                                additionalParams: updatedParams,
                              ),
                            );
                          },
                        ),
                      ),

                      // 2. Location Dropdown (Visible only for Google Vertex AI)
                      if (currentPlatform == 'vertex_ai')
                        Padding(
                          padding: const EdgeInsets.only(
                            bottom: AppSpacing.s12,
                          ),
                          child: DropdownButtonFormField<String>(
                            initialValue: currentLocation,
                            isExpanded: true,
                            decoration: InputDecoration(
                              labelText: l10n.locationLabel,
                              border: const OutlineInputBorder(),
                            ),
                            items: () {
                              final baseLocations =
                                  supportedLocations.isNotEmpty
                                  ? supportedLocations
                                  : [
                                      {
                                        'id': 'europe-north1',
                                        'label':
                                            'Hamina, Finland (europe-north1)',
                                      },
                                      {
                                        'id': 'europe-west1',
                                        'label':
                                            'St. Ghislain, Belgium (europe-west1)',
                                      },
                                      {
                                        'id': 'europe-west4',
                                        'label':
                                            'Eemshaven, Netherlands (europe-west4)',
                                      },
                                      {
                                        'id': 'europe-west3',
                                        'label':
                                            'Frankfurt, Germany (europe-west3)',
                                      },
                                      {
                                        'id': 'us-central1',
                                        'label':
                                            'Council Bluffs, Iowa (us-central1)',
                                      },
                                      {
                                        'id': 'us-east4',
                                        'label': 'Ashburn, Virginia (us-east4)',
                                      },
                                    ];

                              final existingIds = baseLocations
                                  .map((loc) => loc['id'] as String? ?? '')
                                  .toSet();

                              return [
                                if (currentLocation.isNotEmpty &&
                                    !existingIds.contains(currentLocation))
                                  DropdownMenuItem(
                                    value: currentLocation,
                                    child: Text(currentLocation),
                                  ),
                                ...baseLocations.map((loc) {
                                  final locId =
                                      loc['id'] as String? ?? 'europe-north1';
                                  final locLabel =
                                      loc['label'] as String? ?? locId;
                                  return DropdownMenuItem(
                                    value: locId,
                                    child: Text(locLabel),
                                  );
                                }),
                              ];
                            }(),
                            onChanged: (val) {
                              if (val != null) {
                                final updatedParams = Map<String, dynamic>.from(
                                  cfg.additionalParams,
                                );
                                updatedParams['vertex_location'] = val;
                                updateModel(
                                  modelId,
                                  cfg.copyWith(additionalParams: updatedParams),
                                );
                              }
                            },
                          ),
                        ),

                      // 3. Model Name Dropdown
                      Padding(
                        padding: const EdgeInsets.only(bottom: AppSpacing.s12),
                        child: DropdownButtonFormField<String>(
                          isExpanded: true,
                          initialValue:
                              (cfg.modelName.isNotEmpty &&
                                  (dynamicModels.contains(cfg.modelName) ||
                                      dynamicModels.isEmpty))
                              ? cfg.modelName
                              : (dynamicModels.isNotEmpty
                                    ? dynamicModels.first
                                    : null),
                          decoration: InputDecoration(
                            labelText: l10n.modelNameLabel,
                            border: const OutlineInputBorder(),
                          ),
                          items:
                              {
                                    if (cfg.modelName.isNotEmpty &&
                                        !dynamicModels.contains(cfg.modelName))
                                      cfg.modelName,
                                    ...dynamicModels,
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
                        l10n,
                        (val) => updateModel(
                          modelId,
                          cfg.copyWith(temperature: val),
                        ),
                      ),
                      _buildDoubleField(
                        cfg.frequencyPenalty,
                        l10n.frequencyPenaltyLabel,
                        l10n,
                        (val) => updateModel(
                          modelId,
                          cfg.copyWith(frequencyPenalty: val),
                        ),
                      ),
                      _buildDoubleField(
                        cfg.presencePenalty,
                        l10n.presencePenaltyLabel,
                        l10n,
                        (val) => updateModel(
                          modelId,
                          cfg.copyWith(presencePenalty: val),
                        ),
                      ),
                      _buildIntField(
                        cfg.maxTokens,
                        l10n.maxTokensLabel,
                        l10n,
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
                        l10n,
                        (val) => updateModel(modelId, cfg.copyWith(topP: val)),
                      ),
                      _buildIntField(
                        cfg.topK,
                        l10n.topKLabel,
                        l10n,
                        (val) => updateModel(modelId, cfg.copyWith(topK: val)),
                      ),
                      _buildIntField(
                        cfg.tpmLimit,
                        l10n.tpmLimitLabel,
                        l10n,
                        (val) =>
                            updateModel(modelId, cfg.copyWith(tpmLimit: val)),
                      ),
                      _buildIntField(
                        cfg.rpmLimit,
                        l10n.rpmLimitLabel,
                        l10n,
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
                        l10n,
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
    AppLocalizations l10n,
    Function(Map<String, dynamic>) onSaved,
  ) {
    final initialText = initialValue != null && initialValue.isNotEmpty
        ? const JsonEncoder.withIndent('  ').convert(initialValue)
        : '{}';
    return Padding(
      padding: const EdgeInsets.only(bottom: AppSpacing.s12),
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
              return l10n.jsonMustBeObjectError;
            }
          } catch (e) {
            return l10n.invalidJsonError;
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
      padding: const EdgeInsets.only(bottom: AppSpacing.s12),
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
    AppLocalizations l10n,
    Function(double) onChanged,
  ) {
    return Padding(
      padding: const EdgeInsets.only(bottom: AppSpacing.s12),
      child: TextFormField(
        initialValue: initialValue?.toString() ?? '',
        keyboardType: const TextInputType.numberWithOptions(decimal: true),
        decoration: InputDecoration(
          labelText: label,
          border: const OutlineInputBorder(),
        ),
        validator: (val) {
          if (val == null || val.isEmpty) return null;
          if (double.tryParse(val) == null) return l10n.mustBeNumberError;
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
    AppLocalizations l10n,
    Function(int) onChanged,
  ) {
    return Padding(
      padding: const EdgeInsets.only(bottom: AppSpacing.s12),
      child: TextFormField(
        initialValue: initialValue?.toString() ?? '',
        keyboardType: TextInputType.number,
        decoration: InputDecoration(
          labelText: label,
          border: const OutlineInputBorder(),
        ),
        validator: (val) {
          if (val == null || val.isEmpty) return null;
          if (int.tryParse(val) == null) return l10n.mustBeIntegerError;
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
      padding: const EdgeInsets.only(bottom: AppSpacing.s8),
      child: SwitchListTile(
        title: Text(label),
        value: initialValue,
        onChanged: onChanged,
      ),
    );
  }
}
