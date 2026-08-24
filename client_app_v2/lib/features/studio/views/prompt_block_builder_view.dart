import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:go_router/go_router.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:client_app/core/state/mutation.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';
import 'package:client_app/features/studio/controllers/prompt_blocks_controller.dart';
import 'package:client_app/features/studio/views/widgets/i18n_text_field.dart';
import 'package:client_app/core/error/app_error_boundary.dart';
import 'package:uuid/uuid.dart';
import 'package:client_app/core/error/app_error_ext.dart';
import 'package:client_app/features/studio/views/widgets/scale_editor_modal.dart';
import 'package:client_app/features/studio/views/widgets/row_editor_modal.dart';
import 'package:client_app/features/studio/views/components/bars_matrix_builder.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/core/models/prompt_block_category.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/shared/models/i18n_text.dart';

/// **Universal Matrix Builder**
///
/// CRUD interface for editing evaluation matrices adhering strictly to the
/// De-Generator policy (`Map<String, dynamic>`).
/// Now compliant with the Gold Standard Riverpod Form UI pattern.
class PromptBlockBuilderView extends HookConsumerWidget {
  final String? id;
  final String? slug;

  const PromptBlockBuilderView({super.key, this.id, this.slug});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final blockId = (id == null || id!.isEmpty) ? 'new' : id!;
    final AsyncValue<PromptBlock> formState = ref.watch(
      promptBlockFormProvider(blockId),
    );

    return switch (formState) {
      AsyncData(:final value) => _buildScaffold(
        context,
        ref,
        l10n,
        formState,
        value,
        blockId,
      ),
      AsyncError(:final error, :final stackTrace) => Scaffold(
        appBar: AppBar(title: Text(l10n.promptBlockEditTitle)),
        body: ErrorView(
          error: error,
          stackTrace: stackTrace,
          compact: false,
          onRetry: () => ref.invalidate(promptBlockFormProvider(blockId)),
        ),
      ),
      _ => Scaffold(
        appBar: AppBar(title: Text(l10n.promptBlockEditTitle)),
        body: const Center(child: CircularProgressIndicator()),
      ),
    };
  }

  void _addListItem<T>(
    WidgetRef ref,
    String blockId,
    List<T> currentList,
    T initialValue,
    PromptBlock Function(List<T>) updater,
  ) {
    final newList = List<T>.from(currentList)..add(initialValue);
    ref
        .read(promptBlockFormProvider(blockId).notifier)
        .forceRebuild(updater(newList));
  }

  void _removeListItem<T>(
    WidgetRef ref,
    String blockId,
    List<T> currentList,
    int index,
    PromptBlock Function(List<T>) updater,
  ) {
    if (index >= 0 && index < currentList.length) {
      final newList = List<T>.from(currentList)..removeAt(index);
      ref
          .read(promptBlockFormProvider(blockId).notifier)
          .forceRebuild(updater(newList));
    }
  }

  void _deletePromptBlock(
    BuildContext context,
    WidgetRef ref,
    AppLocalizations l10n,
    PromptBlock payload,
    MutationState<void> deleteMut,
  ) {
    final trans = payload.label.translations;
    final currentLocale = Localizations.localeOf(context).languageCode;
    final nameToDisplay = trans[currentLocale] ?? trans['en'];

    if (nameToDisplay == null || nameToDisplay.trim().isEmpty) {
      throw AppException.validation(
        'Fail-Fast: PromptBlock ${payload.id} lacks required localization for active language or English fallback.',
      );
    }

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
          TextButton(
            onPressed: () {
              Navigator.pop(ctx);
              deleteMut.mutate(
                () => ref
                    .read(promptBlocksControllerProvider.notifier)
                    .deletePromptBlock(payload.id),
              );
            },
            child: Text(
              l10n.delete,
              style: TextStyle(color: Theme.of(context).colorScheme.error),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildScaffold(
    BuildContext context,
    WidgetRef ref,
    AppLocalizations l10n,
    AsyncValue<PromptBlock> formState,
    PromptBlock payload,
    String blockId,
  ) {
    final isMatrix =
        payload.categoryId == 'matrix' &&
        (blockId != 'new' ||
            payload.scales != null ||
            payload.rows != null ||
            payload.columns != null);

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
              title: Text(l10n.compiledPromptPreviewTitle),
              content: SizedBox(
                width: double.maxFinite,
                child: SingleChildScrollView(
                  child: SelectableText(
                    rendered.isNotEmpty ? rendered : l10n.noInstructionsDefined,
                    style: const TextStyle(fontFamily: 'monospace'),
                  ),
                ),
              ),
              actions: [
                TextButton.icon(
                  onPressed: () async {
                    await Clipboard.setData(ClipboardData(text: rendered));
                    if (context.mounted) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(content: Text(l10n.promptCopiedSnackbar)),
                      );
                    }
                  },
                  icon: const Icon(Icons.copy),
                  label: Text(l10n.copyToClipboardBtn),
                ),
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
          ref
              .read(loggerServiceProvider)
              .error('Studio', 'Failed to validate prompt block: $e', e);
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
              .error('Studio', 'Failed to delete prompt block: $e', e);
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(errorMsg),
              backgroundColor: Theme.of(context).colorScheme.error,
            ),
          );
        }
      },
    );

    Future<void> savePromptBlock() async {
      final enLabel = payload.label.translations['en'] ?? '';

      if (enLabel.isEmpty) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(l10n.promptBlockMandatoryEnglishError)),
        );
        return;
      }

      final uuidHex = const Uuid().v4().replaceAll('-', '');
      final currentId = payload.id.isNotEmpty ? payload.id : 'blk_$uuidHex';

      final savingPayload = payload.copyWith(id: currentId);

      try {
        await ref
            .read(promptBlockFormProvider(blockId).notifier)
            .submit(savingPayload);
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(l10n.promptBlockSavedSuccess),
              backgroundColor: Theme.of(context).colorScheme.primaryContainer,
            ),
          );
          context.pop();
        }
      } catch (e) {
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(l10n.saveFailedError(e.toString())),
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
            tooltip: l10n.backToStudioTooltip,
            onPressed: () => context.go('/admin'),
          ),
          title: Text(l10n.promptBlockEditTitle),
          actions: [
            if (payload.id.isNotEmpty == true)
              IconButton(
                onPressed: () => _deletePromptBlock(
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
                        return await ref
                            .read(promptBlocksControllerProvider.notifier)
                            .simulatePromptBlock(payload, {});
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
              tooltip: l10n.compiledPromptPreviewTooltip,
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
                onPressed: savePromptBlock,
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
                // Matrix Metadata
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          l10n.promptBlockConfigTitle,
                          style: const TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 16),
                        if (payload.id.isNotEmpty == true) ...[
                          Text(
                            l10n.opaqueIdLabel(payload.id),
                            style: TextStyle(
                              color: Theme.of(
                                context,
                              ).colorScheme.onSurfaceVariant,
                              fontFamily: 'monospace',
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(height: 24),
                        ],
                      ],
                    ),
                  ),
                ),

                const SizedBox(height: 24),

                // --- ROOT CONFIGURATION (NO MORE CRITERIA ARRAY) ---
                const SizedBox(height: 16),
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        Text(
                          l10n.promptBlockPropertiesTitle,
                          style: const TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 16),

                        // Categories
                        DropdownButtonFormField<PromptBlockCategory>(
                          decoration: InputDecoration(
                            labelText: l10n.categoryLabel,
                            helperText: isMatrix
                                ? l10n.matrixCategoryLockedHelper
                                : null,
                          ),
                          initialValue: PromptBlockCategory.fromId(
                            payload.categoryId,
                          ),
                          items: PromptBlockCategory.values.map((category) {
                            return DropdownMenuItem(
                              value: category,
                              child: Text(category.displayName(context)),
                            );
                          }).toList(),
                          onChanged: isMatrix
                              ? null
                              : (val) {
                                  if (val != null) {
                                    final newBlock = switch (val) {
                                      PromptBlockCategory.matrix =>
                                        PromptBlock.matrix(
                                          id: payload.id,
                                          slug: payload.slug,
                                          organizationId:
                                              payload.organizationId,
                                          label: payload.label,
                                          description: payload.description,
                                          aiDescription: payload.aiDescription,
                                          isEvaluative: payload.isEvaluative,
                                          type: payload.type,
                                          allowDecimals: payload.allowDecimals,
                                          outputExtensions:
                                              payload.outputExtensions,
                                          theoryGrounding:
                                              payload.theoryGrounding,
                                          isLightweightProtocol:
                                              payload.isLightweightProtocol,
                                          scales: const [],
                                        ),
                                      PromptBlockCategory.systemRule =>
                                        PromptBlock.systemRule(
                                          id: payload.id,
                                          slug: payload.slug,
                                          organizationId:
                                              payload.organizationId,
                                          label: payload.label,
                                          description: payload.description,
                                          aiDescription: payload.aiDescription,
                                          isEvaluative: payload.isEvaluative,
                                          type: payload.type,
                                          allowDecimals: payload.allowDecimals,
                                          outputExtensions:
                                              payload.outputExtensions,
                                          theoryGrounding:
                                              payload.theoryGrounding,
                                          isLightweightProtocol:
                                              payload.isLightweightProtocol,
                                        ),
                                      PromptBlockCategory.executionPersona =>
                                        PromptBlock.executionPersona(
                                          id: payload.id,
                                          slug: payload.slug,
                                          organizationId:
                                              payload.organizationId,
                                          label: payload.label,
                                          description: payload.description,
                                          aiDescription: payload.aiDescription,
                                          isEvaluative: payload.isEvaluative,
                                          type: payload.type,
                                          allowDecimals: payload.allowDecimals,
                                          outputExtensions:
                                              payload.outputExtensions,
                                          theoryGrounding:
                                              payload.theoryGrounding,
                                          isLightweightProtocol:
                                              payload.isLightweightProtocol,
                                        ),
                                      PromptBlockCategory.agentRole =>
                                        PromptBlock.agentRole(
                                          id: payload.id,
                                          slug: payload.slug,
                                          organizationId:
                                              payload.organizationId,
                                          label: payload.label,
                                          description: payload.description,
                                          aiDescription: payload.aiDescription,
                                          isEvaluative: payload.isEvaluative,
                                          type: payload.type,
                                          allowDecimals: payload.allowDecimals,
                                          outputExtensions:
                                              payload.outputExtensions,
                                          theoryGrounding:
                                              payload.theoryGrounding,
                                          isLightweightProtocol:
                                              payload.isLightweightProtocol,
                                        ),
                                      PromptBlockCategory.protocol =>
                                        PromptBlock.protocol(
                                          id: payload.id,
                                          slug: payload.slug,
                                          organizationId:
                                              payload.organizationId,
                                          label: payload.label,
                                          description: payload.description,
                                          aiDescription: payload.aiDescription,
                                          isEvaluative: payload.isEvaluative,
                                          type: payload.type,
                                          allowDecimals: payload.allowDecimals,
                                          outputExtensions:
                                              payload.outputExtensions,
                                          theoryGrounding:
                                              payload.theoryGrounding,
                                          isLightweightProtocol:
                                              payload.isLightweightProtocol,
                                        ),
                                      PromptBlockCategory.runtimeVariables =>
                                        PromptBlock.runtimeVariables(
                                          id: payload.id,
                                          slug: payload.slug,
                                          organizationId:
                                              payload.organizationId,
                                          label: payload.label,
                                          description: payload.description,
                                          aiDescription: payload.aiDescription,
                                          isEvaluative: payload.isEvaluative,
                                          type: payload.type,
                                          allowDecimals: payload.allowDecimals,
                                          outputExtensions:
                                              payload.outputExtensions,
                                          theoryGrounding:
                                              payload.theoryGrounding,
                                          isLightweightProtocol:
                                              payload.isLightweightProtocol,
                                        ),
                                      PromptBlockCategory.taskDefinition =>
                                        PromptBlock.taskDefinition(
                                          id: payload.id,
                                          slug: payload.slug,
                                          organizationId:
                                              payload.organizationId,
                                          label: payload.label,
                                          description: payload.description,
                                          aiDescription: payload.aiDescription,
                                          isEvaluative: payload.isEvaluative,
                                          type: payload.type,
                                          allowDecimals: payload.allowDecimals,
                                          outputExtensions:
                                              payload.outputExtensions,
                                          theoryGrounding:
                                              payload.theoryGrounding,
                                          isLightweightProtocol:
                                              payload.isLightweightProtocol,
                                        ),
                                    };
                                    ref
                                        .read(
                                          promptBlockFormProvider(
                                            blockId,
                                          ).notifier,
                                        )
                                        .forceRebuild(newBlock);
                                  }
                                },
                        ),
                        const SizedBox(height: 16),

                        // Label (I18N)
                        I18nTextField(
                          label: l10n.blockLabelName,
                          initialData: payload.label,
                          onChanged: (val) {
                            ref
                                .read(promptBlockFormProvider(blockId).notifier)
                                .forceRebuild(payload.copyWith(label: val));
                          },
                        ),
                        AppSpacing.h16,

                        // Description (I18N) - Short UI Hint
                        I18nTextField(
                          label: l10n.shortDescriptionHint,
                          initialData: payload.description,
                          onChanged: (val) {
                            ref
                                .read(promptBlockFormProvider(blockId).notifier)
                                .forceRebuild(
                                  payload.copyWith(description: val),
                                );
                          },
                        ),
                        AppSpacing.h16,

                        // Zero-XML Polymorphic Form Sections
                        _buildPolymorphicInstructionSection(
                          context,
                          ref,
                          l10n,
                          payload,
                          blockId,
                        ),
                        AppSpacing.h16,

                        // XAI & Constraints Container
                        Container(
                          padding: const EdgeInsets.all(12),
                          color: Theme.of(
                            context,
                          ).colorScheme.surfaceContainerHighest,
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.stretch,
                            children: [
                              Text(
                                l10n.dataTypeExecutionConstraints,
                                style: const TextStyle(
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              const SizedBox(height: 12),
                              Wrap(
                                spacing: 16,
                                runSpacing: 8,
                                crossAxisAlignment: WrapCrossAlignment.center,
                                children: [
                                  DropdownButton<BlockDataType>(
                                    value: payload.type,
                                    items: [
                                      DropdownMenuItem(
                                        value: BlockDataType.instruction,
                                        child: Text(l10n.typeInstruction),
                                      ),
                                      DropdownMenuItem(
                                        value: BlockDataType.stringType,
                                        child: Text(l10n.typeString),
                                      ),
                                      DropdownMenuItem(
                                        value: BlockDataType.intType,
                                        child: Text(l10n.typeInteger),
                                      ),
                                      DropdownMenuItem(
                                        value: BlockDataType.floatType,
                                        child: Text(l10n.typeFloat),
                                      ),
                                    ],
                                    onChanged: (val) {
                                      if (val != null) {
                                        ref
                                            .read(
                                              promptBlockFormProvider(
                                                blockId,
                                              ).notifier,
                                            )
                                            .forceRebuild(
                                              payload.copyWith(type: val),
                                            );
                                      }
                                    },
                                  ),
                                  Row(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      Checkbox(
                                        value: payload.allowDecimals,
                                        onChanged: (val) {
                                          if (val != null) {
                                            ref
                                                .read(
                                                  promptBlockFormProvider(
                                                    blockId,
                                                  ).notifier,
                                                )
                                                .forceRebuild(
                                                  payload.copyWith(
                                                    allowDecimals: val,
                                                  ),
                                                );
                                          }
                                        },
                                      ),
                                      Text(l10n.allowDecimals),
                                    ],
                                  ),
                                  Row(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      Checkbox(
                                        value: payload.isEvaluative,
                                        onChanged: (val) {
                                          if (val != null) {
                                            ref
                                                .read(
                                                  promptBlockFormProvider(
                                                    blockId,
                                                  ).notifier,
                                                )
                                                .forceRebuild(
                                                  payload.copyWith(
                                                    isEvaluative: val,
                                                  ),
                                                );
                                          }
                                        },
                                      ),
                                      Text(l10n.isEvaluativeMatrix),
                                    ],
                                  ),
                                ],
                              ),
                              const SizedBox(height: 16),
                              Text(
                                l10n.xaiOutputExtensionsTitle,
                                style: const TextStyle(
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              const SizedBox(height: 8),
                              Wrap(
                                spacing: 8,
                                runSpacing: 8,
                                children:
                                    {
                                      "justification": l10n.xaiJustification,
                                      "coaching": l10n.xaiCoachingTip,
                                      "falsification": l10n.xaiDevilsAdvocate,
                                      "missing_context": l10n.xaiMissingContext,
                                      "risk_flag": l10n.xaiRiskFlag,
                                      "remediation_steps": l10n.xaiRemediation,
                                      "emotional_sentiment": l10n.xaiSentiment,
                                      "theory_link": l10n.xaiTheoryLink,
                                      "confidence": l10n.xaiConfidence,
                                      "citation": l10n.xaiSourceCitation,
                                    }.entries.map((entry) {
                                      final extList = payload.outputExtensions;
                                      final isSelected = extList.contains(
                                        entry.key,
                                      );
                                      return FilterChip(
                                        label: Text(entry.value),
                                        selected: isSelected,
                                        onSelected: (bool selected) {
                                          final newList = List<String>.from(
                                            payload.outputExtensions,
                                          );
                                          if (selected) {
                                            newList.add(entry.key);
                                          } else {
                                            newList.remove(entry.key);
                                          }
                                          ref
                                              .read(
                                                promptBlockFormProvider(
                                                  blockId,
                                                ).notifier,
                                              )
                                              .forceRebuild(
                                                payload.copyWith(
                                                  outputExtensions: newList,
                                                ),
                                              );
                                        },
                                        selectedColor: Theme.of(
                                          context,
                                        ).colorScheme.primaryContainer,
                                        checkmarkColor: Theme.of(
                                          context,
                                        ).colorScheme.onPrimaryContainer,
                                      );
                                    }).toList(),
                              ),
                            ],
                          ),
                        ),

                        if (payload is MatrixPromptBlock) ...[
                          const SizedBox(height: 16),
                          // Contextual Override Configuration
                          Container(
                            padding: const EdgeInsets.all(12),
                            color: Theme.of(
                              context,
                            ).colorScheme.surfaceContainerHighest,
                            child: SwitchListTile(
                              title: Text(
                                l10n.allowContextualOverrideLabel,
                                style: const TextStyle(
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              subtitle: Padding(
                                padding: const EdgeInsets.only(top: 4.0),
                                child: Text(
                                  l10n.allowContextualOverrideDescription,
                                ),
                              ),
                              value: payload.allowContextualOverride,
                              onChanged: (val) {
                                ref
                                    .read(
                                      promptBlockFormProvider(blockId).notifier,
                                    )
                                    .forceRebuild(
                                      payload.copyWith(
                                        allowContextualOverride: val,
                                      ),
                                    );
                              },
                              contentPadding: EdgeInsets.zero,
                            ),
                          ),
                        ],

                        const SizedBox(height: 16),
                        // Ensemble Configuration
                        Container(
                          padding: const EdgeInsets.all(12),
                          color: Theme.of(
                            context,
                          ).colorScheme.surfaceContainerHighest,
                          child: SwitchListTile(
                            title: Text(
                              l10n.promptBlockEnsembleToggle,
                              style: const TextStyle(
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            subtitle: Padding(
                              padding: const EdgeInsets.only(top: 4.0),
                              child: Text(l10n.promptBlockEnsembleToggleDesc),
                            ),
                            value: !payload.isLightweightProtocol,
                            onChanged: (val) {
                              ref
                                  .read(
                                    promptBlockFormProvider(blockId).notifier,
                                  )
                                  .forceRebuild(
                                    payload.copyWith(
                                      isLightweightProtocol: !val,
                                    ),
                                  );
                            },
                            contentPadding: EdgeInsets.zero,
                          ),
                        ),

                        const SizedBox(height: 16),
                        // Theory Grounding Wrapper
                        Container(
                          padding: const EdgeInsets.all(12),
                          color: Theme.of(
                            context,
                          ).colorScheme.surfaceContainerHigh,
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.stretch,
                            children: [
                              Row(
                                mainAxisAlignment:
                                    MainAxisAlignment.spaceBetween,
                                children: [
                                  Text(
                                    l10n.theoryGroundingTitle,
                                    style: const TextStyle(
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                  Switch(
                                    value: payload.theoryGrounding != null,
                                    onChanged: (val) {
                                      if (val) {
                                        ref
                                            .read(
                                              promptBlockFormProvider(
                                                blockId,
                                              ).notifier,
                                            )
                                            .forceRebuild(
                                              payload.copyWith(
                                                theoryGrounding:
                                                    const TheoryGrounding(
                                                      sourceUrl: '',
                                                      citationReference: '',
                                                    ),
                                              ),
                                            );
                                      } else {
                                        ref
                                            .read(
                                              promptBlockFormProvider(
                                                blockId,
                                              ).notifier,
                                            )
                                            .forceRebuild(
                                              payload.copyWith(
                                                theoryGrounding: null,
                                              ),
                                            );
                                      }
                                    },
                                  ),
                                ],
                              ),
                              if (payload.theoryGrounding != null) ...[
                                const SizedBox(height: 8),
                                // Source URL
                                TextFormField(
                                  initialValue:
                                      payload.theoryGrounding!.sourceUrl,
                                  decoration: InputDecoration(
                                    labelText: l10n.sourceUrlLabel,
                                    border: const UnderlineInputBorder(),
                                  ),
                                  onChanged: (val) {
                                    ref
                                        .read(
                                          promptBlockFormProvider(
                                            blockId,
                                          ).notifier,
                                        )
                                        .forceRebuild(
                                          payload.copyWith(
                                            theoryGrounding: payload
                                                .theoryGrounding!
                                                .copyWith(sourceUrl: val),
                                          ),
                                        );
                                  },
                                ),
                                const SizedBox(height: 8),
                                TextFormField(
                                  initialValue: payload
                                      .theoryGrounding!
                                      .citationReference,
                                  decoration: InputDecoration(
                                    labelText: l10n.citationReferenceLabel,
                                    border: const UnderlineInputBorder(),
                                  ),
                                  onChanged: (val) {
                                    ref
                                        .read(
                                          promptBlockFormProvider(
                                            blockId,
                                          ).notifier,
                                        )
                                        .forceRebuild(
                                          payload.copyWith(
                                            theoryGrounding: payload
                                                .theoryGrounding!
                                                .copyWith(
                                                  citationReference: val,
                                                ),
                                          ),
                                        );
                                  },
                                ),
                              ],
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                if (payload is MatrixPromptBlock) ...[
                  const SizedBox(height: 16),
                  _buildRowListCard(
                    context,
                    ref,
                    l10n,
                    payload,
                    blockId,
                    l10n.gridRowsOptional,
                  ),
                  const SizedBox(height: 16),
                  _buildColumnListCard(
                    context,
                    ref,
                    l10n,
                    payload,
                    blockId,
                    l10n.gridColumnsOptional,
                  ),
                  const SizedBox(height: 16),
                  _buildScalesCard(context, ref, l10n, payload, blockId),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildRowListCard(
    BuildContext context,
    WidgetRef ref,
    AppLocalizations l10n,
    MatrixPromptBlock payload,
    String blockId,
    String title,
  ) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Row(
                  children: [
                    Switch(
                      value: payload.rows != null,
                      onChanged: (val) {
                        ref
                            .read(promptBlockFormProvider(blockId).notifier)
                            .forceRebuild(
                              payload.copyWith(rows: val ? [] : null),
                            );
                      },
                    ),
                    if (payload.rows != null) ...[
                      const SizedBox(width: 8),
                      OutlinedButton.icon(
                        onPressed: () async {
                          final result = await showDialog<MatrixRow>(
                            context: context,
                            builder: (ctx) => RowEditorModal(
                              initialMatrixRow: const MatrixRow(
                                label: I18nText(
                                  defaultLocale: 'en',
                                  translations: {'en': ''},
                                ),
                                aiDescription: 'CRITICAL MANDATE: ',
                              ),
                              title: 'Add $title',
                              isMatrixRow: true,
                            ),
                          );
                          if (result != null) {
                            _addListItem<MatrixRow>(
                              ref,
                              blockId,
                              payload.rows!,
                              result,
                              (list) => payload.copyWith(rows: list),
                            );
                          }
                        },
                        icon: const Icon(Icons.add),
                        label: const Text('Add'),
                      ),
                    ],
                  ],
                ),
              ],
            ),
            if (payload.rows != null) ...[
              const SizedBox(height: 16),
              ...payload.rows!.asMap().entries.map((entry) {
                final index = entry.key;
                final item = entry.value;

                return Card(
                  margin: const EdgeInsets.only(bottom: 8.0),
                  color: Theme.of(context).colorScheme.surfaceContainerHighest,
                  child: ListTile(
                    title: Text(
                      item.label.translations[item.label.defaultLocale] ??
                          item.label.defaultLocale,
                    ),
                    subtitle: Text('Item ${index + 1}'),
                    trailing: IconButton(
                      icon: Icon(
                        Icons.delete,
                        color: Theme.of(context).colorScheme.error,
                      ),
                      onPressed: () => _removeListItem<MatrixRow>(
                        ref,
                        blockId,
                        payload.rows!,
                        index,
                        (list) => payload.copyWith(rows: list),
                      ),
                    ),
                    onTap: () async {
                      final result = await showDialog<MatrixRow>(
                        context: context,
                        builder: (ctx) => RowEditorModal(
                          initialMatrixRow: item,
                          title: 'Edit $title Item',
                          isMatrixRow: true,
                        ),
                      );
                      if (result != null) {
                        final list = List<MatrixRow>.from(payload.rows!);
                        list[index] = result;
                        ref
                            .read(promptBlockFormProvider(blockId).notifier)
                            .forceRebuild(payload.copyWith(rows: list));
                      }
                    },
                  ),
                );
              }),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildColumnListCard(
    BuildContext context,
    WidgetRef ref,
    AppLocalizations l10n,
    MatrixPromptBlock payload,
    String blockId,
    String title,
  ) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Row(
                  children: [
                    Switch(
                      value: payload.columns != null,
                      onChanged: (val) {
                        ref
                            .read(promptBlockFormProvider(blockId).notifier)
                            .forceRebuild(
                              payload.copyWith(columns: val ? [] : null),
                            );
                      },
                    ),
                    if (payload.columns != null) ...[
                      const SizedBox(width: 8),
                      OutlinedButton.icon(
                        onPressed: () async {
                          final result = await showDialog<I18nText>(
                            context: context,
                            builder: (ctx) => const RowEditorModal(
                              initialI18nText: I18nText(
                                defaultLocale: 'en',
                                translations: {'en': ''},
                              ),
                              title: 'Add Column',
                              isMatrixRow: false,
                            ),
                          );
                          if (result != null) {
                            _addListItem<I18nText>(
                              ref,
                              blockId,
                              payload.columns!,
                              result,
                              (list) => payload.copyWith(columns: list),
                            );
                          }
                        },
                        icon: const Icon(Icons.add),
                        label: const Text('Add'),
                      ),
                    ],
                  ],
                ),
              ],
            ),
            if (payload.columns != null) ...[
              const SizedBox(height: 16),
              ...payload.columns!.asMap().entries.map((entry) {
                final index = entry.key;
                final item = entry.value;

                return Card(
                  margin: const EdgeInsets.only(bottom: 8.0),
                  color: Theme.of(context).colorScheme.surfaceContainerHighest,
                  child: ListTile(
                    title: Text(
                      item.translations[item.defaultLocale] ??
                          item.defaultLocale,
                    ),
                    subtitle: Text('Item ${index + 1}'),
                    trailing: IconButton(
                      icon: Icon(
                        Icons.delete,
                        color: Theme.of(context).colorScheme.error,
                      ),
                      onPressed: () => _removeListItem<I18nText>(
                        ref,
                        blockId,
                        payload.columns!,
                        index,
                        (list) => payload.copyWith(columns: list),
                      ),
                    ),
                    onTap: () async {
                      final result = await showDialog<I18nText>(
                        context: context,
                        builder: (ctx) => RowEditorModal(
                          initialI18nText: item,
                          title: 'Edit Column Item',
                          isMatrixRow: false,
                        ),
                      );
                      if (result != null) {
                        final list = List<I18nText>.from(payload.columns!);
                        list[index] = result;
                        ref
                            .read(promptBlockFormProvider(blockId).notifier)
                            .forceRebuild(payload.copyWith(columns: list));
                      }
                    },
                  ),
                );
              }),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildScalesCard(
    BuildContext context,
    WidgetRef ref,
    AppLocalizations l10n,
    MatrixPromptBlock payload,
    String blockId,
  ) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  l10n.barsScalesTitle,
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Row(
                  children: [
                    OutlinedButton.icon(
                      onPressed: () async {
                        final result = await showDialog<MatrixScale>(
                          context: context,
                          builder: (ctx) => ScaleEditorModal(
                            initialScale: MatrixScale(
                              score: 1,
                              aiLabel: '1',
                              name: const I18nText(
                                defaultLocale: 'en',
                                translations: {'en': ''},
                              ),
                              claims: [
                                MatrixClaim(
                                  label: const I18nText(
                                    defaultLocale: 'en',
                                    translations: {'en': ''},
                                  ),
                                  tdaAssertions: [
                                    TDAAssertion.create(
                                      conceptDescription: 'CRITICAL MANDATE: ',
                                      inverseEvidence: false,
                                      aggregationMode: AggregationMode.exists,
                                    ),
                                  ],
                                ),
                              ],
                            ),
                          ),
                        );
                        if (result != null) {
                          _addListItem<MatrixScale>(
                            ref,
                            blockId,
                            payload.scales,
                            result,
                            (list) => payload.copyWith(scales: list),
                          );
                        }
                      },
                      icon: const Icon(Icons.add),
                      label: Text(l10n.addGradeBtn),
                    ),
                  ],
                ),
              ],
            ),
            AppSpacing.h16,
            BarsMatrixBuilder(
              scales: payload.scales,
              onChanged: (newList) {
                ref
                    .read(promptBlockFormProvider(blockId).notifier)
                    .forceRebuild(payload.copyWith(scales: newList));
              },
            ),
          ],
        ),
      ),
    );
  }

  /// Dispatches the Zero-XML form sections based on the concrete polymorphic PromptBlock variant.
  Widget _buildPolymorphicInstructionSection(
    BuildContext context,
    WidgetRef ref,
    AppLocalizations l10n,
    PromptBlock payload,
    String blockId,
  ) {
    return switch (payload) {
      SystemRulePromptBlock(:final instructionText) => _buildSystemRuleSection(
        context,
        ref,
        l10n,
        payload,
        blockId,
        instructionText,
      ),
      ExecutionPersonaPromptBlock(
        :final roleEnforcement,
        :final toneDirectives,
      ) =>
        _buildPersonaSection(
          context,
          ref,
          l10n,
          payload,
          blockId,
          roleEnforcement,
          toneDirectives,
        ),
      AgentRolePromptBlock(:final roleEnforcement, :final toneDirectives) =>
        _buildPersonaSection(
          context,
          ref,
          l10n,
          payload,
          blockId,
          roleEnforcement,
          toneDirectives,
        ),
      ProtocolPromptBlock(:final protocolInstructions) => _buildProtocolSection(
        context,
        ref,
        l10n,
        payload,
        blockId,
        protocolInstructions,
      ),
      RuntimeVariablesPromptBlock(:final instructionText) =>
        _buildSystemRuleSection(
          context,
          ref,
          l10n,
          payload,
          blockId,
          instructionText,
        ),
      TaskDefinitionPromptBlock(:final instructionText) =>
        _buildSystemRuleSection(
          context,
          ref,
          l10n,
          payload,
          blockId,
          instructionText,
        ),
      MatrixPromptBlock() => _buildMatrixNoticeSection(context, l10n),
    };
  }

  Widget _buildSystemRuleSection(
    BuildContext context,
    WidgetRef ref,
    AppLocalizations l10n,
    PromptBlock payload,
    String blockId,
    String? instructionText,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        TextFormField(
          initialValue: instructionText ?? '',
          decoration: InputDecoration(
            labelText: l10n.instructionTextLabel,
            helperText: l10n.instructionTextHelper,
            border: const OutlineInputBorder(),
          ),
          maxLines: 8,
          onChanged: (val) {
            final updated = switch (payload) {
              SystemRulePromptBlock() => payload.copyWith(instructionText: val),
              RuntimeVariablesPromptBlock() => payload.copyWith(
                instructionText: val,
              ),
              TaskDefinitionPromptBlock() => payload.copyWith(
                instructionText: val,
              ),
              _ => payload,
            };
            ref
                .read(promptBlockFormProvider(blockId).notifier)
                .forceRebuild(updated);
          },
        ),
      ],
    );
  }

  Widget _buildPersonaSection(
    BuildContext context,
    WidgetRef ref,
    AppLocalizations l10n,
    PromptBlock payload,
    String blockId,
    String? roleEnforcement,
    List<String> toneDirectives,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        TextFormField(
          initialValue: roleEnforcement ?? '',
          decoration: InputDecoration(
            labelText: l10n.roleEnforcementLabel,
            helperText: l10n.roleEnforcementHelper,
            border: const OutlineInputBorder(),
          ),
          maxLines: 6,
          onChanged: (val) {
            final updated = switch (payload) {
              ExecutionPersonaPromptBlock() => payload.copyWith(
                roleEnforcement: val,
              ),
              AgentRolePromptBlock() => payload.copyWith(roleEnforcement: val),
              _ => payload,
            };
            ref
                .read(promptBlockFormProvider(blockId).notifier)
                .forceRebuild(updated);
          },
        ),
        AppSpacing.h16,
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      l10n.toneDirectivesTitle,
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    OutlinedButton.icon(
                      onPressed: () {
                        _addListItem<String>(
                          ref,
                          blockId,
                          toneDirectives,
                          '',
                          (newList) => switch (payload) {
                            ExecutionPersonaPromptBlock() => payload.copyWith(
                              toneDirectives: newList,
                            ),
                            AgentRolePromptBlock() => payload.copyWith(
                              toneDirectives: newList,
                            ),
                            _ => payload,
                          },
                        );
                      },
                      icon: const Icon(Icons.add),
                      label: Text(l10n.addToneDirectiveBtn),
                    ),
                  ],
                ),
                if (toneDirectives.isNotEmpty) ...[
                  AppSpacing.h16,
                  ...toneDirectives.asMap().entries.map((entry) {
                    final index = entry.key;
                    final directive = entry.value;

                    return Padding(
                      key: ValueKey(
                        'tone_directive_${entry.key}_${entry.value}',
                      ),
                      padding: const EdgeInsets.only(bottom: 8.0),
                      child: Row(
                        children: [
                          Expanded(
                            child: TextFormField(
                              initialValue: directive,
                              decoration: InputDecoration(
                                labelText: l10n.toneDirectiveItemLabel(
                                  index + 1,
                                ),
                                border: const OutlineInputBorder(),
                                isDense: true,
                              ),
                              onChanged: (val) {
                                final updatedList = List<String>.from(
                                  toneDirectives,
                                );
                                updatedList[index] = val;
                                final updated = switch (payload) {
                                  ExecutionPersonaPromptBlock() =>
                                    payload.copyWith(
                                      toneDirectives: updatedList,
                                    ),
                                  AgentRolePromptBlock() => payload.copyWith(
                                    toneDirectives: updatedList,
                                  ),
                                  _ => payload,
                                };
                                ref
                                    .read(
                                      promptBlockFormProvider(blockId).notifier,
                                    )
                                    .forceRebuild(updated);
                              },
                            ),
                          ),
                          AppSpacing.w8,
                          IconButton(
                            icon: Icon(
                              Icons.delete,
                              color: Theme.of(context).colorScheme.error,
                            ),
                            onPressed: () {
                              _removeListItem<String>(
                                ref,
                                blockId,
                                toneDirectives,
                                index,
                                (newList) => switch (payload) {
                                  ExecutionPersonaPromptBlock() =>
                                    payload.copyWith(toneDirectives: newList),
                                  AgentRolePromptBlock() => payload.copyWith(
                                    toneDirectives: newList,
                                  ),
                                  _ => payload,
                                },
                              );
                            },
                          ),
                        ],
                      ),
                    );
                  }),
                ],
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildProtocolSection(
    BuildContext context,
    WidgetRef ref,
    AppLocalizations l10n,
    PromptBlock payload,
    String blockId,
    String? protocolInstructions,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        TextFormField(
          initialValue: protocolInstructions ?? '',
          decoration: InputDecoration(
            labelText: l10n.protocolInstructionsLabel,
            helperText: l10n.protocolInstructionsHelper,
            border: const OutlineInputBorder(),
          ),
          maxLines: 8,
          onChanged: (val) {
            final updated = switch (payload) {
              ProtocolPromptBlock() => payload.copyWith(
                protocolInstructions: val,
              ),
              _ => payload,
            };
            ref
                .read(promptBlockFormProvider(blockId).notifier)
                .forceRebuild(updated);
          },
        ),
      ],
    );
  }

  Widget _buildMatrixNoticeSection(
    BuildContext context,
    AppLocalizations l10n,
  ) {
    return Card(
      color: Theme.of(context).colorScheme.surfaceContainerHighest,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Row(
          children: [
            Icon(
              Icons.info_outline,
              color: Theme.of(context).colorScheme.primary,
            ),
            AppSpacing.w16,
            Expanded(
              child: Text(
                l10n.matrixPromptNotice,
                style: TextStyle(
                  color: Theme.of(context).colorScheme.onSurfaceVariant,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
