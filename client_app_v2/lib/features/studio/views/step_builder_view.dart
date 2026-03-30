import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:client_app/core/state/mutation.dart';
import 'package:client_app/features/studio/controllers/studio_controller.dart';
import 'package:client_app/features/studio/controllers/prompt_blocks_controller.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';
import 'package:client_app/features/studio/controllers/mcp_gateways_controller.dart';
import 'package:client_app/features/studio/controllers/model_registry_controller.dart';
import 'package:client_app/features/studio/views/widgets/i18n_text_field.dart';
import 'package:client_app/utils/safe_cast.dart';
import 'package:client_app/core/error/app_error_boundary.dart';
import 'package:client_app/core/error/app_error_ext.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/core/error/app_exception.dart';

class StepBuilderView extends HookConsumerWidget {
  final Map<String, dynamic> step;

  const StepBuilderView({super.key, required this.step});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final stepId = (step['id']?.toString() ?? '').isEmpty
        ? 'new'
        : step['id'].toString();
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

  void _addPromptBlock(
    WidgetRef ref,
    Map<String, dynamic> payload,
    String blockId,
  ) {
    final blocks = SafeCast.safeList(payload['prompt_blocks']);
    blocks.add('');
    payload['prompt_blocks'] = blocks;
    ref.read(stepFormProvider(blockId).notifier).forceRebuild();
  }

  void _addPreHook(
    WidgetRef ref,
    Map<String, dynamic> payload,
    String blockId,
  ) {
    final hooks = SafeCast.safeList(payload['pre_hooks']);
    hooks.add('');
    payload['pre_hooks'] = hooks;
    ref.read(stepFormProvider(blockId).notifier).forceRebuild();
  }

  void _deleteStep(
    BuildContext context,
    WidgetRef ref,
    AppLocalizations l10n,
    Map<String, dynamic> payload,
    MutationState<void> deleteMut,
  ) {
    final id = payload['id']?.toString() ?? '';
    final labelMap = SafeCast.safeMap(payload['label']);
    final trans = SafeCast.safeMap(labelMap['translations']);
    final nameToDisplay = trans['fi']?.toString() ?? trans['en']?.toString() ?? id;

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
    AsyncValue<Map<String, dynamic>> formState,
    Map<String, dynamic> payload,
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
      final id = payload['id']?.toString().trim() ?? '';
      if (id.isEmpty) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(l10n.idRequiredError),
            backgroundColor: Theme.of(context).colorScheme.error,
          ),
        );
        return;
      }

      final stepType = SafeCast.safeString(payload['type'], 'llm');
      final strategy = SafeCast.safeString(payload['model_strategy']);
      if (stepType == 'llm' && strategy.isEmpty) {
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
            if (payload['id']?.toString().isNotEmpty == true)
              IconButton(
                onPressed: () => _deleteStep(
                  context,
                  ref,
                  l10n,
                  payload,
                  deleteMutation,
                ),
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
                        final simPayload = {
                          'step': payload,
                          'mock_inputs': <String, dynamic>{},
                        };
                        return await ref
                            .read(stepsControllerProvider.notifier)
                            .simulateStep(simPayload);
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
                          initialValue: SafeCast.safeString(payload['id']),
                          decoration: InputDecoration(
                            labelText: l10n.stepIdLabel,
                            border: const OutlineInputBorder(),
                          ),
                          enabled:
                              step['id'] == null ||
                              step['id'].toString().isEmpty,
                          onChanged: (val) => payload['id'] = val,
                        ),
                        const SizedBox(height: 16),
                        TextFormField(
                          initialValue: SafeCast.safeString(payload['slug']),
                          decoration: InputDecoration(
                            labelText: l10n.slugLabel,
                            border: const OutlineInputBorder(),
                          ),
                          onChanged: (val) => payload['slug'] = val,
                        ),
                        const SizedBox(height: 16),
                        I18nTextField(
                          label: l10n.nameLabel,
                          initialData: I18nText.fromJson(
                            SafeCast.safeMap(payload['label']),
                          ),
                          onChanged: (val) {
                            payload['label'] = val.toJson();
                            ref
                                .read(stepFormProvider(stepId).notifier)
                                .forceRebuild();
                          },
                        ),
                        const SizedBox(height: 16),
                        I18nTextField(
                          label: l10n.descriptionLabel,
                          initialData: I18nText.fromJson(
                            SafeCast.safeMap(payload['description']),
                          ),
                          onChanged: (val) {
                            payload['description'] = val.toJson();
                            ref
                                .read(stepFormProvider(stepId).notifier)
                                .forceRebuild();
                          },
                        ),
                        const SizedBox(height: 16),
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
                              (c) => c['type'] == 'model_registry',
                              orElse: () => <String, dynamic>{},
                            );

                            final modelsObj = SafeCast.safeMap(
                              registryConfig['models'],
                            );
                            final modelKeys = modelsObj.keys.toList();

                            if (modelKeys.isEmpty) {
                              return Text(
                                'Warning: No models found.',
                                style: TextStyle(
                                  color: Theme.of(context).colorScheme.error,
                                ),
                              );
                            }

                            final currentStrategy = SafeCast.safeString(
                              payload['model_strategy'],
                            );
                            final safeValue =
                                modelKeys.contains(currentStrategy)
                                ? currentStrategy
                                : null;

                            return DropdownButtonFormField<String>(
                              key: ValueKey(modelKeys.length),
                              initialValue: safeValue,
                              decoration: const InputDecoration(
                                labelText:
                                    'Model Strategy (Cost/Cognition Override)',
                                border: OutlineInputBorder(),
                                isDense: true,
                              ),
                              items: modelKeys.map((key) {
                                final modelData = SafeCast.safeMap(
                                  modelsObj[key],
                                );
                                final label = modelData['model_name'] != null
                                    ? '${key.toUpperCase()} (${modelData['model_name']})'
                                    : key.toUpperCase();
                                return DropdownMenuItem(
                                  value: key,
                                  child: Text(label),
                                );
                              }).toList(),
                              onChanged: (val) {
                                if (val != null) {
                                  payload['model_strategy'] = val;
                                  ref
                                      .read(stepFormProvider(stepId).notifier)
                                      .forceRebuild();
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
                  children: mcpGateways.map((toolMap) {
                    final slug = SafeCast.safeString(toolMap['slug']);
                    final allowedMcpTools = SafeCast.safeList(
                      payload['allowed_mcp_tools'],
                    ).map((e) => e.toString()).toList();
                    final isSelected = allowedMcpTools.contains(slug);
                    return FilterChip(
                      label: Text(slug),
                      selected: isSelected,
                      onSelected: (bool selected) {
                        if (selected) {
                          if (!allowedMcpTools.contains(slug)) {
                            allowedMcpTools.add(slug);
                          }
                        } else {
                          allowedMcpTools.remove(slug);
                        }
                        payload['allowed_mcp_tools'] = allowedMcpTools;
                        ref
                            .read(stepFormProvider(stepId).notifier)
                            .forceRebuild();
                      },
                    );
                  }).toList(),
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
                  itemCount: SafeCast.safeList(payload['pre_hooks']).length,
                  onReorder: (oldIndex, newIndex) {
                    if (oldIndex < newIndex) newIndex -= 1;
                    final hooks = SafeCast.safeList(payload['pre_hooks']);
                    final item = hooks.removeAt(oldIndex);
                    hooks.insert(newIndex, item);
                    payload['pre_hooks'] = hooks;
                    ref.read(stepFormProvider(stepId).notifier).forceRebuild();
                  },
                  itemBuilder: (context, index) {
                    final hooks = SafeCast.safeList(payload['pre_hooks']);
                    return _buildPreHookCard(
                      ref,
                      l10n,
                      payload,
                      stepId,
                      ValueKey('hook_$index\_${hooks[index]}'),
                      index,
                      hooks[index].toString(),
                    );
                  },
                ),

                const SizedBox(height: 24),

                // prompt_blocks
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      l10n.promptBlocksTitle,
                      style: const TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    OutlinedButton.icon(
                      onPressed: () => _addPromptBlock(ref, payload, stepId),
                      icon: const Icon(Icons.add),
                      label: Text(l10n.addPromptBlockBtn),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                ReorderableListView.builder(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  itemCount: SafeCast.safeList(payload['prompt_blocks']).length,
                  onReorder: (oldIndex, newIndex) {
                    if (oldIndex < newIndex) newIndex -= 1;
                    final blocks = SafeCast.safeList(payload['prompt_blocks']);
                    final item = blocks.removeAt(oldIndex);
                    blocks.insert(newIndex, item);
                    payload['prompt_blocks'] = blocks;
                    ref.read(stepFormProvider(stepId).notifier).forceRebuild();
                  },
                  itemBuilder: (context, index) {
                    final blocks = SafeCast.safeList(payload['prompt_blocks']);
                    return _buildPromptBlockCard(
                      ref,
                      l10n,
                      payload,
                      stepId,
                      ValueKey('block_$index\_${blocks[index]}'),
                      index,
                      blocks[index].toString(),
                      promptBlocks,
                    );
                  },
                ),
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
    Map<String, dynamic> payload,
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
              child: Icon(Icons.drag_indicator, color: const Color(0xFF9E9E9E)),
            ),
            Expanded(
              child: DropdownButtonFormField<String>(
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
                    final hooks = SafeCast.safeList(payload['pre_hooks']);
                    hooks[index] = val;
                    payload['pre_hooks'] = hooks;
                    ref.read(stepFormProvider(stepId).notifier).forceRebuild();
                  }
                },
              ),
            ),
            IconButton(
              icon: Icon(Icons.delete, color: const Color(0xFFD32F2F)),
              onPressed: () {
                SafeCast.safeList(payload['pre_hooks']).removeAt(index);
                ref.read(stepFormProvider(stepId).notifier).forceRebuild();
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPromptBlockCard(
    WidgetRef ref,
    AppLocalizations l10n,
    Map<String, dynamic> payload,
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
              child: Icon(Icons.drag_indicator, color: const Color(0xFF9E9E9E)),
            ),
            Expanded(
              child: DropdownButtonFormField<String>(
                decoration: InputDecoration(labelText: l10n.promptBlockLabel),
                initialValue: promptBlocks.any((m) => m.id == blockDef)
                    ? blockDef
                    : null,
                items: promptBlocks.map((m) {
                  return DropdownMenuItem(value: m.id, child: Text(m.id));
                }).toList(),
                onChanged: (val) {
                  final blocks = SafeCast.safeList(payload['prompt_blocks']);
                  blocks[index] = val;
                  payload['prompt_blocks'] = blocks;
                  ref.read(stepFormProvider(stepId).notifier).forceRebuild();
                },
              ),
            ),
            IconButton(
              icon: Icon(Icons.delete, color: const Color(0xFFD32F2F)),
              onPressed: () {
                SafeCast.safeList(payload['prompt_blocks']).removeAt(index);
                ref.read(stepFormProvider(stepId).notifier).forceRebuild();
              },
            ),
          ],
        ),
      ),
    );
  }
}
