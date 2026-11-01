import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/features/studio/controllers/model_registry_controller.dart';
import 'package:client_app/features/studio/models/gcp_location.dart';
import 'package:client_app/features/studio/models/model_config.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/router/router.dart';
import 'package:client_app/theme/app_colors.dart';

/// Admin Studio View for managing the Sovereign Model Registry stack.
/// Uses Desktop Pro Tool UX with 1200px bounded canvas, PopScope dirty checking,
/// in-view stack cloning, and 4 canonical cognitive tier cards.
class ModelRegistryView extends HookConsumerWidget {
  final String id;
  const ModelRegistryView({super.key, required this.id});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final formKey = useMemoized(() => GlobalKey<FormState>());

    final initialJsonRef = useRef<String?>(null);

    // 1. Data and loading states are read from Riverpod!
    final formState = ref.watch(modelRegistryFormProvider(id));

    if (formState case AsyncData(value: final payload)) {
      initialJsonRef.value ??= jsonEncode(payload.toJson());
    }

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
        initialJsonRef.value,
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
    String? initialJson,
  ) {
    final initialConfigJson = initialJson ?? jsonEncode(payload.toJson());

    Future<bool> handlePop() async {
      FocusScope.of(context).unfocus();
      final latestPayload =
          ref.read(modelRegistryFormProvider(id)).value ?? payload;
      final isDirty = jsonEncode(latestPayload.toJson()) != initialConfigJson;
      if (!isDirty) return true;

      final shouldDiscard = await showDialog<bool>(
        context: context,
        builder: (ctx) => AlertDialog(
          title: Text(l10n.modelRegistryDiscardTitle),
          content: Text(l10n.modelRegistryDiscardMessage),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(ctx, false),
              child: Text(l10n.modelRegistryKeepEditingBtn),
            ),
            FilledButton(
              style: FilledButton.styleFrom(
                backgroundColor: Theme.of(context).colorScheme.error,
              ),
              onPressed: () => Navigator.pop(ctx, true),
              child: Text(l10n.modelRegistryDiscardBtn),
            ),
          ],
        ),
      );
      return shouldDiscard == true;
    }

    Future<void> deleteRegistry() async {
      final String idToDelete = payload.id;
      if (idToDelete.isEmpty) return;

      final nameToDisplay = payload.name.isNotEmpty ? payload.name : payload.id;

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

    Future<void> triggerBack() async {
      final canLeave = await handlePop();
      if (canLeave && context.mounted) {
        if (context.canPop()) {
          context.pop();
        } else {
          context.go('/studio');
        }
      }
    }

    return PopScope(
      canPop: false,
      onPopInvokedWithResult: (didPop, result) async {
        if (didPop) return;
        await triggerBack();
      },
      child: Scaffold(
        appBar: AppBar(
          leading: IconButton(
            icon: const Icon(Icons.arrow_back),
            tooltip: MaterialLocalizations.of(context).backButtonTooltip,
            onPressed: triggerBack,
          ),
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
              icon: const Icon(Icons.copy),
              tooltip: l10n.modelRegistryCloneBtn,
              onPressed: formState.isLoading
                  ? null
                  : () async {
                      try {
                        final cloned = await ref
                            .read(modelRegistryControllerProvider.notifier)
                            .cloneConfig(id);
                        if (!context.mounted) return;
                        ModelRegistryEditRoute(id: cloned.id).go(context);
                      } catch (e) {
                        if (!context.mounted) return;
                        ref
                            .read(loggerServiceProvider)
                            .error(
                              'Studio',
                              'Failed to clone registry config: $e',
                              e,
                            );
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(
                            content: Text(
                              l10n.studioViewsFailedToClone(e.toString()),
                            ),
                            backgroundColor: Theme.of(
                              context,
                            ).colorScheme.error,
                          ),
                        );
                      }
                    },
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
        body: Align(
          alignment: Alignment.topCenter,
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 1200),
            child: Form(
              key: formKey,
              child: ListView(
                padding: AppSpacing.p16,
                children: [
                  _buildSystemAttributes(context, ref, l10n, payload),
                  AppSpacing.h24,
                  _buildTierCardsSection(context, ref, l10n, payload),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildSystemAttributes(
    BuildContext context,
    WidgetRef ref,
    AppLocalizations l10n,
    ModelConfig data,
  ) {
    return Card(
      child: Padding(
        padding: AppSpacing.p16,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              l10n.systemMetaTitle,
              style: Theme.of(
                context,
              ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w600),
            ),
            AppSpacing.h16,
            TextFormField(
              initialValue: data.id,
              decoration: InputDecoration(labelText: l10n.configIdLabel),
              readOnly: true, // Server-side Minting: ID is immutable
            ),
            AppSpacing.h12,
            TextFormField(
              key: const ValueKey('model_registry_name_field'),
              initialValue: data.name,
              decoration: InputDecoration(
                labelText: l10n.modelRegistryNameLabel,
                border: const OutlineInputBorder(),
              ),
              onChanged: (val) {
                ref
                    .read(modelRegistryFormProvider(id).notifier)
                    .forceRebuild(data.copyWith(name: val.trim()));
              },
            ),
            AppSpacing.h12,
            DropdownButtonFormField<String>(
              key: const ValueKey('model_registry_default_provider_field'),
              initialValue: data.defaultProvider,
              isExpanded: true,
              decoration: InputDecoration(
                labelText: l10n.modelRegistryDefaultProviderLabel,
                border: const OutlineInputBorder(),
              ),
              items: [
                DropdownMenuItem(
                  value: 'vertex_ai',
                  child: Text(
                    l10n.platformVertexAi,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                DropdownMenuItem(
                  value: 'ai_studio',
                  child: Text(
                    l10n.platformAiStudio,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                DropdownMenuItem(
                  value: 'openai',
                  child: Text(
                    l10n.platformOpenAi,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                DropdownMenuItem(
                  value: 'anthropic',
                  child: Text(
                    l10n.platformAnthropic,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
              onChanged: (val) {
                if (val != null) {
                  final updatedTiers = <String, LlmModelConfig>{};
                  for (final entry in data.tierDefinitions.entries) {
                    updatedTiers[entry.key] = entry.value.copyWith(
                      provider: val,
                    );
                  }
                  ref
                      .read(modelRegistryFormProvider(id).notifier)
                      .forceRebuild(
                        data.copyWith(
                          defaultProvider: val,
                          tierDefinitions: updatedTiers,
                        ),
                      );
                }
              },
            ),
            if (data.defaultProvider == 'vertex_ai') ...[
              AppSpacing.h12,
              _buildLocationDropdown(context, ref, l10n, data),
            ],
            AppSpacing.h12,
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

  Widget _buildLocationDropdown(
    BuildContext context,
    WidgetRef ref,
    AppLocalizations l10n,
    ModelConfig data,
  ) {
    final firstTier = data.tierDefinitions.values.firstOrNull;
    final currentLocation =
        (firstTier?.additionalParams['vertex_location'] as String?)
                ?.isNotEmpty ==
            true
        ? firstTier!.additionalParams['vertex_location'] as String
        : 'europe-north1';

    final supportedLocationsAsync = ref.watch(supportedLocationsProvider);
    final locations = supportedLocationsAsync.value ?? [];

    return DropdownButtonFormField<String>(
      key: const ValueKey('model_registry_location_field'),
      initialValue: currentLocation,
      isExpanded: true,
      decoration: InputDecoration(
        labelText: l10n.locationLabel,
        border: const OutlineInputBorder(),
        suffixIcon: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            if (supportedLocationsAsync.isLoading)
              const Padding(
                padding: EdgeInsets.symmetric(horizontal: AppSpacing.s8),
                child: SizedBox(
                  width: AppSpacing.s16,
                  height: AppSpacing.s16,
                  child: CircularProgressIndicator(strokeWidth: 2),
                ),
              ),
            if (supportedLocationsAsync.hasError)
              Tooltip(
                message: l10n.discoveryErrorTooltip,
                child: Padding(
                  padding: const EdgeInsets.symmetric(
                    horizontal: AppSpacing.s8,
                  ),
                  child: Icon(
                    Icons.warning_amber_rounded,
                    color: context.semanticColors.warning,
                    size: 20,
                  ),
                ),
              ),
            IconButton(
              icon: const Icon(Icons.refresh, size: 20),
              tooltip: l10n.refreshLocationsTooltip,
              onPressed: () => ref.invalidate(supportedLocationsProvider),
            ),
          ],
        ),
      ),
      items: [
        if (currentLocation.isNotEmpty &&
            !locations.any((GcpLocation loc) => loc.id == currentLocation))
          DropdownMenuItem(
            value: currentLocation,
            child: Text(currentLocation, overflow: TextOverflow.ellipsis),
          ),
        ...locations.map((GcpLocation loc) {
          return DropdownMenuItem(
            value: loc.id,
            child: Text(loc.label, overflow: TextOverflow.ellipsis),
          );
        }),
      ],
      onChanged: (val) {
        if (val != null) {
          final updatedTiers = <String, LlmModelConfig>{};
          for (final entry in data.tierDefinitions.entries) {
            final newParams = Map<String, Object?>.from(
              entry.value.additionalParams,
            );
            newParams['vertex_location'] = val;
            updatedTiers[entry.key] = entry.value.copyWith(
              additionalParams: newParams,
            );
          }
          ref
              .read(modelRegistryFormProvider(id).notifier)
              .forceRebuild(data.copyWith(tierDefinitions: updatedTiers));
        }
      },
    );
  }

  Widget _buildTierCardsSection(
    BuildContext context,
    WidgetRef ref,
    AppLocalizations l10n,
    ModelConfig payload,
  ) {
    final canonicalTiers = [
      ('fast', l10n.studioTierFast, Icons.bolt),
      ('balanced', l10n.studioTierBalanced, Icons.balance),
      ('deep', l10n.studioTierDeep, Icons.psychology),
      ('reasoning', l10n.studioTierReasoning, Icons.auto_awesome),
    ];

    void updateTier(String tierKey, LlmModelConfig updated) {
      final newTierDefs = Map<String, LlmModelConfig>.from(
        payload.tierDefinitions,
      );
      newTierDefs[tierKey] = updated;
      ref
          .read(modelRegistryFormProvider(id).notifier)
          .forceRebuild(payload.copyWith(tierDefinitions: newTierDefs));
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text(
          l10n.providerSettings,
          style: Theme.of(
            context,
          ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w600),
        ),
        AppSpacing.h16,
        ...canonicalTiers.map((tierTuple) {
          final tierKey = tierTuple.$1;
          final tierLabel = tierTuple.$2;
          final tierIcon = tierTuple.$3;
          final cfg =
              payload.tierDefinitions[tierKey] ??
              LlmModelConfig(
                provider: payload.defaultProvider,
                modelName: '',
                isActive: true,
              );

          final effectiveProvider = cfg.provider.isNotEmpty
              ? cfg.provider
              : payload.defaultProvider;
          final isReasoning = _isReasoningModel(cfg);
          final hasRegions = effectiveProvider == 'vertex_ai';
          final activeLocation = hasRegions
              ? ((cfg.additionalParams['vertex_location'] as String?)
                            ?.isNotEmpty ==
                        true
                    ? cfg.additionalParams['vertex_location'] as String
                    : 'europe-north1')
              : null;

          final modelsAsync = ref.watch(
            availableModelsProvider(
              platform: effectiveProvider,
              location: activeLocation,
            ),
          );
          final dynamicModels = modelsAsync.value ?? [];
          final currentModel = cfg.modelName;
          final modelItems = <String>{
            if (currentModel.isNotEmpty) currentModel,
            ...dynamicModels,
          }.toList();

          return Card(
            key: ValueKey('tier_card_$tierKey'),
            margin: const EdgeInsets.only(bottom: AppSpacing.s16),
            child: Padding(
              padding: AppSpacing.p16,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Expanded(
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Chip(
                              avatar: Icon(tierIcon, size: 16),
                              label: Text(
                                tierKey.toUpperCase(),
                                style: Theme.of(context).textTheme.labelMedium
                                    ?.copyWith(fontWeight: FontWeight.bold),
                              ),
                            ),
                            AppSpacing.w12,
                            Flexible(
                              child: Text(
                                tierLabel,
                                style: Theme.of(context).textTheme.titleMedium,
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                          ],
                        ),
                      ),
                      Switch(
                        value: cfg.isActive,
                        onChanged: (val) {
                          updateTier(tierKey, cfg.copyWith(isActive: val));
                        },
                      ),
                    ],
                  ),
                  const Divider(height: AppSpacing.s24),
                  DropdownButtonFormField<String>(
                    key: ValueKey('${tierKey}_model_name'),
                    initialValue: currentModel.isNotEmpty
                        ? currentModel
                        : modelItems.firstOrNull,
                    isExpanded: true,
                    decoration: InputDecoration(
                      labelText: l10n.modelNameLabel,
                      border: const OutlineInputBorder(),
                      isDense: true,
                      suffixIcon: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          if (modelsAsync.isLoading)
                            const Padding(
                              padding: EdgeInsets.symmetric(
                                horizontal: AppSpacing.s8,
                              ),
                              child: SizedBox(
                                width: AppSpacing.s16,
                                height: AppSpacing.s16,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                ),
                              ),
                            ),
                          if (modelsAsync.hasError)
                            Tooltip(
                              message: l10n.discoveryErrorTooltip,
                              child: Padding(
                                padding: const EdgeInsets.symmetric(
                                  horizontal: AppSpacing.s8,
                                ),
                                child: Icon(
                                  Icons.warning_amber_rounded,
                                  color: context.semanticColors.warning,
                                  size: 18,
                                ),
                              ),
                            ),
                          IconButton(
                            icon: const Icon(Icons.refresh, size: 18),
                            tooltip: l10n.refreshModelsTooltip,
                            onPressed: () => ref.invalidate(
                              availableModelsProvider(
                                platform: effectiveProvider,
                                location: activeLocation,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                    items: modelItems.map((model) {
                      return DropdownMenuItem<String>(
                        value: model,
                        child: Text(model, overflow: TextOverflow.ellipsis),
                      );
                    }).toList(),
                    onChanged: (val) {
                      if (val != null) {
                        updateTier(tierKey, cfg.copyWith(modelName: val));
                      }
                    },
                  ),
                  if (isReasoning) ...[
                    AppSpacing.h12,
                    Container(
                      padding: AppSpacing.p12,
                      decoration: BoxDecoration(
                        color: Theme.of(
                          context,
                        ).colorScheme.primaryContainer.withValues(alpha: 0.3),
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(
                          color: Theme.of(
                            context,
                          ).colorScheme.primary.withValues(alpha: 0.5),
                        ),
                      ),
                      child: Row(
                        children: [
                          Icon(
                            Icons.psychology,
                            color: Theme.of(context).colorScheme.primary,
                            size: 20,
                          ),
                          AppSpacing.w8,
                          Expanded(
                            child: Text(
                              l10n.reasoningModelNotice,
                              style: Theme.of(context).textTheme.bodySmall
                                  ?.copyWith(
                                    color: Theme.of(
                                      context,
                                    ).colorScheme.primary,
                                    fontWeight: FontWeight.w500,
                                  ),
                            ),
                          ),
                        ],
                      ),
                    ),
                    AppSpacing.h12,
                    Row(
                      children: [
                        Expanded(
                          child: _buildIntField(
                            ValueKey('${tierKey}_thinking_budget'),
                            cfg.thinkingBudgetTokens,
                            l10n.thinkingBudgetTokensLabel,
                            l10n,
                            (val) => updateTier(
                              tierKey,
                              cfg.copyWith(thinkingBudgetTokens: val),
                            ),
                            helperText: l10n.thinkingBudgetHelper,
                          ),
                        ),
                        AppSpacing.w12,
                        Expanded(
                          child: DropdownButtonFormField<String?>(
                            initialValue: cfg.reasoningEffort,
                            isExpanded: true,
                            decoration: InputDecoration(
                              labelText: l10n.lblReasoning,
                              border: const OutlineInputBorder(),
                              isDense: true,
                            ),
                            items: [
                              DropdownMenuItem(
                                value: null,
                                child: Text(
                                  l10n.mcpToolParamsUseDefaultOption,
                                  overflow: TextOverflow.ellipsis,
                                ),
                              ),
                              DropdownMenuItem(
                                value: 'low',
                                child: Text(
                                  l10n.stratLow,
                                  overflow: TextOverflow.ellipsis,
                                ),
                              ),
                              DropdownMenuItem(
                                value: 'medium',
                                child: Text(
                                  l10n.stratMedium,
                                  overflow: TextOverflow.ellipsis,
                                ),
                              ),
                              DropdownMenuItem(
                                value: 'high',
                                child: Text(
                                  l10n.stratHigh,
                                  overflow: TextOverflow.ellipsis,
                                ),
                              ),
                            ],
                            onChanged: (val) {
                              updateTier(tierKey, cfg.withReasoningEffort(val));
                            },
                          ),
                        ),
                      ],
                    ),
                  ],
                  if (!isReasoning) ...[
                    AppSpacing.h12,
                    Row(
                      children: [
                        Expanded(
                          child: _buildDoubleField(
                            ValueKey('${tierKey}_temp'),
                            cfg.temperature,
                            l10n.temperatureLabel,
                            l10n,
                            (val) => updateTier(
                              tierKey,
                              cfg.copyWith(temperature: val),
                            ),
                          ),
                        ),
                        AppSpacing.w12,
                        Expanded(
                          child: _buildDoubleField(
                            ValueKey('${tierKey}_topP'),
                            cfg.topP,
                            l10n.topPLabel,
                            l10n,
                            (val) =>
                                updateTier(tierKey, cfg.copyWith(topP: val)),
                          ),
                        ),
                      ],
                    ),
                    AppSpacing.h12,
                    Row(
                      children: [
                        Expanded(
                          child: _buildIntField(
                            ValueKey('${tierKey}_topK'),
                            cfg.topK,
                            l10n.topKLabel,
                            l10n,
                            (val) =>
                                updateTier(tierKey, cfg.copyWith(topK: val)),
                          ),
                        ),
                        AppSpacing.w12,
                        Expanded(
                          child: _buildDoubleField(
                            ValueKey('${tierKey}_freq_penalty'),
                            cfg.frequencyPenalty,
                            l10n.frequencyPenaltyLabel,
                            l10n,
                            (val) => updateTier(
                              tierKey,
                              cfg.copyWith(frequencyPenalty: val),
                            ),
                          ),
                        ),
                        AppSpacing.w12,
                        Expanded(
                          child: _buildDoubleField(
                            ValueKey('${tierKey}_pres_penalty'),
                            cfg.presencePenalty,
                            l10n.presencePenaltyLabel,
                            l10n,
                            (val) => updateTier(
                              tierKey,
                              cfg.copyWith(presencePenalty: val),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ],
                  AppSpacing.h12,
                  Row(
                    children: [
                      Expanded(
                        child: _buildIntField(
                          ValueKey('${tierKey}_max_tokens'),
                          cfg.maxTokens,
                          l10n.maxTokensLabel,
                          l10n,
                          (val) =>
                              updateTier(tierKey, cfg.copyWith(maxTokens: val)),
                        ),
                      ),
                      AppSpacing.w12,
                      Expanded(
                        child: DropdownButtonFormField<String>(
                          initialValue: cfg.parsingMode,
                          isExpanded: true,
                          decoration: InputDecoration(
                            labelText: l10n.parsingModeLabel,
                            border: const OutlineInputBorder(),
                            isDense: true,
                          ),
                          items: [
                            DropdownMenuItem(
                              value: 'AUTO',
                              child: Text(
                                l10n.presetAutomatic,
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                            DropdownMenuItem(
                              value: 'NONE',
                              child: Text(
                                l10n.studioViewsNone,
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                            DropdownMenuItem(
                              value: 'STRUCTURED_JSON',
                              child: Text(
                                l10n.workflowTypeJson,
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                          ],
                          onChanged: (val) {
                            if (val != null) {
                              updateTier(
                                tierKey,
                                cfg.copyWith(parsingMode: val),
                              );
                            }
                          },
                        ),
                      ),
                    ],
                  ),
                  _buildBoolField(
                    cfg.supportsGrounding,
                    l10n.supportsGroundingLabel,
                    (val) => updateTier(
                      tierKey,
                      cfg.copyWith(supportsGrounding: val),
                    ),
                  ),
                ],
              ),
            ),
          );
        }),
      ],
    );
  }

  Widget _buildDoubleField(
    Key? key,
    double? initialValue,
    String label,
    AppLocalizations l10n,
    ValueChanged<double> onChanged, {
    String? helperText,
  }) {
    return Padding(
      padding: const EdgeInsets.only(bottom: AppSpacing.s12),
      child: TextFormField(
        key: key,
        initialValue: initialValue?.toString() ?? '',
        keyboardType: const TextInputType.numberWithOptions(decimal: true),
        decoration: InputDecoration(
          labelText: label,
          helperText: helperText,
          border: const OutlineInputBorder(),
          isDense: true,
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
    Key? key,
    int? initialValue,
    String label,
    AppLocalizations l10n,
    ValueChanged<int> onChanged, {
    String? helperText,
  }) {
    return Padding(
      padding: const EdgeInsets.only(bottom: AppSpacing.s12),
      child: TextFormField(
        key: key,
        initialValue: initialValue?.toString() ?? '',
        keyboardType: TextInputType.number,
        decoration: InputDecoration(
          labelText: label,
          helperText: helperText,
          border: const OutlineInputBorder(),
          isDense: true,
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
    ValueChanged<bool> onChanged,
  ) {
    return Padding(
      padding: const EdgeInsets.only(bottom: AppSpacing.s8),
      child: SwitchListTile(
        title: Text(label),
        value: initialValue,
        onChanged: onChanged,
        contentPadding: EdgeInsets.zero,
      ),
    );
  }

  bool _isReasoningModel(LlmModelConfig cfg) {
    final name = cfg.modelName.toLowerCase();
    return name.contains('gemini-3') ||
        name.contains('claude-3-7') ||
        name.contains('claude-3.7') ||
        name.contains('o1') ||
        name.contains('o3') ||
        name.contains('o4') ||
        (cfg.thinkingBudgetTokens ?? 0) > 0;
  }
}
