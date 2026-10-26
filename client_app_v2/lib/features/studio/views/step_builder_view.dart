import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:go_router/go_router.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:client_app/core/state/mutation.dart';
import 'package:client_app/features/studio/controllers/studio_controller.dart';
import 'package:client_app/features/studio/controllers/prompt_blocks_controller.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/features/studio/controllers/mcp_gateways_controller.dart';
import 'package:client_app/features/studio/models/mcp_gateway.dart';
import 'package:client_app/features/studio/views/widgets/i18n_text_field.dart';
import 'package:client_app/features/studio/views/widgets/step_simulation_dialog.dart';
import 'package:client_app/features/studio/views/widgets/mcp_tool_params_panel.dart';
import 'package:client_app/core/error/app_error_boundary.dart';
import 'package:client_app/core/error/app_error_ext.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/core/models/enums.dart';

class StepBuilderView extends HookConsumerWidget {
  final String stepId;

  const StepBuilderView({super.key, required this.stepId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;

    final formState = ref.watch(stepFormProvider(stepId));
    final promptBlocksAsync = ref.watch(promptBlocksControllerProvider);
    final mcpGatewaysAsync = ref.watch(mcpGatewaysControllerProvider);

    final idFocusNode = useFocusNode();
    final slugController = useTextEditingController();
    final slugFocusNode = useFocusNode();
    final syncedStepId = useRef<String?>(null);

    final currentStep = switch (formState) {
      AsyncData(:final value) => value,
      _ => null,
    };

    useEffect(() {
      if (currentStep != null && syncedStepId.value != currentStep.id) {
        slugController.text = currentStep.slug;
        syncedStepId.value = currentStep.id;
      }
      return null;
    }, [currentStep?.id, currentStep?.slug]);

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

    return AppErrorBoundary(
      child: switch (formState) {
        AsyncLoading() => Scaffold(
          appBar: AppBar(title: Text(l10n.stepEditTitle)),
          body: const Center(child: CircularProgressIndicator()),
        ),
        AsyncError(:final error, :final stackTrace) => Scaffold(
          appBar: AppBar(title: Text(l10n.stepEditTitle)),
          body: ErrorView(
            error: error,
            stackTrace: stackTrace,
            compact: false,
            onRetry: () => ref.invalidate(stepFormProvider(stepId)),
          ),
        ),
        AsyncData(:final value) => switch ((
          promptBlocksAsync,
          mcpGatewaysAsync,
        )) {
          (AsyncError(:final error), _) => throw error,
          (_, AsyncError(:final error)) => throw error,
          (
            AsyncData(value: final promptBlocks),
            AsyncData(value: final mcpGateways),
          ) =>
            _buildScaffold(
              context,
              ref,
              l10n,
              formState,
              value,
              stepId,
              promptBlocks,
              mcpGateways,
              deleteMutation,
              idFocusNode,
              slugController,
              slugFocusNode,
            ),
          _ => const Scaffold(body: Center(child: CircularProgressIndicator())),
        },
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
    final currentLocale = Localizations.localeOf(context).languageCode;
    final nameToDisplay = trans[currentLocale] ?? trans['en'];

    if (nameToDisplay == null || nameToDisplay.trim().isEmpty) {
      throw AppException.validation(
        'Fail-Fast: Step $id lacks required localization for active language or English fallback.',
      );
    }

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(l10n.stepDeleteConfirmTitle),
        content: Text(l10n.stepDeleteConfirmMessage(nameToDisplay)),
        actions: [
          TextButton(
            style: TextButton.styleFrom(
              enabledMouseCursor: SystemMouseCursors.click,
            ),
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
    List<McpGateway> mcpGateways,
    MutationState<void> deleteMutation,
    FocusNode idFocusNode,
    TextEditingController slugController,
    FocusNode slugFocusNode,
  ) {
    Future<void> saveStep() async {
      final effectivePayload = payload.copyWith(
        slug: slugController.text.trim(),
      );
      final id = effectivePayload.id.trim();
      if (id.isEmpty) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(l10n.idRequiredError),
            backgroundColor: Theme.of(context).colorScheme.error,
          ),
        );
        return;
      }

      if (effectivePayload is NodeStrategyLlm) {
        // Specialist LLM blueprints require at least one role, persona, or criteria block
        if (!effectivePayload.isSystemCore) {
          final hasRoleOrPersona =
              (effectivePayload.roleBlockId != null &&
                  effectivePayload.roleBlockId!.isNotEmpty) ||
              (effectivePayload.executionPersonaBlockId != null &&
                  effectivePayload.executionPersonaBlockId!.isNotEmpty) ||
              effectivePayload.criteriaBlockIds.isNotEmpty;

          if (!hasRoleOrPersona) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text(l10n.studioStepBuilderRoleOrCriteriaRequired),
                backgroundColor: Theme.of(context).colorScheme.error,
              ),
            );
            return;
          }
        }
      }

      try {
        await ref
            .read(stepFormProvider(stepId).notifier)
            .submit(effectivePayload);
        if (context.mounted) {
          ScaffoldMessenger.of(
            context,
          ).showSnackBar(SnackBar(content: Text(l10n.stepSavedSuccess)));
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

    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          mouseCursor: SystemMouseCursors.click,
          icon: const Icon(Icons.arrow_back),
          tooltip: l10n.backToStudioTooltip,
          onPressed: () => context.go('/admin'),
        ),
        title: Text(l10n.stepEditTitle),
        actions: [
          if (payload.id.isNotEmpty && !payload.isSystemCore)
            IconButton(
              mouseCursor: SystemMouseCursors.click,
              onPressed: () =>
                  _deleteStep(context, ref, l10n, payload, deleteMutation),
              icon: Icon(
                Icons.delete,
                color: Theme.of(context).colorScheme.error,
              ),
              tooltip: l10n.delete,
            ),
          IconButton(
            mouseCursor: SystemMouseCursors.click,
            onPressed: () => showDialog<void>(
              context: context,
              builder: (ctx) => StepSimulationDialog(
                step: payload.copyWith(slug: slugController.text.trim()),
              ),
            ),
            icon: Icon(
              Icons.bug_report,
              color: Theme.of(context).colorScheme.primary,
            ),
            tooltip: l10n.simulateStepTooltip,
          ),
          if (formState.isLoading)
            const Padding(
              padding: EdgeInsets.symmetric(horizontal: AppSpacing.s16),
              child: Center(
                child: SizedBox(
                  width: AppSpacing.s16,
                  height: AppSpacing.s16,
                  child: CircularProgressIndicator(strokeWidth: AppSpacing.s2),
                ),
              ),
            )
          else
            TextButton.icon(
              style: TextButton.styleFrom(
                enabledMouseCursor: SystemMouseCursors.click,
              ),
              onPressed: saveStep,
              icon: const Icon(Icons.save),
              label: Text(l10n.studioSaveButton),
            ),
          AppSpacing.w16,
        ],
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: AppSpacing.p16,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Card(
                elevation: AppSpacing.s2,
                margin: const EdgeInsets.only(bottom: AppSpacing.s16),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(AppSpacing.s12),
                ),
                child: Padding(
                  padding: AppSpacing.p16,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Flexible(
                            child: Text(
                              l10n.configurationTitle,
                              overflow: TextOverflow.ellipsis,
                              style: Theme.of(context).textTheme.titleMedium
                                  ?.copyWith(fontWeight: FontWeight.bold),
                            ),
                          ),
                          if (payload.isSystemCore) ...[
                            AppSpacing.w8,
                            Flexible(
                              child: Container(
                                padding: const EdgeInsets.symmetric(
                                  horizontal: AppSpacing.s8,
                                  vertical: AppSpacing.s2,
                                ),
                                decoration: BoxDecoration(
                                  color: Theme.of(
                                    context,
                                  ).colorScheme.primaryContainer,
                                  borderRadius: BorderRadius.circular(
                                    AppSpacing.s12,
                                  ),
                                ),
                                child: Text(
                                  l10n.studioSystemCoreBadge,
                                  overflow: TextOverflow.ellipsis,
                                  style: Theme.of(context).textTheme.labelSmall
                                      ?.copyWith(
                                        fontWeight: FontWeight.w600,
                                        color: Theme.of(
                                          context,
                                        ).colorScheme.onPrimaryContainer,
                                      ),
                                ),
                              ),
                            ),
                          ],
                        ],
                      ),
                      AppSpacing.h16,
                      TextFormField(
                        focusNode: idFocusNode,
                        initialValue: payload.id,
                        decoration: InputDecoration(
                          labelText: l10n.stepIdLabel,
                          border: const OutlineInputBorder(),
                        ),
                        readOnly: true,
                      ),
                      AppSpacing.h16,
                      TextFormField(
                        controller: slugController,
                        focusNode: slugFocusNode,
                        decoration: InputDecoration(
                          labelText: l10n.slugLabel,
                          border: const OutlineInputBorder(),
                        ),
                      ),
                      AppSpacing.h16,
                      I18nTextField(
                        label: l10n.nameLabel,
                        initialData: payload.name,
                        onChanged: (val) {
                          ref
                              .read(stepFormProvider(stepId).notifier)
                              .forceRebuild(
                                payload.copyWith(
                                  slug: slugController.text.trim(),
                                  name: val,
                                ),
                              );
                        },
                      ),
                      AppSpacing.h16,
                      I18nTextField(
                        label: l10n.descriptionLabel,
                        initialData: payload.description,
                        onChanged: (val) {
                          ref
                              .read(stepFormProvider(stepId).notifier)
                              .forceRebuild(
                                payload.copyWith(
                                  slug: slugController.text.trim(),
                                  description: val,
                                ),
                              );
                        },
                      ),
                      AppSpacing.h16,
                      if (payload is NodeStrategyLlm)
                        DropdownButtonFormField<CognitiveTier>(
                          key: ValueKey(payload.cognitiveTier),
                          isExpanded: true,
                          initialValue: payload.cognitiveTier,
                          decoration: InputDecoration(
                            labelText: l10n.studioCognitiveTierLabel,
                            border: const OutlineInputBorder(),
                            isDense: true,
                          ),
                          items: CognitiveTier.values.map((tier) {
                            final label = switch (tier) {
                              CognitiveTier.fast => l10n.studioTierFast,
                              CognitiveTier.balanced => l10n.studioTierBalanced,
                              CognitiveTier.deep => l10n.studioTierDeep,
                              CognitiveTier.reasoning =>
                                l10n.studioTierReasoning,
                            };
                            return DropdownMenuItem(
                              value: tier,
                              child: Text(
                                label,
                                overflow: TextOverflow.ellipsis,
                              ),
                            );
                          }).toList(),
                          onChanged: (val) {
                            if (val != null) {
                              ref
                                  .read(stepFormProvider(stepId).notifier)
                                  .forceRebuild(
                                    payload.copyWith(
                                      slug: slugController.text.trim(),
                                      cognitiveTier: val,
                                    ),
                                  );
                            }
                          },
                        ),
                    ],
                  ),
                ),
              ),

              AppSpacing.h24,

              Text(
                l10n.mcpGatewaysTitle,
                style: Theme.of(
                  context,
                ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
              ),
              AppSpacing.h16,
              ...mcpGateways
                  .where(
                    (gateway) => gateway.tools.any(
                      (tool) => tool.enabled && tool.toolId.isNotEmpty,
                    ),
                  )
                  .map((gateway) {
                    final enabledTools = gateway.tools
                        .where((tool) => tool.enabled && tool.toolId.isNotEmpty)
                        .toList();

                    return Padding(
                      padding: const EdgeInsets.only(bottom: AppSpacing.s16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            gateway.slug,
                            style: Theme.of(context).textTheme.titleSmall
                                ?.copyWith(fontWeight: FontWeight.w600),
                          ),
                          AppSpacing.h8,
                          Wrap(
                            spacing: AppSpacing.s8,
                            runSpacing: AppSpacing.s8,
                            children: enabledTools.map((tool) {
                              final namespacedAlias =
                                  '${gateway.slug}__${tool.toolId}';
                              final currentLocale = Localizations.localeOf(
                                context,
                              ).languageCode;
                              final labelText = tool.name.get(currentLocale);

                              if (labelText.trim().isEmpty) {
                                throw AppException.validation(
                                  'Fail-Fast: MCP tool $namespacedAlias lacks required translation for locale $currentLocale or en fallback.',
                                );
                              }

                              final allowedMcpTools = List<String>.from(
                                payload.allowedMcpTools,
                              );
                              final isSelected = allowedMcpTools.contains(
                                namespacedAlias,
                              );
                              final chipLabel = '$labelText ($namespacedAlias)';

                              return FilterChip(
                                mouseCursor: SystemMouseCursors.click,
                                label: Text(chipLabel),
                                selected: isSelected,
                                onSelected: (bool selected) {
                                  if (selected) {
                                    if (!allowedMcpTools.contains(
                                      namespacedAlias,
                                    )) {
                                      allowedMcpTools.add(namespacedAlias);
                                    }
                                  } else {
                                    allowedMcpTools.remove(namespacedAlias);
                                  }
                                  final updatedToolParams =
                                      <String, Map<String, Object?>>{
                                        for (final entry
                                            in payload.mcpToolParams.entries)
                                          if (selected ||
                                              entry.key != namespacedAlias)
                                            entry.key:
                                                Map<String, Object?>.from(
                                                  entry.value,
                                                ),
                                      };
                                  ref
                                      .read(stepFormProvider(stepId).notifier)
                                      .forceRebuild(
                                        payload.copyWith(
                                          slug: slugController.text.trim(),
                                          allowedMcpTools: allowedMcpTools,
                                          mcpToolParams: updatedToolParams,
                                        ),
                                      );
                                },
                              );
                            }).toList(),
                          ),
                        ],
                      ),
                    );
                  }),

              AppSpacing.h24,

              McpToolParamsPanel(
                allowedMcpTools: payload.allowedMcpTools,
                mcpToolParams: payload.mcpToolParams,
                mcpGateways: mcpGateways,
                onChanged: (updatedParams) {
                  ref
                      .read(stepFormProvider(stepId).notifier)
                      .forceRebuild(
                        payload.copyWith(
                          slug: slugController.text.trim(),
                          mcpToolParams: updatedParams,
                        ),
                      );
                },
              ),

              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(
                    child: Text(
                      l10n.preHooksTitle,
                      overflow: TextOverflow.ellipsis,
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  AppSpacing.w8,
                  OutlinedButton.icon(
                    style: OutlinedButton.styleFrom(
                      enabledMouseCursor: SystemMouseCursors.click,
                    ),
                    onPressed: () => _addPreHook(ref, payload, stepId),
                    icon: const Icon(Icons.add),
                    label: Text(l10n.addHookBtn),
                  ),
                ],
              ),
              AppSpacing.h16,
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
                      .forceRebuild(
                        payload.copyWith(
                          slug: slugController.text.trim(),
                          preHooks: hooks,
                        ),
                      );
                },
                itemBuilder: (context, index) {
                  final hooks = payload.preHooks;
                  return _buildPreHookCard(
                    context,
                    ref,
                    l10n,
                    payload,
                    stepId,
                    ValueKey('hook_${index}_${hooks[index]}'),
                    index,
                    hooks[index],
                  );
                },
              ),
              AppSpacing.h24,

              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(
                    child: Text(
                      l10n.postHooksTitle,
                      overflow: TextOverflow.ellipsis,
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  AppSpacing.w8,
                  OutlinedButton.icon(
                    style: OutlinedButton.styleFrom(
                      enabledMouseCursor: SystemMouseCursors.click,
                    ),
                    onPressed: () => _addPostHook(ref, payload, stepId),
                    icon: const Icon(Icons.add),
                    label: Text(l10n.addHookBtn),
                  ),
                ],
              ),
              AppSpacing.h16,
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
                      .forceRebuild(
                        payload.copyWith(
                          slug: slugController.text.trim(),
                          postHooks: hooks,
                        ),
                      );
                },
                itemBuilder: (context, index) {
                  final hooks = payload.postHooks;
                  return _buildPostHookCard(
                    context,
                    ref,
                    l10n,
                    payload,
                    stepId,
                    ValueKey('post_hook_${index}_${hooks[index]}'),
                    index,
                    hooks[index],
                  );
                },
              ),

              AppSpacing.h24,

              if (payload is NodeStrategyLlm) ...[
                AppSpacing.h24,
                Card(
                  elevation: AppSpacing.s2,
                  margin: const EdgeInsets.only(bottom: AppSpacing.s16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(AppSpacing.s12),
                  ),
                  child: Padding(
                    padding: AppSpacing.p16,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          l10n.protocolBlockLabel,
                          style: Theme.of(context).textTheme.titleMedium
                              ?.copyWith(fontWeight: FontWeight.bold),
                        ),
                        AppSpacing.h4,
                        Text(
                          l10n.protocolBlockDescription,
                          style: Theme.of(context).textTheme.bodySmall
                              ?.copyWith(
                                color: Theme.of(
                                  context,
                                ).colorScheme.onSurfaceVariant,
                              ),
                        ),
                        AppSpacing.h12,
                        DropdownButtonFormField<String>(
                          isExpanded: true,
                          decoration: const InputDecoration(
                            border: OutlineInputBorder(),
                            isDense: true,
                          ),
                          initialValue:
                              promptBlocks.any(
                                (m) =>
                                    m.id == payload.extractionProtocolBlockId &&
                                    PromptBlockCategoryGroups.protocolCategories
                                        .contains(m.categoryId),
                              )
                              ? payload.extractionProtocolBlockId
                              : null,
                          items: [
                            DropdownMenuItem<String>(
                              value: null,
                              child: Text(
                                l10n.noneDefaultLabel,
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                            ...promptBlocks
                                .where(
                                  (m) => PromptBlockCategoryGroups
                                      .protocolCategories
                                      .contains(m.categoryId),
                                )
                                .map((m) {
                                  final currentLocale = Localizations.localeOf(
                                    context,
                                  ).languageCode;
                                  final rawLabel =
                                      m.label.translations[currentLocale] ??
                                      m.label.translations['en'];

                                  if (rawLabel == null ||
                                      rawLabel.trim().isEmpty) {
                                    throw AppException.validation(
                                      'Fail-Fast: PromptBlock ${m.id} lacks required translation for locale $currentLocale or en fallback.',
                                    );
                                  }

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
                                    slug: slugController.text.trim(),
                                    extractionProtocolBlockId: val,
                                  ),
                                );
                          },
                        ),
                      ],
                    ),
                  ),
                ),

                AppSpacing.h24,
                Card(
                  elevation: AppSpacing.s2,
                  margin: const EdgeInsets.only(bottom: AppSpacing.s16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(AppSpacing.s12),
                  ),
                  child: Padding(
                    padding: AppSpacing.p16,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          l10n.executionPersonaTitle,
                          style: Theme.of(context).textTheme.titleMedium
                              ?.copyWith(fontWeight: FontWeight.bold),
                        ),
                        AppSpacing.h4,
                        Text(
                          l10n.executionPersonaDescription,
                          style: Theme.of(context).textTheme.bodySmall
                              ?.copyWith(
                                color: Theme.of(
                                  context,
                                ).colorScheme.onSurfaceVariant,
                              ),
                        ),
                        AppSpacing.h12,
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
                                    PromptBlockCategoryGroups.personaCategories
                                        .contains(m.categoryId),
                              )
                              ? payload.executionPersonaBlockId
                              : null,
                          items: [
                            DropdownMenuItem<String>(
                              value: null,
                              child: Text(
                                l10n.noneDefaultLabel,
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                            ...promptBlocks
                                .where(
                                  (m) => PromptBlockCategoryGroups
                                      .personaCategories
                                      .contains(m.categoryId),
                                )
                                .map((m) {
                                  final currentLocale = Localizations.localeOf(
                                    context,
                                  ).languageCode;
                                  final rawLabel =
                                      m.label.translations[currentLocale] ??
                                      m.label.translations['en'];

                                  if (rawLabel == null ||
                                      rawLabel.trim().isEmpty) {
                                    throw AppException.validation(
                                      'Fail-Fast: PromptBlock ${m.id} lacks required translation for locale $currentLocale or en fallback.',
                                    );
                                  }

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
                                    slug: slugController.text.trim(),
                                    executionPersonaBlockId: val,
                                  ),
                                );
                          },
                        ),
                      ],
                    ),
                  ),
                ),

                AppSpacing.h24,
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            l10n.criteriaBlocksTitle,
                            overflow: TextOverflow.ellipsis,
                            style: Theme.of(context).textTheme.titleLarge
                                ?.copyWith(fontWeight: FontWeight.bold),
                          ),
                          AppSpacing.h4,
                          Text(
                            l10n.criteriaBlocksDescription,
                            overflow: TextOverflow.ellipsis,
                            style: Theme.of(context).textTheme.bodySmall
                                ?.copyWith(
                                  color: Theme.of(
                                    context,
                                  ).colorScheme.onSurfaceVariant,
                                ),
                          ),
                        ],
                      ),
                    ),
                    AppSpacing.w8,
                    OutlinedButton.icon(
                      style: OutlinedButton.styleFrom(
                        enabledMouseCursor: SystemMouseCursors.click,
                      ),
                      onPressed: () => _addCriteriaBlock(ref, payload, stepId),
                      icon: const Icon(Icons.add),
                      label: Text(l10n.addPromptBlockBtn),
                    ),
                  ],
                ),
                AppSpacing.h16,
                ReorderableListView.builder(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  itemCount: payload.criteriaBlockIds.length,
                  onReorder: (oldIndex, newIndex) {
                    if (oldIndex < newIndex) newIndex -= 1;
                    final blocks = List<String>.from(payload.criteriaBlockIds);
                    final item = blocks.removeAt(oldIndex);
                    blocks.insert(newIndex, item);
                    ref
                        .read(stepFormProvider(stepId).notifier)
                        .forceRebuild(
                          payload.copyWith(
                            slug: slugController.text.trim(),
                            criteriaBlockIds: blocks,
                          ),
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
                      ValueKey('criteria_block_${index}_${blocks[index]}'),
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
    );
  }

  Widget _buildPreHookCard(
    BuildContext context,
    WidgetRef ref,
    AppLocalizations l10n,
    NodeStrategy payload,
    String stepId,
    Key key,
    int index,
    String hookDef,
  ) {
    const knownHooks = <String>[
      'search_hook',
      'memory_hook',
      'validation_hook',
      'score_hook',
    ];
    if (hookDef.isNotEmpty && !knownHooks.contains(hookDef)) {
      throw AppException.validation(
        'Fail-Fast: Unsupported pre-hook "$hookDef" in step $stepId.',
      );
    }

    return Card(
      key: key,
      elevation: AppSpacing.s2,
      margin: const EdgeInsets.only(bottom: AppSpacing.s12),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppSpacing.s12),
      ),
      child: Padding(
        padding: AppSpacing.p12,
        child: Row(
          children: [
            Padding(
              padding: const EdgeInsets.only(right: AppSpacing.s8),
              child: Icon(
                Icons.drag_indicator,
                color: Theme.of(context).colorScheme.onSurfaceVariant,
              ),
            ),
            Expanded(
              child: DropdownButtonFormField<String>(
                isExpanded: true,
                decoration: InputDecoration(labelText: l10n.preHookEngineLabel),
                initialValue: hookDef.isEmpty ? null : hookDef,
                items: [
                  DropdownMenuItem(
                    value: 'search_hook',
                    child: Text(
                      l10n.hookTavily,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  DropdownMenuItem(
                    value: 'memory_hook',
                    child: Text(
                      l10n.hookMemory,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  DropdownMenuItem(
                    value: 'validation_hook',
                    child: Text(
                      l10n.hookValidation,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  DropdownMenuItem(
                    value: 'score_hook',
                    child: Text(
                      l10n.hookScore,
                      overflow: TextOverflow.ellipsis,
                    ),
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
              mouseCursor: SystemMouseCursors.click,
              icon: Icon(
                Icons.delete,
                color: Theme.of(context).colorScheme.error,
              ),
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
    BuildContext context,
    WidgetRef ref,
    AppLocalizations l10n,
    NodeStrategy payload,
    String stepId,
    Key key,
    int index,
    String hookDef,
  ) {
    const knownHooks = <String>[
      'search_hook',
      'memory_hook',
      'validation_hook',
      'score_hook',
      'waterfall_scoring_hook',
      'normalize_matrix_scores',
      'verify_citation_integrity',
      'enforce_hypothesis_linking',
    ];
    if (hookDef.isNotEmpty && !knownHooks.contains(hookDef)) {
      throw AppException.validation(
        'Fail-Fast: Unsupported post-hook "$hookDef" in step $stepId.',
      );
    }

    return Card(
      key: key,
      elevation: AppSpacing.s2,
      margin: const EdgeInsets.only(bottom: AppSpacing.s12),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppSpacing.s12),
      ),
      child: Padding(
        padding: AppSpacing.p12,
        child: Row(
          children: [
            Padding(
              padding: const EdgeInsets.only(right: AppSpacing.s8),
              child: Icon(
                Icons.drag_indicator,
                color: Theme.of(context).colorScheme.onSurfaceVariant,
              ),
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
                    child: Text(
                      l10n.hookWaterfall,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  DropdownMenuItem(
                    value: 'normalize_matrix_scores',
                    child: Text(
                      l10n.hookNormalize,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  DropdownMenuItem(
                    value: 'search_hook',
                    child: Text(
                      l10n.hookTavily,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  DropdownMenuItem(
                    value: 'memory_hook',
                    child: Text(
                      l10n.hookMemory,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  DropdownMenuItem(
                    value: 'validation_hook',
                    child: Text(
                      l10n.hookValidation,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  DropdownMenuItem(
                    value: 'score_hook',
                    child: Text(
                      l10n.hookScore,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  DropdownMenuItem(
                    value: 'verify_citation_integrity',
                    child: Text(
                      l10n.hookVerifyCitation,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  DropdownMenuItem(
                    value: 'enforce_hypothesis_linking',
                    child: Text(
                      l10n.hookHypothesis,
                      overflow: TextOverflow.ellipsis,
                    ),
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
              mouseCursor: SystemMouseCursors.click,
              icon: Icon(
                Icons.delete,
                color: Theme.of(context).colorScheme.error,
              ),
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
      elevation: AppSpacing.s2,
      margin: const EdgeInsets.only(bottom: AppSpacing.s12),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppSpacing.s12),
      ),
      child: Padding(
        padding: AppSpacing.p12,
        child: Row(
          children: [
            Padding(
              padding: const EdgeInsets.only(right: AppSpacing.s8),
              child: Icon(
                Icons.drag_indicator,
                color: Theme.of(context).colorScheme.onSurfaceVariant,
              ),
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
                          'Fail-Fast: PromptBlock ${m.id} lacks required translation for locale $currentLocale or en fallback.',
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
              mouseCursor: SystemMouseCursors.click,
              icon: Icon(
                Icons.delete,
                color: Theme.of(context).colorScheme.error,
              ),
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
