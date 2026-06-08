import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:client_app/core/state/mutation.dart';
import 'package:client_app/features/studio/controllers/studio_controller.dart';
import 'package:client_app/features/studio/controllers/prompt_blocks_controller.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/features/studio/controllers/mcp_gateways_controller.dart';
import 'package:client_app/features/studio/controllers/model_registry_controller.dart';
import 'package:client_app/features/studio/models/model_config.dart';
import 'package:client_app/features/studio/views/widgets/i18n_text_field.dart';
import 'package:client_app/core/error/app_error_boundary.dart';
import 'package:client_app/core/error/app_error_ext.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/shared/models/i18n_text.dart';

class StepBuilderView extends HookConsumerWidget {
  final dynamic step;

  const StepBuilderView({super.key, required this.step});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    String stepId = 'new';
    if (step is NodeStrategy) {
      stepId = (step as NodeStrategy).id.isNotEmpty
          ? (step as NodeStrategy).id
          : 'new';
    } else if (step is Map) {
      final idStr = step['id']?.toString() ?? '';
      stepId = idStr.isNotEmpty ? idStr : 'new';
    }

    final formState = ref.watch(stepFormProvider(stepId));
    final promptBlocksAsync = ref.watch(promptBlocksControllerProvider);
    final mcpGatewaysAsync = ref.watch(mcpGatewaysControllerProvider);

    return formState.when(
      loading: () => Scaffold(
        appBar: AppBar(title: Text(l10n.stepEditTitle)),
        body: const Center(child: CircularProgressIndicator()),
      ),
      error: (e, st) => Scaffold(
        appBar: AppBar(title: Text(l10n.stepEditTitle)),
        body: ErrorView(
          error: e,
          stackTrace: st,
          compact: false,
          onRetry: () => ref.invalidate(stepFormProvider(stepId)),
        ),
      ),
      data: (payload) {
        // Absolute Fail-Fast for dependencies
        if (promptBlocksAsync.hasError) throw promptBlocksAsync.error!;
        if (mcpGatewaysAsync.hasError) throw mcpGatewaysAsync.error!;
        if (!promptBlocksAsync.hasValue || !mcpGatewaysAsync.hasValue) {
          return const Scaffold(
            body: Center(child: CircularProgressIndicator()),
          );
        }

        return _buildScaffold(
          context,
          ref,
          l10n,
          formState,
          payload,
          stepId,
          promptBlocksAsync.value!,
          mcpGatewaysAsync.value!,
        );
      },
    );
  }

  void _addCriteriaBlock(WidgetRef ref, NodeStrategy payload, String blockId) {
    if (payload is NodeStrategyLlm) {
      final blocks = List<String>.from(payload.criteriaBlockIds);
      blocks.add('');
      ref
          .read(stepFormProvider(blockId).notifier)
          .forceRebuild(payload.copyWith(criteriaBlockIds: blocks));
    }
  }

  void _addPreHook(WidgetRef ref, NodeStrategy payload, String blockId) {
    final hooks = List<String>.from(payload.preHooks);
    hooks.add('');
    ref
        .read(stepFormProvider(blockId).notifier)
        .forceRebuild(payload.copyWith(preHooks: hooks));
  }

  void _addPostHook(WidgetRef ref, NodeStrategy payload, String blockId) {
    final hooks = List<String>.from(payload.postHooks);
    hooks.add('');
    ref
        .read(stepFormProvider(blockId).notifier)
        .forceRebuild(payload.copyWith(postHooks: hooks));
  }

  void _deleteStep(
    BuildContext context,
    WidgetRef ref,
    AppLocalizations l10n,
    NodeStrategy payload,
    MutationState<void> deleteMut,
  ) {
    final id = payload.id;
    final trans = payload.name.translations;
    final nameToDisplay = trans['fi'] ?? trans['en'] ?? id;

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(l10n.stepDeleteConfirmTitle),
        content: Text(l10n.stepDeleteConfirmMessage(nameToDisplay)),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: Text(l10n.cancel),
          ),
          MutationButton<void>(
            mutation: deleteMut,
            label: l10n.delete,
            action: () async {
              await ref.read(stepsControllerProvider.notifier).deleteStep(id);
              if (ctx.mounted) Navigator.pop(ctx);
            },
          ),
        ],
      ),
    );
  }

  Widget _buildScaffold(
    BuildContext context,
    WidgetRef ref,
    AppLocalizations l10n,
    AsyncValue<NodeStrategy> formState,
    NodeStrategy payload,
    String stepId,
    List<PromptBlock> promptBlocks,
    List<Map<String, dynamic>> mcpGateways,
  ) {
    final validateMutation = useMutation<Map<String, dynamic>>(
      onSuccess: (data) {
        if (context.mounted) {
          final rendered = data['rendered_prompt']?.toString();
          if (rendered == null) {
            throw AppException.validation(l10n.simulatorCorruptionError);
          }
          showDialog(
            context: context,
            builder: (ctx) => AlertDialog(
              title: Text(l10n.simulatorOutputTitle),
              content: SizedBox(
                width: double.maxFinite,
                child: SingleChildScrollView(
                  child: Text(
                    rendered,
                    style: const TextStyle(fontFamily: 'monospace'),
                  ),
                ),
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(ctx),
                  child: Text(l10n.closeModalBtn),
                ),
              ],
            ),
          );
        }
      },
      onError: (e) {
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(l10n.simulatorFailedError(e.toString())),
              backgroundColor: Theme.of(context).colorScheme.error,
            ),
          );
        }
      },
    );

    final deleteMutation = useMutation<void>(
      onSuccess: (_) {
        if (context.mounted) {
          ScaffoldMessenger.of(
            context,
          ).showSnackBar(SnackBar(content: Text(l10n.studioSaveSuccess)));
          context.pop();
        }
      },
      onError: (e) {
        if (context.mounted) {
          final errorMsg = AppExceptionX.extractLocalizedHint(e, l10n);
          ref
              .read(loggerServiceProvider)
              .error('Studio', 'Failed to delete step: $e', e);
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(errorMsg),
              backgroundColor: Theme.of(context).colorScheme.error,
            ),
          );
        }
      },
    );

    Future<void> saveStep() async {
      final id = payload.id.trim();
      if (id.isEmpty) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(l10n.idRequiredError),
            backgroundColor: Theme.of(context).colorScheme.error,
          ),
        );
        return;
      }

      if (payload is NodeStrategyLlm) {
        final strategy = payload.modelStrategy ?? '';
        if (strategy.isEmpty) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: const Text(
                'Model Strategy (Tekoälymalli) on pakollinen LLM-askelille.',
              ),
              backgroundColor: Theme.of(context).colorScheme.error,
            ),
          );
          return;
        }
      }

      try {
        await ref.read(stepFormProvider(stepId).notifier).submit(payload);
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(l10n.stepSavedSuccess),
              backgroundColor: const Color(0xFF2E7D32),
            ),
          );
          context.pop();
        }
      } catch (e) {
        if (context.mounted) {
          final errorMsg = e is AppException
              ? AppExceptionX.extractLocalizedHint(e, l10n)
              : e.toString();
          ref
              .read(loggerServiceProvider)
              .error('Studio', 'Failed to save step: $e', e);
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(errorMsg),
              backgroundColor: Theme.of(context).colorScheme.error,
            ),
          );
        }
      }
    }

    return AppExceptionBoundary(
      child: Scaffold(
        appBar: AppBar(
          leading: IconButton(
            icon: const Icon(Icons.arrow_back),
            tooltip: 'Back to Studio',
            onPressed: () => context.go('/admin'),
          ),
          title: Text(l10n.stepEditTitle),
          actions: [
            if (payload.id.isNotEmpty)
              IconButton(
                onPressed: () =>
                    _deleteStep(context, ref, l10n, payload, deleteMutation),
                icon: Icon(
                  Icons.delete,
                  color: Theme.of(context).colorScheme.error,
                ),
                tooltip: l10n.delete,
              ),
            IconButton(
              onPressed: validateMutation.isLoading
                  ? null
                  : () {
                      validateMutation.mutate(() async {
                        // Backend actually expects { 'step': {...rules}, 'mock_inputs': {} }
                        // but if simulateStep asks for NodeStrategy, we need to see its signature.
                        // Assuming simulateStep(Map<String, dynamic>)
                        // Let's pass the mapping directly if simulateStep was changed, or we just reconstruct the map.
                        // Since the error is "can't be assigned to the parameter type 'NodeStrategy'", simulateStep is defined as: simulateStep(NodeStrategy)
                        // If it wants NodeStrategy, we pass payload:
                        return await ref
                            .read(stepsControllerProvider.notifier)
                            .simulateStep(payload);
                      });
                    },
              icon: validateMutation.isLoading
                  ? const SizedBox(
                      width: 16,
                      height: 16,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : Icon(
                      Icons.bug_report,
                      color: Theme.of(context).colorScheme.primary,
                    ),
              tooltip: l10n.simulateStepTooltip,
            ),
            if (formState.isLoading)
              const Padding(
                padding: EdgeInsets.symmetric(horizontal: 16.0),
                child: Center(
                  child: SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  ),
                ),
              )
            else
              TextButton.icon(
                onPressed: saveStep,
                icon: const Icon(Icons.save),
                label: Text(l10n.studioSaveButton),
              ),
            const SizedBox(width: 16),
          ],
        ),
        body: SingleChildScrollView(
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Metadata
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          l10n.configurationTitle,
                          style: const TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 16),
                        TextFormField(
                          initialValue: payload.id,
                          decoration: InputDecoration(
                            labelText: l10n.stepIdLabel,
                            border: const OutlineInputBorder(),
                          ),
                          enabled: payload.id.isEmpty,
                          onChanged: (val) {
                            ref
                                .read(stepFormProvider(stepId).notifier)
                                .forceRebuild(payload.copyWith(id: val.trim()));
                          },
                        ),
                        const SizedBox(height: 16),
                        TextFormField(
                          initialValue: payload.slug,
                          decoration: InputDecoration(
                            labelText: l10n.slugLabel,
                            border: const OutlineInputBorder(),
                          ),
                          onChanged: (val) {
                            ref
                                .read(stepFormProvider(stepId).notifier)
                                .forceRebuild(
                                  payload.copyWith(slug: val.trim()),
                                );
                          },
                        ),
                        const SizedBox(height: 16),
                        I18nTextField(
                          label: l10n.nameLabel,
                          initialData: payload.name,
                          onChanged: (val) {
                            ref
                                .read(stepFormProvider(stepId).notifier)
                                .forceRebuild(payload.copyWith(name: val));
                          },
                        ),
                        const SizedBox(height: 16),
                        I18nTextField(
                          label: l10n.descriptionLabel,
                          initialData: payload.description ?? I18nText(),
                          onChanged: (val) {
                            ref
                                .read(stepFormProvider(stepId).notifier)
                                .forceRebuild(
                                  payload.copyWith(description: val),
                                );
                          },
                        ),
                        const SizedBox(height: 16),
                        if (payload is NodeStrategyLlm)
                          Builder(
                            builder: (context) {
                              final configsAsync = ref.watch(
                                modelRegistryControllerProvider,
                              );
                              if (configsAsync.isLoading) {
                                return const Center(
                                  child: CircularProgressIndicator(),
                                );
                              }
                              if (configsAsync.hasError) {
                                return ErrorView(
                                  error: configsAsync.error!,
                                  compact: true,
                                );
                              }

                              final configs = configsAsync.value ?? [];
                              final registryConfig = configs.firstWhere(
                                (c) => c.type == 'model_registry',
                                orElse: () =>
                                    const ModelConfig(id: '', slug: ''),
                              );

                              final modelKeys = registryConfig.models.keys
                                  .toList();

                              if (modelKeys.isEmpty) {
                                return Text(
                                  'Warning: No models found.',
                                  style: TextStyle(
                                    color: Theme.of(context).colorScheme.error,
                                  ),
                                );
                              }

                              final currentStrategy =
                                  payload.modelStrategy ?? '';
                              final safeValue =
                                  modelKeys.contains(currentStrategy)
                                  ? currentStrategy
                                  : null;

                              return DropdownButtonFormField<String>(
                                key: ValueKey(modelKeys.length),
                                isExpanded: true,
                                initialValue: safeValue,
                                decoration: const InputDecoration(
                                  labelText:
                                      'Model Strategy (Cost/Cognition Override)',
                                  border: OutlineInputBorder(),
                                  isDense: true,
                                ),
                                items: modelKeys.map((key) {
                                  final modelData = registryConfig.models[key];
                                  final label =
                                      modelData?.modelName != null &&
                                          modelData!.modelName.isNotEmpty
                                      ? '${key.toUpperCase()} (${modelData.modelName})'
                                      : key.toUpperCase();
                                  return DropdownMenuItem(
                                    value: key,
                                    child: Text(label),
                                  );
                                }).toList(),
                                onChanged: (val) {
                                  if (val != null) {
                                    ref
                                        .read(stepFormProvider(stepId).notifier)
                                        .forceRebuild(
                                          payload.copyWith(modelStrategy: val),
                                        );
                                  }
                                },
                              );
                            },
                          ),
                      ],
                    ),
                  ),
                ),

                const SizedBox(height: 24),

                // allowed_mcp_tools
                Text(
                  l10n.mcpGatewaysTitle,
                  style: const TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 16),
                Wrap(
                  spacing: 8,
                  children: mcpGateways
                      .expand((gateway) {
                        final tools = gateway['tools'] as List<dynamic>? ?? [];
                        return tools;
                      })
                      .map((toolRaw) {
                        final toolData = toolRaw as Map<String, dynamic>;
                        final toolId = toolData['tool_id']?.toString() ?? '';
                        if (toolId.isEmpty) return const SizedBox.shrink();

                        final nameMap =
                            toolData['name'] as Map<String, dynamic>? ?? {};
                        final translations =
                            nameMap['translations'] as Map<String, dynamic>? ??
                            {};

                        // Current locale via Localizations or simple fallback
                        final currentLocale = Localizations.localeOf(
                          context,
                        ).languageCode;
                        final labelText =
                            translations[currentLocale] ??
                            translations['fi'] ??
                            translations['en'] ??
                            toolId;

                        final allowedMcpTools = List<String>.from(
                          payload.allowedMcpTools,
                        );
                        final isSelected = allowedMcpTools.contains(toolId);

                        return FilterChip(
                          label: Text(labelText),
                          selected: isSelected,
                          onSelected: (bool selected) {
                            if (selected) {
                              if (!allowedMcpTools.contains(toolId)) {
                                allowedMcpTools.add(toolId);
                              }
                            } else {
                              allowedMcpTools.remove(toolId);
                            }
                            ref
                                .read(stepFormProvider(stepId).notifier)
                                .forceRebuild(
                                  payload.copyWith(
                                    allowedMcpTools: allowedMcpTools,
                                  ),
                                );
                          },
                        );
                      })
                      .toList(),
                ),

                const SizedBox(height: 24),

                // pre_hooks
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      l10n.preHooksTitle,
                      style: const TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    OutlinedButton.icon(
                      onPressed: () => _addPreHook(ref, payload, stepId),
                      icon: const Icon(Icons.add),
                      label: Text(l10n.addHookBtn),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                ReorderableListView.builder(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  itemCount: payload.preHooks.length,
                  onReorder: (oldIndex, newIndex) {
                    if (oldIndex < newIndex) newIndex -= 1;
                    final hooks = List<String>.from(payload.preHooks);
                    final item = hooks.removeAt(oldIndex);
                    hooks.insert(newIndex, item);
                    ref
                        .read(stepFormProvider(stepId).notifier)
                        .forceRebuild(payload.copyWith(preHooks: hooks));
                  },
                  itemBuilder: (context, index) {
                    final hooks = payload.preHooks;
                    return _buildPreHookCard(
                      ref,
                      l10n,
                      payload,
                      stepId,
                      ValueKey('hook_$index\_${hooks[index]}'),
                      index,
                      hooks[index],
                    );
                  },
                ),
                const SizedBox(height: 24),

                // post_hooks
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      l10n.postHooksTitle,
                      style: const TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    OutlinedButton.icon(
                      onPressed: () => _addPostHook(ref, payload, stepId),
                      icon: const Icon(Icons.add),
                      label: Text(l10n.addHookBtn),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                ReorderableListView.builder(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  itemCount: payload.postHooks.length,
                  onReorder: (oldIndex, newIndex) {
                    if (oldIndex < newIndex) newIndex -= 1;
                    final hooks = List<String>.from(payload.postHooks);
                    final item = hooks.removeAt(oldIndex);
                    hooks.insert(newIndex, item);
                    ref
                        .read(stepFormProvider(stepId).notifier)
                        .forceRebuild(payload.copyWith(postHooks: hooks));
                  },
                  itemBuilder: (context, index) {
                    final hooks = payload.postHooks;
                    return _buildPostHookCard(
                      ref,
                      l10n,
                      payload,
                      stepId,
                      ValueKey('post_hook_$index\_${hooks[index]}'),
                      index,
                      hooks[index],
                    );
                  },
                ),

                const SizedBox(height: 24),

                if (payload is NodeStrategyLlm) ...[
                  // 2. Extraction Protocol Dropdown
                  const SizedBox(height: 24),
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            l10n.protocolBlockLabel,
                            style: const TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            l10n.protocolBlockDescription,
                            style: TextStyle(
                              fontSize: 13,
                              color: Theme.of(
                                context,
                              ).colorScheme.onSurfaceVariant,
                            ),
                          ),
                          const SizedBox(height: 12),
                          DropdownButtonFormField<String>(
                            isExpanded: true,
                            decoration: const InputDecoration(
                              border: OutlineInputBorder(),
                              isDense: true,
                            ),
                            initialValue:
                                promptBlocks.any(
                                  (m) =>
                                      m.id ==
                                          payload.extractionProtocolBlockId &&
                                      PromptBlockCategoryGroups
                                          .protocolCategories
                                          .contains(m.categoryId),
                                )
                                ? payload.extractionProtocolBlockId
                                : null,
                            items: [
                              DropdownMenuItem<String>(
                                value: null,
                                child: Text(l10n.noneDefaultLabel),
                              ),
                              ...promptBlocks
                                  .where(
                                    (m) => PromptBlockCategoryGroups
                                        .protocolCategories
                                        .contains(m.categoryId),
                                  )
                                  .map((m) {
                                    final currentLocale =
                                        Localizations.localeOf(
                                          context,
                                        ).languageCode;
                                    final rawLabel =
                                        m.label.translations[currentLocale] ??
                                        m.label.translations['en'] ??
                                        m.id;
                                    return DropdownMenuItem(
                                      value: m.id,
                                      child: Text(
                                        '$rawLabel (${m.id})',
                                        maxLines: 1,
                                        overflow: TextOverflow.ellipsis,
                                      ),
                                    );
                                  }),
                            ],
                            onChanged: (val) {
                              ref
                                  .read(stepFormProvider(stepId).notifier)
                                  .forceRebuild(
                                    payload.copyWith(
                                      extractionProtocolBlockId: val,
                                    ),
                                  );
                            },
                          ),
                        ],
                      ),
                    ),
                  ),

                  // 3. Execution Persona Protocol Dropdown
                  const SizedBox(height: 24),
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            l10n.executionPersonaTitle,
                            style: const TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            l10n.executionPersonaDescription,
                            style: TextStyle(
                              fontSize: 13,
                              color: Theme.of(
                                context,
                              ).colorScheme.onSurfaceVariant,
                            ),
                          ),
                          const SizedBox(height: 12),
                          DropdownButtonFormField<String>(
                            isExpanded: true,
                            decoration: const InputDecoration(
                              border: OutlineInputBorder(),
                              isDense: true,
                            ),
                            initialValue:
                                promptBlocks.any(
                                  (m) =>
                                      m.id == payload.executionPersonaBlockId &&
                                      PromptBlockCategoryGroups
                                          .personaCategories
                                          .contains(m.categoryId),
                                )
                                ? payload.executionPersonaBlockId
                                : null,
                            items: [
                              DropdownMenuItem<String>(
                                value: null,
                                child: Text(l10n.noneDefaultLabel),
                              ),
                              ...promptBlocks
                                  .where(
                                    (m) => PromptBlockCategoryGroups
                                        .personaCategories
                                        .contains(m.categoryId),
                                  )
                                  .map((m) {
                                    final currentLocale =
                                        Localizations.localeOf(
                                          context,
                                        ).languageCode;
                                    final rawLabel =
                                        m.label.translations[currentLocale] ??
                                        m.label.translations['en'] ??
                                        m.id;
                                    return DropdownMenuItem(
                                      value: m.id,
                                      child: Text(
                                        '$rawLabel (${m.id})',
                                        maxLines: 1,
                                        overflow: TextOverflow.ellipsis,
                                      ),
                                    );
                                  }),
                            ],
                            onChanged: (val) {
                              ref
                                  .read(stepFormProvider(stepId).notifier)
                                  .forceRebuild(
                                    payload.copyWith(
                                      executionPersonaBlockId: val,
                                    ),
                                  );
                            },
                          ),
                        ],
                      ),
                    ),
                  ),

                  // 4. Criteria Blocks List (Reorderable)
                  const SizedBox(height: 24),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              l10n.criteriaBlocksTitle,
                              style: const TextStyle(
                                fontSize: 20,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              l10n.criteriaBlocksDescription,
                              style: TextStyle(
                                fontSize: 13,
                                color: Theme.of(
                                  context,
                                ).colorScheme.onSurfaceVariant,
                              ),
                            ),
                          ],
                        ),
                      ),
                      OutlinedButton.icon(
                        onPressed: () =>
                            _addCriteriaBlock(ref, payload, stepId),
                        icon: const Icon(Icons.add),
                        label: Text(l10n.addPromptBlockBtn),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  ReorderableListView.builder(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    itemCount: payload.criteriaBlockIds.length,
                    onReorder: (oldIndex, newIndex) {
                      if (oldIndex < newIndex) newIndex -= 1;
                      final blocks = List<String>.from(
                        payload.criteriaBlockIds,
                      );
                      final item = blocks.removeAt(oldIndex);
                      blocks.insert(newIndex, item);
                      ref
                          .read(stepFormProvider(stepId).notifier)
                          .forceRebuild(
                            payload.copyWith(criteriaBlockIds: blocks),
                          );
                    },
                    itemBuilder: (context, index) {
                      final blocks = payload.criteriaBlockIds;
                      return _buildCriteriaBlockCard(
                        context,
                        ref,
                        l10n,
                        payload,
                        stepId,
                        ValueKey('criteria_block_$index\_${blocks[index]}'),
                        index,
                        blocks[index],
                        promptBlocks,
                      );
                    },
                  ),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildPreHookCard(
    WidgetRef ref,
    AppLocalizations l10n,
    NodeStrategy payload,
    String stepId,
    Key key,
    int index,
    String hookDef,
  ) {
    final knownHooks = [
      'search_hook',
      'memory_hook',
      'validation_hook',
      'score_hook',
    ];
    final bool isCustom = hookDef.isNotEmpty && !knownHooks.contains(hookDef);

    return Card(
      key: key,
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Row(
          children: [
            const Padding(
              padding: EdgeInsets.only(right: 8.0),
              child: Icon(Icons.drag_indicator, color: Color(0xFF9E9E9E)),
            ),
            Expanded(
              child: DropdownButtonFormField<String>(
                isExpanded: true,
                decoration: InputDecoration(labelText: l10n.preHookEngineLabel),
                initialValue: hookDef.isEmpty ? null : hookDef,
                items: [
                  DropdownMenuItem(
                    value: 'search_hook',
                    child: Text(l10n.hookTavily),
                  ),
                  DropdownMenuItem(
                    value: 'memory_hook',
                    child: Text(l10n.hookMemory),
                  ),
                  DropdownMenuItem(
                    value: 'validation_hook',
                    child: Text(l10n.hookValidation),
                  ),
                  DropdownMenuItem(
                    value: 'score_hook',
                    child: Text(l10n.hookScore),
                  ),
                  if (isCustom)
                    DropdownMenuItem(
                      value: hookDef,
                      child: Text(l10n.hookLegacy(hookDef)),
                    ),
                ],
                onChanged: (val) {
                  if (val != null) {
                    final hooks = List<String>.from(payload.preHooks);
                    hooks[index] = val;
                    ref
                        .read(stepFormProvider(stepId).notifier)
                        .forceRebuild(payload.copyWith(preHooks: hooks));
                  }
                },
              ),
            ),
            IconButton(
              icon: const Icon(Icons.delete, color: Color(0xFFD32F2F)),
              onPressed: () {
                final hooks = List<String>.from(payload.preHooks);
                hooks.removeAt(index);
                ref
                    .read(stepFormProvider(stepId).notifier)
                    .forceRebuild(payload.copyWith(preHooks: hooks));
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPostHookCard(
    WidgetRef ref,
    AppLocalizations l10n,
    NodeStrategy payload,
    String stepId,
    Key key,
    int index,
    String hookDef,
  ) {
    final knownHooks = [
      'search_hook',
      'memory_hook',
      'validation_hook',
      'score_hook',
      'waterfall_scoring_hook',
      'normalize_matrix_scores',
      'verify_citation_integrity',
      'enforce_hypothesis_linking',
    ];
    final bool isCustom = hookDef.isNotEmpty && !knownHooks.contains(hookDef);

    return Card(
      key: key,
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Row(
          children: [
            const Padding(
              padding: EdgeInsets.only(right: 8.0),
              child: Icon(Icons.drag_indicator, color: Color(0xFF9E9E9E)),
            ),
            Expanded(
              child: DropdownButtonFormField<String>(
                isExpanded: true,
                decoration: InputDecoration(
                  labelText: l10n.postHookEngineLabel,
                ),
                initialValue: hookDef.isEmpty ? null : hookDef,
                items: [
                  DropdownMenuItem(
                    value: 'waterfall_scoring_hook',
                    child: Text(l10n.hookWaterfall),
                  ),
                  DropdownMenuItem(
                    value: 'normalize_matrix_scores',
                    child: Text(l10n.hookNormalize),
                  ),
                  DropdownMenuItem(
                    value: 'search_hook',
                    child: Text(l10n.hookTavily),
                  ),
                  DropdownMenuItem(
                    value: 'memory_hook',
                    child: Text(l10n.hookMemory),
                  ),
                  DropdownMenuItem(
                    value: 'validation_hook',
                    child: Text(l10n.hookValidation),
                  ),
                  DropdownMenuItem(
                    value: 'score_hook',
                    child: Text(l10n.hookScore),
                  ),
                  DropdownMenuItem(
                    value: 'verify_citation_integrity',
                    child: Text(l10n.hookVerifyCitation),
                  ),
                  DropdownMenuItem(
                    value: 'enforce_hypothesis_linking',
                    child: Text(l10n.hookHypothesis),
                  ),
                  if (isCustom)
                    DropdownMenuItem(
                      value: hookDef,
                      child: Text(l10n.hookLegacy(hookDef)),
                    ),
                ],
                onChanged: (val) {
                  if (val != null) {
                    final hooks = List<String>.from(payload.postHooks);
                    hooks[index] = val;
                    ref
                        .read(stepFormProvider(stepId).notifier)
                        .forceRebuild(payload.copyWith(postHooks: hooks));
                  }
                },
              ),
            ),
            IconButton(
              icon: const Icon(Icons.delete, color: Color(0xFFD32F2F)),
              onPressed: () {
                final hooks = List<String>.from(payload.postHooks);
                hooks.removeAt(index);
                ref
                    .read(stepFormProvider(stepId).notifier)
                    .forceRebuild(payload.copyWith(postHooks: hooks));
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCriteriaBlockCard(
    BuildContext context,
    WidgetRef ref,
    AppLocalizations l10n,
    NodeStrategyLlm payload,
    String stepId,
    Key key,
    int index,
    String blockDef,
    List<PromptBlock> promptBlocks,
  ) {
    return Card(
      key: key,
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Row(
          children: [
            const Padding(
              padding: EdgeInsets.only(right: 8.0),
              child: Icon(Icons.drag_indicator, color: Color(0xFF9E9E9E)),
            ),
            Expanded(
              child: DropdownButtonFormField<String>(
                isExpanded: true,
                decoration: InputDecoration(labelText: l10n.promptBlockLabel),
                initialValue:
                    promptBlocks.any(
                      (m) =>
                          m.id == blockDef &&
                          PromptBlockCategoryGroups.criteriaCategories.contains(
                            m.categoryId,
                          ),
                    )
                    ? blockDef
                    : null,
                items: promptBlocks
                    .where(
                      (m) => PromptBlockCategoryGroups.criteriaCategories
                          .contains(m.categoryId),
                    )
                    .map((m) {
                      final currentLocale = Localizations.localeOf(
                        context,
                      ).languageCode;
                      final rawLabel =
                          m.label.translations[currentLocale] ??
                          m.label.translations['en'];

                      if (rawLabel == null || rawLabel.trim().isEmpty) {
                        throw AppException.validation(
                          'Fail-Fast: PromptBlock ${m.id} lacks required FI/EN translation.',
                        );
                      }

                      final displayText = '$rawLabel (${m.id})';
                      return DropdownMenuItem(
                        value: m.id,
                        child: Text(
                          displayText,
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      );
                    })
                    .toList(),
                onChanged: (val) {
                  if (val != null) {
                    final blocks = List<String>.from(payload.criteriaBlockIds);
                    blocks[index] = val;
                    ref
                        .read(stepFormProvider(stepId).notifier)
                        .forceRebuild(
                          payload.copyWith(criteriaBlockIds: blocks),
                        );
                  }
                },
              ),
            ),
            IconButton(
              icon: const Icon(Icons.delete, color: Color(0xFFD32F2F)),
              onPressed: () {
                final blocks = List<String>.from(payload.criteriaBlockIds);
                blocks.removeAt(index);
                ref
                    .read(stepFormProvider(stepId).notifier)
                    .forceRebuild(payload.copyWith(criteriaBlockIds: blocks));
              },
            ),
          ],
        ),
      ),
    );
  }
}
